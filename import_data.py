import pandas as pd
import sqlite3
from datetime import datetime

# Load the expanded dataset
data = pd.read_csv('expanded_stock_data.csv')

# Sample 2700 data points
data_sample = data.sample(n=2700, random_state=42).reset_index(drop=True)

# Connect to database
conn = sqlite3.connect('stock_data.db')
c = conn.cursor()

# Clear existing data
c.execute('DELETE FROM stock_history')

# Insert data into stock_history table
for index, row in data_sample.iterrows():
    corporate_name = row['Symbol']
    data_time = row['Date']
    price = row['Close']
    c.execute('INSERT INTO stock_history (corporate_name, data_time, price) VALUES (?, ?, ?)',
              (corporate_name, data_time, price))

conn.commit()
conn.close()

print(f"✅ Imported 2700 sampled data points into the database")