import argparse
import sys
import threading
import tkinter as tk
from tkinter import messagebox

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from stock_price import get_price_history, get_stock_names, get_realtime_price

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

PERIODS = {
    '1M':  60,
    '3M':  130,
    '6M':  260,
    '1Y':  500,
}


def run_cli():
    parser = argparse.ArgumentParser(description="Fetch current stock price for a given symbol.")
    parser.add_argument("symbol", help="Ticker symbol (e.g. AAPL, MSFT)")
    args = parser.parse_args()

    try:
        df, symbol = get_price_history(args.symbol)
        price = float(df['Close'].iloc[-1])
        currency = f"₩{price:,.0f}" if symbol.isdigit() else f"${price:.2f}"
        print(f"Current price for {symbol.upper()}: {currency}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


class AutocompleteEntry(tk.Entry):
    def __init__(self, master, fetch_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.fetch_callback = fetch_callback
        self.stock_names = []
        self._popup = None
        self._listbox = None

        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<Down>', self._focus_listbox)
        self.bind('<Return>', lambda e: fetch_callback())

    def set_names(self, names):
        self.stock_names = names

    def _on_key_release(self, event):
        if event.keysym in ('Return', 'Escape', 'Down', 'Up'):
            return
        text = self.get().strip()
        if len(text) < 1:
            self._hide_popup()
            return
        matches = [n for n in self.stock_names if text in n][:10]
        if matches:
            self._show_popup(matches)
        else:
            self._hide_popup()

    def _show_popup(self, matches):
        self._hide_popup()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()

        self._popup = tk.Toplevel(self)
        self._popup.wm_overrideredirect(True)
        self._popup.geometry(f"+{x}+{y}")

        self._listbox = tk.Listbox(self._popup, height=min(len(matches), 8), width=30)
        self._listbox.pack()
        for m in matches:
            self._listbox.insert(tk.END, m)

        self._listbox.bind('<ButtonRelease-1>', self._on_select)
        self._listbox.bind('<Return>', self._on_select)
        self._listbox.bind('<Escape>', lambda e: self._hide_popup())

    def _focus_listbox(self, event):
        if self._listbox:
            self._listbox.focus_set()
            self._listbox.selection_set(0)

    def _on_select(self, event):
        if self._listbox:
            sel = self._listbox.curselection()
            if sel:
                value = self._listbox.get(sel[0])
                self.delete(0, tk.END)
                self.insert(0, value)
        self._hide_popup()
        self.focus_set()
        self.fetch_callback()

    def _hide_popup(self):
        if self._popup:
            self._popup.destroy()
            self._popup = None
            self._listbox = None


def run_gui():
    root = tk.Tk()
    root.title("Stock Price Checker")
    root.resizable(True, True)

    # 상태
    current_symbol = [None]   # 마지막 검색 심볼 (기간 변경 시 재사용)
    current_period = tk.StringVar(value='1M')
    current_chart_type = tk.StringVar(value='line')  # 'line' or 'candle'
    last_df = [None]
    last_symbol = [None]
    last_currency = [None]
    last_period_label = [None]

    # 상단: 검색창
    top = tk.Frame(root, padx=10, pady=8)
    top.pack(fill='x')

    tk.Label(top, text="종목명 / 심볼:").pack(side='left')
    status_var = tk.StringVar(value="종목 목록 로딩 중...")
    price_var = tk.StringVar(value="")

    def do_fetch(sym, period_label):
        days = PERIODS[period_label]
        try:
            df, symbol = get_price_history(sym, days=days)
            current_symbol[0] = symbol
            price = float(df['Close'].iloc[-1])
            currency = f"₩{price:,.0f}" if symbol.isdigit() else f"${price:.2f}"

            # KRX/NXT 실시간 가격 (한국 주식만)
            nxt_text = ""
            if symbol.isdigit():
                try:
                    rt = get_realtime_price(symbol)
                    sign = '+' if rt['krx_direction'] == 'RISING' else '-' if rt['krx_direction'] == 'FALLING' else ''
                    if rt['market_status'] == 'OPEN':
                        currency = f"₩{rt['krx_price']:,}  {sign}{abs(rt['krx_change']):,} ({sign}{abs(rt['krx_ratio']):.2f}%)  [KRX]"
                    else:
                        currency = f"₩{rt['krx_price']:,}  {sign}{abs(rt['krx_change']):,} ({sign}{abs(rt['krx_ratio']):.2f}%)  [KRX 종가]"
                    if rt['nxt_active']:
                        nxt_sign = '+' if rt['nxt_change'] >= 0 else ''
                        nxt_text = f"NXT  ₩{rt['nxt_price']:,}  {nxt_sign}{rt['nxt_change']:,} ({nxt_sign}{rt['nxt_ratio']:.2f}%)"
                except Exception:
                    pass

            root.after(0, lambda c=currency, n=nxt_text: [
                update_chart(df, symbol, c, period_label, current_chart_type.get()),
                nxt_var.set(n)
            ])
        except Exception as e:
            root.after(0, lambda: [
                price_var.set(""),
                nxt_var.set(""),
                messagebox.showerror("오류", str(e))
            ])

    def fetch():
        sym = entry.get().strip()
        if not sym:
            return
        entry._hide_popup()
        price_var.set("조회 중...")
        period = current_period.get()
        threading.Thread(target=do_fetch, args=(sym, period), daemon=True).start()

    def fetch_period(label):
        current_period.set(label)
        update_period_buttons(label)
        sym = current_symbol[0] or entry.get().strip()
        if not sym:
            return
        price_var.set("조회 중...")
        threading.Thread(target=do_fetch, args=(sym, label), daemon=True).start()

    entry = AutocompleteEntry(top, fetch, width=22)
    entry.pack(side='left', padx=6)
    entry.focus_set()

    tk.Button(top, text="검색", command=fetch).pack(side='left')
    tk.Label(top, textvariable=status_var, fg="gray").pack(side='left', padx=10)

    # 현재가 표시 (KRX + NXT)
    price_frame = tk.Frame(root, padx=12, pady=2)
    price_frame.pack(fill='x')
    tk.Label(price_frame, textvariable=price_var,
             font=("Malgun Gothic", 14, "bold"), anchor='w').pack(side='left')
    nxt_var = tk.StringVar(value="")
    nxt_label = tk.Label(price_frame, textvariable=nxt_var,
                         font=("Malgun Gothic", 10), fg='#8e44ad', anchor='w', padx=10)
    nxt_label.pack(side='left')

    # 기간 + 차트 타입 버튼 행
    period_frame = tk.Frame(root, padx=10, pady=2)
    period_frame.pack(fill='x')

    period_buttons = {}
    for label in PERIODS:
        btn = tk.Button(
            period_frame, text=label, width=5,
            command=lambda l=label: fetch_period(l)
        )
        btn.pack(side='left', padx=2)
        period_buttons[label] = btn

    # 구분선
    tk.Label(period_frame, text='|', fg='gray').pack(side='left', padx=6)

    chart_type_buttons = {}
    for ctype, label in [('line', '라인'), ('candle', '캔들')]:
        btn = tk.Button(
            period_frame, text=label, width=5,
            command=lambda t=ctype: switch_chart_type(t)
        )
        btn.pack(side='left', padx=2)
        chart_type_buttons[ctype] = btn

    def update_period_buttons(active):
        for label, btn in period_buttons.items():
            if label == active:
                btn.config(relief='sunken', bg='#2980b9', fg='white')
            else:
                btn.config(relief='raised', bg='SystemButtonFace', fg='black')

    def update_chart_type_buttons(active):
        for ctype, btn in chart_type_buttons.items():
            if ctype == active:
                btn.config(relief='sunken', bg='#27ae60', fg='white')
            else:
                btn.config(relief='raised', bg='SystemButtonFace', fg='black')

    def switch_chart_type(ctype):
        current_chart_type.set(ctype)
        update_chart_type_buttons(ctype)
        if last_df[0] is not None:
            update_chart(last_df[0], last_symbol[0], last_currency[0],
                         last_period_label[0], ctype)

    update_period_buttons('1M')
    update_chart_type_buttons('line')

    # 차트 영역
    fig = Figure(figsize=(8, 4), dpi=100)
    ax = fig.add_subplot(111)
    ax.text(0.5, 0.5, '종목을 검색하면 차트가 표시됩니다',
            ha='center', va='center', transform=ax.transAxes, color='gray')
    ax.axis('off')
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=(4, 10))

    def update_chart(df, symbol, currency, period_label, chart_type='line'):
        last_df[0] = df
        last_symbol[0] = symbol
        last_currency[0] = currency
        last_period_label[0] = period_label

        price_var.set(f"{symbol}  현재가: {currency}")
        ax.clear()

        closes = df['Close']
        dates = df.index
        fmt_price = plt.FuncFormatter(lambda v, _: f"{v:,.0f}" if symbol.isdigit() else f"${v:,.2f}")

        if chart_type == 'candle' and {'Open', 'High', 'Low', 'Close'}.issubset(df.columns):
            # 캔들 너비: 전체 기간에 비례
            total_days = (dates[-1] - dates[0]).days
            width = max(0.4, total_days / len(dates) * 0.6)
            for date, row in df.iterrows():
                up = row['Close'] >= row['Open']
                body_color = '#e74c3c' if not up else '#2ecc71'
                # 심지 (high-low)
                ax.plot([date, date], [row['Low'], row['High']],
                        color=body_color, linewidth=0.8, zorder=2)
                # 몸통 (open-close)
                bottom = min(row['Open'], row['Close'])
                height = max(abs(row['Close'] - row['Open']), closes.max() * 0.001)
                ax.bar(date, height, bottom=bottom, color=body_color,
                       width=width, alpha=0.9, zorder=3)
        else:
            color = '#e74c3c' if closes.iloc[-1] < closes.iloc[0] else '#2980b9'
            ax.plot(dates, closes, color=color, linewidth=1.8, label='종가', zorder=3)
            ax.fill_between(dates, closes, closes.min(), alpha=0.06, color=color)

        # 이동평균선 (공통)
        for period, ma_color, lw in [(20, '#e67e22', 1.2), (40, '#27ae60', 1.2), (60, '#8e44ad', 1.2)]:
            if len(closes) >= period:
                ma = closes.rolling(window=period).mean()
                ax.plot(dates, ma, color=ma_color, linewidth=lw,
                        linestyle='--', label=f'MA{period}', alpha=0.85)

        # x축 날짜 포맷
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d' if period_label != '1Y' else '%y/%m'))
        locator = mdates.WeekdayLocator(byweekday=0) if period_label in ('1M', '3M') else mdates.MonthLocator()
        ax.xaxis.set_major_locator(locator)
        fig.autofmt_xdate(rotation=30)

        ax.legend(loc='upper left', fontsize=8, framealpha=0.7)
        ax.set_title(f"{symbol}  {period_label}", fontsize=11)
        ax.set_ylabel("가격")
        ax.yaxis.set_major_formatter(fmt_price)
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.tight_layout()
        canvas.draw()

    def load_names():
        names = get_stock_names()
        if names:
            entry.set_names(names)
            root.after(0, lambda: status_var.set(f"종목 {len(names):,}개 로드 완료"))
        else:
            root.after(0, lambda: status_var.set("종목 목록 로드 실패 (직접 입력 가능)"))

    threading.Thread(target=load_names, daemon=True).start()
    root.mainloop()


def main():
    if len(sys.argv) > 1:
        run_cli()
    else:
        run_gui()


if __name__ == "__main__":
    main()
