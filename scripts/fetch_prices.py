import yfinance as yf
import sqlite3
import pandas as pd

# dynamically pull top 20 most active tickers through webscraping
def get_top_tickers(url):
    tables = pd.read_html(url)
    df = tables[0]
    tickers = df['Symbol'].tolist()
    return tickers[:20]  

url = "https://finance.yahoo.com/most-active"
tickers = get_top_tickers(url)

conn = sqlite3.connect("../../data/sim_database.db")
data = []

for ticker in tickers:
    print(f"Fetching {ticker}...")
    try:
        df = yf.download(ticker, start=start, end=end)[['Close']].reset_index()
        df['ticker'] = ticker
        df.rename(columns={'Date': 'date', 'Close': 'close'}, inplace=True)
        all_data.append(df)
    except Exception as e:
        print(f"Failed to fetch {ticker}: {e}")

# Combine and insert into SQLite
if all_data:
    final_df = pd.concat(all_data)
    final_df.to_sql("stock_prices", conn, if_exists="append", index=False)
    print(f"Inserted {len(final_df)} rows into stock_prices")
else:
    print("No data downloaded.")

conn.close()