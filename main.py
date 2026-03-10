import argparse
import sys
import threading
import tkinter as tk
from tkinter import messagebox

from stock_price import get_stock_price, get_stock_names


def run_cli():
    parser = argparse.ArgumentParser(description="Fetch current stock price for a given symbol.")
    parser.add_argument("symbol", help="Ticker symbol (e.g. AAPL, MSFT)")
    args = parser.parse_args()

    try:
        price, symbol = get_stock_price(args.symbol)
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

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack()

    tk.Label(frame, text="종목명 / 심볼:").grid(row=0, column=0, sticky="w")

    def fetch():
        sym = entry.get().strip()
        if not sym:
            return
        entry._hide_popup()
        try:
            price, symbol = get_stock_price(sym)
            currency = f"₩{price:,.0f}" if symbol.isdigit() else f"${price:.2f}"
            messagebox.showinfo("가격", f"{symbol.upper()}: {currency}")
        except Exception as e:
            messagebox.showerror("오류", str(e))

    entry = AutocompleteEntry(frame, fetch, width=25)
    entry.grid(row=0, column=1, padx=5)
    entry.focus_set()

    status_var = tk.StringVar(value="종목 목록 로딩 중...")
    tk.Label(frame, textvariable=status_var, fg="gray").grid(row=2, column=0, columnspan=2)

    tk.Button(frame, text="검색", command=fetch).grid(row=1, column=0, columnspan=2, pady=5)

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
