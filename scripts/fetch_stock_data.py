import os
import sqlite3
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class FetchPrices:
    def __init__(self, db_path="../../stock-portfolio-tracker/data/sim_database.db", num_tickers=10):
        self.db_path = os.path.abspath(db_path)
        self.num_tickers = num_tickers
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_live_tickers(self):
        """Get live most-active tickers from Yahoo Finance screener API."""
        url = (
            "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"
            f"?scrIds=most_actives&count={self.num_tickers}"
        )
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            )
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            quotes = (
                response.json()
                .get("finance", {})
                .get("result", [{}])[0]
                .get("quotes", [])
            )
            tickers = [q["symbol"] for q in quotes if "symbol" in q]
            print(f"Pulled {len(tickers)} tickers from Yahoo Finance")
            return tickers[:self.num_tickers]
        except Exception as e:
            print(f"Failed to fetch tickers: {e}")
            return []

    def fetch_intraday_prices(self, tickers):
        """Download 1-minute intraday close prices for today."""
        frames = []
        for tkr in tickers:
            try:
                print(f"Fetching {tkr} intraday data...")
                df = yf.download(tkr, period="1d", interval="1m")[['Close']].copy()
                df.reset_index(inplace=True)

                # Ensure date column is in correct format
                df.rename(columns={'Datetime': 'date', 'Close': 'close'}, inplace=True)
                df['date'] = pd.to_datetime(df['date']).dt.strftime("%Y-%m-%d %H:%M:%S")
                df['ticker'] = tkr
                df = df[['date', 'ticker', 'close']]

                # Flatten column names
                df.columns = [col if isinstance(col, str) else col[0] for col in df.columns]

                frames.append(df)

            except Exception as e:
                print(f"Error: Failed to fetch {tkr}: {e}")
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def insert_into_database(self, df):
        """Insert DataFrame into SQLite 'stock_prices' table."""
        if df.empty:
            print("Error: No data to insert into database.")
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                df.to_sql("stock_prices", conn, if_exists="append", index=False)
            print(f"Inserted {len(df)} rows into 'stock_prices'")
        except Exception as e:
            print(f"DB insert error: {e}")
    
    # delete data from previous days to get data from past week only
    def delete_from_database(self, df):
        with sqlite3.connect(self.db_path) as conn:
            # datetimeobj to str
            week_dates = (datetime.now() - timedelta(days=7)).isoformat()
            conn.cursor().execute("""
                                DELETE FROM stock_prices
                                WHERE date < ?
                                """,(week_dates,))
        conn.commit()
        conn.close()
        print(f"Old records deleted from trades from more than week ago")
            
        

    def run(self):
        """Run full fetch + insert process."""
        tickers = self.get_live_tickers()
        if tickers:
            df = self.fetch_intraday_prices(tickers)
            self.insert_into_database(df)
            self.delete_from_database(df)
            
            # Load data into stock_data.csv
            csv_path = os.path.abspath("../../stock-portfolio-tracker/data/stock_data.csv")
            df.to_csv(csv_path, index=False)
            
# ─── Entry Point ─────────────────────────────────────
if __name__ == "__main__":
    fetcher = FetchPrices()
    fetcher.run()
