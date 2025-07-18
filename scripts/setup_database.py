import os
import sqlite3
from sqlite3 import Error
import yfinance as yf
import pandas as pd

class DatabaseManager:
    """ Class to manage database and add tables """
    def __init__(self, config=None, db_file:str="../../stock-portfolio-tracker/data/sim_database.db"):
        """ Create database object and establish connection to file """
        try:
            os.makedirs(os.path.dirname(db_file), exist_ok=True)
            self.conn = sqlite3.connect(db_file)
            self.cursor = self.conn.cursor()
            # Create trade table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                ticker TEXT,
                action TEXT,
                quantity INTEGER,
                price REAL
            )
            """)
            
            # Create stock_prices table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                ticker TEXT,
                close REAL
            )
            """)
            
            # Get sector info
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sectors (
                ticker TEXT PRIMARY KEY,
                sector TEXT,
                industry TEXT
                );
                """)
            # # URL for Yahoo Finance "Most Active" stocks
            # url = "https://finance.yahoo.com/most-active"

            # # Read the HTML tables on the page
            # tables = pd.read_html(url)

            # # The first table contains the data
            # most_active_df = tables[0]

            # # Extract the ticker symbols
            # tickers = most_active_df["Symbol"].tolist()
            # # most_active_df = yf.get_day_most_active()
            # # tickers = most_active_df['Symbol'].tolist()
            # for symbol in tickers:
            #     try: 
            #         info = yf.Ticker(symbol).info
            #         sector = info.get("sector", "N/A")
            #         industry = info.get("industry", "N/A")
            #         self.cursor.execute("INSERT OR REPLACE INTO sectors(tickers, sector, industry) VALUES (?, ?, ?)"
            #                             (symbol, sector, industry))
            #     except Exception as e:
            #         print(f"Falied for {symbol}: {e}")
                    
            self.conn.commit()
            self.conn.close()
            
            print(f"Database created at: {os.path.abspath(db_file)}")
        except Error as e:
            print(f"Error initializing database: {e}")
            
if __name__ == "__main__":
    db = DatabaseManager()