import os
import sqlite3
from datetime import datetime 
import pandas as pd
import random
import openpyxl

from fetch_stock_data import FetchPrices
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