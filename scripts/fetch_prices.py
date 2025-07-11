# dynamically pull top 20 most active tickers through webscraping
# def get_top_tickers(url):
#     tables = pd.read_html(url)
#     df = tables[0]
#     tickers = df['Symbol'].tolist()
#     return tickers[:20]  

# url = "https://finance.yahoo.com/most-active"
# tickers = get_top_tickers(url)

# conn = sqlite3.connect("../../data/sim_database.db")
# data = []

# for ticker in tickers:
#     print(f"Fetching {ticker}...")
#     try:
#         df = yf.download(ticker, start=start, end=end)[['Close']].reset_index()
#         df['ticker'] = ticker
#         df.rename(columns={'Date': 'date', 'Close': 'close'}, inplace=True)
#         all_data.append(df)
#     except Exception as e:
#         print(f"Failed to fetch {ticker}: {e}")

# # Combine and insert into SQLite
# if all_data:
#     final_df = pd.concat(all_data)
#     final_df.to_sql("stock_prices", conn, if_exists="append", index=False)
#     print(f"Inserted {len(final_df)} rows into stock_prices")
# else:
#     print("No data downloaded.")

# conn.close()

import os
import sqlite3
import requests
import yfinance as yf
import pandas as pd

##### CONFIG #####
DATABASE_PATH = "../../stock-portfolio-tracker/data/sim_database.db" 
NUM_TICKERS   = 10                             # top ten active


def get_live_tickers(limit=10):
    """Pull live tickers from Yahoo Finance Screener JSON API."""
    url = (
        "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"
        f"?scrIds=most_actives&count={limit}"
    )
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        quotes = (
            r.json()
            .get("finance", {})
            .get("result", [{}])[0]
            .get("quotes", [])
        )
        tickers = [q["symbol"] for q in quotes if "symbol" in q]
        print(f"✅ Pulled {len(tickers)} tickers")
        return tickers[:limit]
    except Exception as e:
        print(f"❌ Couldn’t fetch tickers: {e}")
        return []

def fetch_intraday_prices(tickers):
    frames = []
    for tkr in tickers:
        try:
            print(f"📡 Fetching {tkr} …")
            df = yf.download(tkr, period="1d", interval="1m")

            # Clean and structure DataFrame
            df = df[['Close']].copy()
            df.reset_index(inplace=True)

            # Rename & reorder columns to match SQLite table
            df.rename(columns={'Datetime': 'date', 'Close': 'close'}, inplace=True)
            df['ticker'] = tkr
            df = df[['date', 'ticker', 'close']]  #TODO: ensure correct order

            frames.append(df)

        except Exception as e:
            print(f"⚠️  {tkr} failed: {e}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def insert_into_db(df, db_path):
    if df.empty:
        print("⚠️  No new price rows to insert.")
        return
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        with sqlite3.connect(db_path) as conn:
            df.to_sql("stock_prices", conn, if_exists="append", index=False)
        print(f"✅ Inserted {len(df)} rows into stock_prices")
    except Exception as e:
        print(f"❌ DB insert error: {e}")

##### MAIN #####
if __name__ == "__main__":
    symbols = get_live_tickers(NUM_TICKERS)
    if symbols:
        prices = fetch_intraday_prices(symbols)
        insert_into_db(prices, DATABASE_PATH)
