import os
import sqlite3
from datetime import datetime 
import pandas as pd
import random
import openpyxl

from fetch_stock_data import FetchPrices

class TradeSim:
    # connect to database
    def __init__(self, db_path="../../stock-portfolio-tracker/data/sim_database.db"):
            self.db_path = os.path.abspath(db_path)
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

    def get_latest_price(self, ticker):
        # return cursor object
        self.cursor.execute("""
                            SELECT close FROM stock_prices
                            WHERE ticker = ?
                            ORDER BY date DESC
                            LIMIT 1
                            """,(ticker,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    # when simulate_trade() is called, row insert:
    # date                 ticker   action  quantity   price
    # 2025-07-11 13:33:00	AAPL	buy	     20	       190.12
    def simulate_trade(self, ticker, action, quantity):
        price = self.get_latest_price(ticker)
        if price is None:
            print(f"No price available for {ticker}. Can not simulate.")
            return
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # format datetime into string format
        self.cursor.execute("""
                            INSERT INTO trades (date, ticker, action, quantity, price)
                            VALUES (?, ?, ?, ?, ?)
                            """, (date, ticker, action, quantity, price))
        self.conn.commit() #confirm the changes made by the user to the database
        print(f"{action.title()} {quantity} shares of {ticker} at ${price:.2f} per share.")
        
    def simulate_random_trades(self, tickers, num_trades=5):
            actions = ['buy', 'sell']
            for _ in range(num_trades):
                ticker = random.choice(tickers)
                action = random.choice(actions)
                quantity = random.randint(1, 100)
                self.simulate_trade(ticker, action, quantity)

    def close(self):
        self.conn.close()
        
if __name__ == "__main__":
    sim = TradeSim() 
    
    # tickers =  ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN"]
    
    fetcher = FetchPrices()
    tickers = fetcher.get_live_tickers()

    sim.simulate_random_trades(tickers, num_trades=10)
    sim.close()
    
    con = sqlite3.connect('/Users/Kat/Documents/repos/stock-portfolio-tracker/data/sim_database.db')
    df_trades = pd.read_sql("SELECT * FROM trades;", con)

    # Export the DataFrame to an Excel file
    df_trades.to_excel('/Users/Kat/Documents/repos/stock-portfolio-tracker/outputs/trades_export.xlsx', sheet_name='Trades Data', index=False)