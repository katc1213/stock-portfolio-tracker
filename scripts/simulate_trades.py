import os
import sqlite3
from datetime import datetime 
import pandas as pd
import random

# connect to database
def __init__(self, db_path="../../stock-portfolio-tracker/data/sim_database.db"):
        self.db_path = os.path.abspath(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()