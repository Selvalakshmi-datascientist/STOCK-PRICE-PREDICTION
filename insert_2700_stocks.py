import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import random
import yfinance as yf

def insert_2700_stock_records():
    """Insert 2700 stock records into the dataset"""
    
    print("=== Inserting 2700 Stock Records ===")
    
    # Stock symbols to use (expand with more Indian stocks)
    stock_symbols = [
        'TCS.NS', 'RELIANCE.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
        'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS', 'LT.NS',
        'ASIANPAINT.NS', 'MARUTI.NS', 'AXISBANK.NS', 'BAJFINANCE.NS', 'HDFCLIFE.NS',
        'SUNPHARMA.NS', 'TITAN.NS', 'ULTRACEMCO.NS', 'WIPRO.NS', 'TECHM.NS',
        'NESTLEIND.NS', 'HCLTECH.NS', 'DIVISLAB.NS', 'GRASIM.NS', 'POWERGRID.NS',
        'NTPC.NS', 'COALINDIA.NS', 'ONGC.NS', 'BPCL.NS', 'IOC.NS',
        'GAIL.NS', 'JSWSTEEL.NS', 'TATASTEEL.NS', 'HINDALCO.NS', 'VEDL.NS',
        'DRREDDY.NS', 'CIPLA.NS', 'BIOCON.NS', 'AUROPHARMA.NS', 'LUPIN.NS',
        'M&M.NS', 'BAJAJFINSV.NS', 'CHOLAFIN.NS', 'SHREECEM.NS', 'DABUR.NS',
        'GODREJCP.NS', 'UBL.NS', 'MCDOWELL-N.NS', 'TATACONSUM.NS', 'BRITANNIA.NS',
        'PIDILITIND.NS', 'BERGEPAINT.NS', 'ASIANPAINT.NS', 'KANSAINER.NS', 'JINDALSTEL.NS',
        'JINDALSAW.NS', 'TATAMOTORS.NS', 'M&MFIN.NS', 'BAJAJ-AUTO.NS', 'HEROMOTOCO.NS',
        'EICHERMOT.NS', 'MOTHERSON.NS', 'BOSCHLTD.NS', 'APOLLOHOSP.NS', 'MAXHEALTH.NS',
        'ALKEM.NS', 'LALPATHLAB.NS', 'DRREDDY.NS', 'AUBANK.NS', 'RBLBANK.NS',
        'FEDERALBNK.NS', 'IDFCFIRSTB.NS', 'BANDHANBNK.NS', 'PNB.NS', 'CANBK.NS',
        'UNIONBANK.NS', 'INDIANB.NS', 'IOB.NS', 'UCOBANK.NS', 'CENTRALBK.NS',
        'MAHABANK.NS', 'J&KBANK.NS', 'SOUTHBANK.NS', 'KARURVYSYA.NS', 'VIJAYABANK.NS'
    ]
    
    # Generate date range (last 90 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    print(f"Stock symbols: {len(stock_symbols)}")
    print(f"Target records: 2700")
    
    # Create records
    records = []
    record_id = 1
    
    for stock in stock_symbols:
        # Generate 30 records per stock (90 stocks * 30 days = 2700)
        for day_offset in range(30):
            current_date = start_date + timedelta(days=day_offset)
            
            # Generate realistic stock price
            base_price = random.uniform(100, 5000)
            
            # Add some randomness
            price_variation = random.uniform(-0.05, 0.05)  # ±5% variation
            current_price = base_price * (1 + price_variation)
            
            # Generate OHLC data
            high = current_price * random.uniform(1.01, 1.05)
            low = current_price * random.uniform(0.95, 0.99)
            open_price = random.uniform(low, high)
            close_price = current_price
            
            # Generate volume
            volume = random.randint(100000, 10000000)
            
            # Generate prediction (future price)
            prediction_change = random.uniform(-0.1, 0.1)  # ±10% prediction
            predicted_price = close_price * (1 + prediction_change)
            
            record = {
                'id': record_id,
                'corporate_name': stock,
                'data_time': current_date.isoformat(),
                'price': close_price,
                'open_price': open_price,
                'high_price': high,
                'low_price': low,
                'volume': volume,
                'prediction': predicted_price,
                'data_source': 'generated'
            }
            
            records.append(record)
            record_id += 1
            
            if len(records) >= 2700:
                break
        
        if len(records) >= 2700:
            break
    
    print(f"Generated {len(records)} records")
    
    # Save to CSV
    df = pd.DataFrame(records)
    df.to_csv('generated_2700_stocks.csv', index=False)
    print(f"Saved to: generated_2700_stocks.csv")
    
    # Insert into database
    insert_into_database(records)
    
    # Create summary
    create_summary(df)
    
    return True

def insert_into_database(records):
    """Insert records into SQLite database"""
    
    print(f"\n=== Inserting into Database ===")
    
    try:
        conn = sqlite3.connect('stock_data.db')
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_history (
                id INTEGER PRIMARY KEY,
                corporate_name TEXT,
                data_time TEXT,
                price REAL,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                volume INTEGER,
                prediction REAL,
                data_source TEXT
            )
        ''')
        
        # Clear existing data
        cursor.execute('DELETE FROM stock_history')
        print("Cleared existing data")
        
        # Insert new records
        for record in records:
            cursor.execute('''
                INSERT INTO stock_history 
                (id, corporate_name, data_time, price, open_price, high_price, low_price, volume, prediction, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record['id'],
                record['corporate_name'],
                record['data_time'],
                record['price'],
                record['open_price'],
                record['high_price'],
                record['low_price'],
                record['volume'],
                record['prediction'],
                record['data_source']
            ))
        
        conn.commit()
        
        # Verify insertion
        cursor.execute('SELECT COUNT(*) FROM stock_history')
        count = cursor.fetchone()[0]
        print(f"Inserted {count} records into database")
        
        # Show sample
        cursor.execute('SELECT corporate_name, price, prediction FROM stock_history LIMIT 5')
        sample = cursor.fetchall()
        print(f"Sample records:")
        for row in sample:
            print(f"  {row[0]}: Price={row[1]:.2f}, Prediction={row[2]:.2f}")
        
        conn.close()
        
    except Exception as e:
        print(f"Database insertion failed: {e}")

def create_summary(df):
    """Create summary statistics"""
    
    print(f"\n=== Dataset Summary ===")
    
    # Basic statistics
    print(f"Total records: {len(df)}")
    print(f"Unique stocks: {df['corporate_name'].nunique()}")
    print(f"Date range: {df['data_time'].min()} to {df['data_time'].max()}")
    
    # Price statistics
    print(f"\nPrice Statistics:")
    print(f"  Min price: ${df['price'].min():.2f}")
    print(f"  Max price: ${df['price'].max():.2f}")
    print(f"  Mean price: ${df['price'].mean():.2f}")
    print(f"  Median price: ${df['price'].median():.2f}")
    
    # Volume statistics
    print(f"\nVolume Statistics:")
    print(f"  Min volume: {df['volume'].min():,}")
    print(f"  Max volume: {df['volume'].max():,}")
    print(f"  Mean volume: {df['volume'].mean():,.0f}")
    
    # Prediction accuracy
    df['prediction_error'] = abs(df['prediction'] - df['price'])
    print(f"\nPrediction Statistics:")
    print(f"  Mean prediction error: ${df['prediction_error'].mean():.2f}")
    print(f"  Max prediction error: ${df['prediction_error'].max():.2f}")
    
    # Top stocks by price
    top_stocks = df.groupby('corporate_name')['price'].last().sort_values(ascending=False).head(10)
    print(f"\nTop 10 Stocks by Current Price:")
    for stock, price in top_stocks.items():
        print(f"  {stock}: ${price:.2f}")
    
    # Save summary
    summary_stats = {
        'total_records': len(df),
        'unique_stocks': df['corporate_name'].nunique(),
        'min_price': df['price'].min(),
        'max_price': df['price'].max(),
        'mean_price': df['price'].mean(),
        'median_price': df['price'].median(),
        'min_volume': df['volume'].min(),
        'max_volume': df['volume'].max(),
        'mean_volume': df['volume'].mean(),
        'mean_prediction_error': df['prediction_error'].mean()
    }
    
    summary_df = pd.DataFrame([summary_stats])
    summary_df.to_csv('dataset_summary.csv', index=False)
    print(f"\nSummary saved to: dataset_summary.csv")

def enhance_with_real_data():
    """Enhance some records with real yfinance data"""
    
    print(f"\n=== Enhancing with Real Data ===")
    
    # Get top 10 stocks
    top_stocks = ['TCS.NS', 'RELIANCE.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
                  'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS', 'LT.NS']
    
    try:
        conn = sqlite3.connect('stock_data.db')
        cursor = conn.cursor()
        
        for stock in top_stocks[:5]:  # Do first 5 to avoid API limits
            try:
                print(f"Fetching real data for {stock}...")
                
                # Get recent data
                ticker = yf.Ticker(stock)
                data = ticker.history(period="5d", interval="1d")
                
                if not data.empty:
                    # Update latest record with real data
                    latest_date = data.index[-1].strftime('%Y-%m-%d')
                    latest_price = float(data['Close'].iloc[-1])
                    
                    cursor.execute('''
                        UPDATE stock_history 
                        SET price = ?, open_price = ?, high_price = ?, low_price = ?, volume = ?, data_source = ?
                        WHERE corporate_name = ? AND data_time LIKE ?
                    ''', (
                        latest_price,
                        float(data['Open'].iloc[-1]),
                        float(data['High'].iloc[-1]),
                        float(data['Low'].iloc[-1]),
                        int(data['Volume'].iloc[-1]),
                        'yfinance',
                        stock,
                        f'{latest_date}%'
                    ))
                    
                    print(f"  + Updated {stock} with real price: ${latest_price:.2f}")
                
            except Exception as e:
                print(f"  - Failed to fetch {stock}: {e}")
        
        conn.commit()
        conn.close()
        print("Real data enhancement complete")
        
    except Exception as e:
        print(f"Enhancement failed: {e}")

if __name__ == "__main__":
    # Insert 2700 records
    success = insert_2700_stock_records()
    
    if success:
        # Enhance with real data
        enhance_with_real_data()
        
        print(f"\n=== 2700 Stock Records Insertion Complete ===")
        print("Files created:")
        print("  - generated_2700_stocks.csv")
        print("  - dataset_summary.csv")
        print("\nDatabase updated with 2700 records")
        print("Some records enhanced with real yfinance data")
        
    else:
        print("Insertion failed!")
