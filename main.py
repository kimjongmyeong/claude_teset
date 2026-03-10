import argparse
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog

from stock_price import get_stock_price, register_name




def run_cli():
    parser = argparse.ArgumentParser(description="Fetch current stock price for a given symbol.")
    parser.add_argument("symbol", help="Ticker symbol (e.g. AAPL, MSFT)")
    args = parser.parse_args()

    try:
        price, symbol = get_stock_price(args.symbol)
        currency = f"₩{price:,.0f}" if symbol.isdigit() else f"${price:.2f}"
        print(f"Current price for {symbol.upper()}: {currency}")
    except LookupError:
        code = input(f"'{args.symbol}'을(를) 찾을 수 없습니다. 종목 코드를 입력하세요 (예: 138040): ").strip()
        if code:
            register_name(args.symbol, code)
            price, symbol = get_stock_price(args.symbol)
            currency = f"₩{price:,.0f}" if symbol.isdigit() else f"${price:.2f}"
            print(f"Current price for {symbol.upper()}: {currency}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def run_gui():
    # create a simple window to input symbol and display price
    root = tk.Tk()
    root.title("Stock Price Checker")

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack()

    tk.Label(frame, text="Ticker symbol:").grid(row=0, column=0, sticky="w")
    symbol_entry = tk.Entry(frame)
    symbol_entry.grid(row=0, column=1)

    def fetch():
        sym = symbol_entry.get().strip()
        try:
            price, symbol = get_stock_price(sym)
            currency = f"₩{price:,.0f}" if symbol.isdigit() else f"${price:.2f}"
            messagebox.showinfo("Price", f"Current price for {symbol.upper()}: {currency}")
        except LookupError:
            code = simpledialog.askstring(
                "종목 코드 등록",
                f"'{sym}'을(를) 찾을 수 없습니다.\n종목 코드를 입력하면 저장 후 조회합니다.\n(예: 138040)",
                parent=root
            )
            if code and code.strip():
                register_name(sym, code.strip())
                fetch()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(frame, text="Get Price", command=fetch).grid(row=1, column=0, columnspan=2, pady=5)

    root.mainloop()


def main():
    if len(sys.argv) > 1:
        run_cli()
    else:
        run_gui()


if __name__ == "__main__":
    main()
