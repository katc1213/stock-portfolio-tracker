import os
import sqlite3
from sqlite3 import Error

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
            self.conn.commit()
            self.conn.close()
            
            print(f"Database created at: {os.path.abspath(db_file)}")
        except Error as e:
            print(f"Error initializing database: {e}")
            
if __name__ == "__main__":
    db = DatabaseManager()