import yfinance as yf
from datetime import datetime

START_DATE = "1995-01-01"
END_DATE = "2025-01-01"

def download_series(symbol, out_csv, price_col_name="USD_Price"):
    """
    從 Yahoo Finance 下載資料，取收盤價 Close，
    只輸出 Date + 價格，一共兩欄。
    """
    df = yf.download(symbol, start=START_DATE, end=END_DATE, progress=False)

    # 只保留收盤價
    df = df[["Close"]].reset_index()

    # 重新命名欄位
    df.columns = ["Date", price_col_name]

    # 存成 CSV（不存 index）
    df.to_csv(out_csv, index=False)
    print(f"Saved: {out_csv}")


# 1️⃣ 美國 10 年期公債
download_series("IEF", "us10y_price_30y.csv", price_col_name="USD_Price")



# 2️⃣ 黃金期貨 GC=F（以美元計價）
download_series("GC=F", "gold_gc_f_30y.csv", price_col_name="USD_Price")


# 3️⃣ 瑞士法郎對美元 CHFUSD=X（1 瑞郎值多少美元）
download_series("CHFUSD=X", "chf_usd_30y.csv", price_col_name="USD_Price")


# 4️⃣ 比特幣對美元 BTC-USD
# 比特幣實際數據大概從 2014 之後才有，前面的日期會是空的沒關係
download_series("BTC-USD", "btc_usd_30y.csv", price_col_name="USD_Price")
