import yfinance as yf

# 設定下載區間
START_DATE = "1995-01-01"
END_DATE = "2025-01-01"   # 或改成你想要的日期，如 "2025-12-31"

def download_sp500():
    symbol = "^GSPC"   # S&P500 指數代碼（Yahoo Finance）
    out_csv = "sp500_30y.csv"

    df = yf.download(symbol, start=START_DATE, end=END_DATE, progress=False)

    # 只取收盤價
    df = df[["Close"]].reset_index()

    # 改名為符合你要的格式
    df.columns = ["Date", "USD_Price"]

    # 輸出 CSV
    df.to_csv(out_csv, index=False)
    print(f"Saved: {out_csv}")

download_sp500()

