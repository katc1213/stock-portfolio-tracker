# | Field               | Description                            |
# | ------------------- | -------------------------------------- |
# | `ticker`            | Stock symbol (e.g., TSLA)              |
# | `quantity`          | Shares currently held                  |
# | `avg_cost`          | Average purchase price per share       |
# | `latest_prices`     | Latest market price per share          |
# | `market_value`      | `quantity * latest_prices`             |
# | `total_cost`        | `quantity * avg_cost`                  |
# |                     | (money spent on shares)                |

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import csv
from datetime import datetime

class StockPortfolio:
    def __init__(self, db_path="../../stock-portfolio-tracker/data/sim_database.db"):
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()

    def get_trades(self):
        return pd.read_sql_query("SELECT * FROM trades ORDER BY date ASC", self.conn)

    def get_stock_data(self):
        return pd.read_sql_query("SELECT * FROM stock_prices ORDER BY date ASC", self.conn)
    
    # for completed trades => realized_pnl = (sell price - avg cost) * quantity sold
    def compute_real_pnl(self) -> dict:
        trades_df = self.get_trades()
        trades_df["date"] = pd.to_datetime(trades_df["date"])
        trades_df = trades_df.sort_values("date")

        positions = {}
        daily_pnl = {}

        for _, row in trades_df.iterrows():
            ticker = row['ticker']
            quantity = row['quantity']
            price = row["price"]
            date = row["date"]

            if ticker not in positions:
                positions[ticker] = {
                    'quantity': 0,
                    'total_cost': 0.0,
                    'real_pnl': 0.0
                }

            if ticker not in daily_pnl:
                daily_pnl[ticker] = []

            if row['action'].lower() == 'buy':
                positions[ticker]['total_cost'] += quantity * price
                positions[ticker]['quantity'] += quantity
                daily_pnl[ticker].append((date, positions[ticker]['real_pnl']))

            elif row['action'].lower() == 'sell':
                sold_quantity = quantity
                prev_quantity = positions[ticker]["quantity"] + quantity  # assume quantity is positive for both buy/sell

                avg_cost = positions[ticker]['total_cost'] / max(prev_quantity, 1)
                new_real_pnl = (price - avg_cost) * sold_quantity

                positions[ticker]['total_cost'] -= avg_cost * sold_quantity
                positions[ticker]['quantity'] -= sold_quantity
                positions[ticker]['real_pnl'] += new_real_pnl

                daily_pnl[ticker].append((date, positions[ticker]['real_pnl']))

        # Plot cumulative realized PnL by ticker
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates

        plt.figure(figsize=(12, 6))

        for ticker, entries in daily_pnl.items():
            if not entries:
                continue
            # Sort by date
            entries = sorted(entries, key=lambda x: x[0])
            dates, pnls = zip(*entries)
            cumulative_pnls = [sum(pnls[:i + 1]) for i in range(len(pnls))]

            plt.plot(dates, cumulative_pnls, marker='o', label=ticker)

        plt.title("Cumulative Realized PnL by Ticker Over Time")
        plt.xlabel("Date")
        plt.ylabel("Realized PnL ($)")
        plt.legend(title="Ticker")
        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        return positions

    
    # unreal_pnl = (live market price - avg cost) * quantity
    def compute_unreal_pnl(self) -> dict:
        trades_df = self.get_trades()
        stock_data_df = self.get_stock_data()
        
        positions = {}
        
        latest_prices = (
            stock_data_df.sort_values(by="date")
            .groupby("ticker")
            .last()["close"]
            .to_dict
        )
        
        for _, row in trades_df.iterrows():
            ticker = row['ticker'] #upper()
            quantity = row['quantity']
            price = row["price"]
            if ticker not in positions:
                positions[ticker] = {
                    'quantity': 0,
                    'total_cost': 0.0,
                    'unreal_pnl': 0.0
                }
            
            if row['action'] == 'buy':
                positions[ticker]['total_cost'] += quantity * price
                positions[ticker]['quantity'] += quantity
            elif row['action'] == 'sell':
                #  ensures the denominator is at least 1, avoiding the division error.
                avg_cost = positions[ticker]["total_cost"] / max(positions[ticker]["quantity"] + quantity, 1)
                positions[ticker]['total_cost'] -= quantity * avg_cost
                positions[ticker]['quantity'] -= quantity
                
        unreal_pnl = {}
        for ticker, data in positions.items():
            quantity = data["quantity"]
            if quantity == 0 or ticker not in latest_prices:
                continue

            avg_cost = data["total_cost"] / quantity
            market_price = latest_prices[ticker]
            unrealized = (market_price - avg_cost) * quantity
            unreal_pnl[ticker] = round(unrealized, 2)
        return unreal_pnl
    
    def dict_to_csv(self, my_dict):
        with open('../../stock-portfolio-tracker/data/pnl_data.csv','w') as f:
            w = csv.writer(f)
            w.writerows(my_dict.items())
    
    def run(self):
        pnl = self.compute_real_pnl()
        self.dict_to_csv(pnl)
        # print(self.compute_unreal_pnl())
        
if __name__ == "__main__":
    portfolio = StockPortfolio()
    portfolio.run()
    
    
    # if action == "SELL":
    # if ticker not in positions or positions[ticker]["quantity"] < quantity:
    #     raise ValueError(f"Cannot sell {quantity} shares of {ticker}; only {positions.get(ticker, {}).get('quantity', 0)} available.")

    # avg_cost_per_share = positions[ticker]["total_cost"] / positions[ticker]["quantity"]
    # realized_pnl += quantity * (price - avg_cost_per_share)

    # positions[ticker]["quantity"] -= quantity
    # positions[ticker]["total_cost"] -= quantity * avg_cost_per_share

    # # Clean up if position is closed
    # if positions[ticker]["quantity"] == 0:
    #     del positions[ticker]
