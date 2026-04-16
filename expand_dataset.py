import yfinance as yf
import pandas as pd
from datetime import datetime

# List of stocks to fetch data for
stocks = ['TCS.NS', 'INFY.NS', 'RELIANCE.NS', 'ICICIBANK.NS']

# Period to fetch
period = '5y'

# List to hold dataframes
all_data = []

for stock in stocks:
    print(f"Fetching data for {stock}...")
    try:
        data = yf.download(stock, period=period, progress=False)
        data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
        # Flatten columns
        data.columns = data.columns.droplevel(1)  # Remove ticker level
        data['Symbol'] = stock
        data.reset_index(inplace=True)
        all_data.append(data)
        print(f"✅ Fetched {len(data)} rows for {stock}")
    except Exception as e:
        print(f"❌ Error fetching {stock}: {e}")

# Combine all data
combined_data = pd.concat(all_data, ignore_index=True)

print("Columns:", combined_data.columns)
print("Shape:", combined_data.shape)
print(combined_data.head())

# Sort by date
combined_data.sort_values('Date', inplace=True)

# Reset index
combined_data.reset_index(drop=True, inplace=True)

# Save to csv
combined_data.to_csv('expanded_stock_data.csv', index=False)

print(f"✅ Combined dataset saved with {len(combined_data)} rows")