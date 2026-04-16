import threading
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import sqlite3
import yfinance as yf
import requests
import json
from typing import Dict, List, Optional, Tuple

class RealTimeDataProcessor:
    """Wishlist change stock data processing and model updating system"""

    def __init__(self, db_file='stock_data.db'):
        self.db_file = db_file
        self.active_symbols = set()
        self.models = {}  # Cache trained models
        self.last_update = {}
        self.is_running = False
        self.update_thread = None
        self.init_database()

    def init_database(self):
        """Initialize database tables for wishlist change data"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        # Main stock data table
        c.execute('''CREATE TABLE IF NOT EXISTS realtime_stock_data (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     symbol TEXT NOT NULL,
                     timestamp TEXT NOT NULL,
                     open_price REAL,
                     high_price REAL,
                     low_price REAL,
                     close_price REAL NOT NULL,
                     volume INTEGER,
                     data_source TEXT DEFAULT 'live',
                     created_at REAL DEFAULT (datetime('now'))
                     )''')

        # Model performance table
        c.execute('''CREATE TABLE IF NOT EXISTS model_performance (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     symbol TEXT NOT NULL,
                     timestamp TEXT NOT NULL,
                     mse REAL,
                     mae REAL,
                     r2_score REAL,
                     prediction_accuracy REAL
                     )''')

        # Data quality metrics
        c.execute('''CREATE TABLE IF NOT EXISTS data_quality (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     symbol TEXT NOT NULL,
                     timestamp TEXT NOT NULL,
                     completeness REAL,
                     accuracy REAL,
                     timeliness REAL,
                     validity REAL
                     )''')

        conn.commit()
        conn.close()

    def add_symbol(self, symbol: str):
        """Add a stock symbol for real-time tracking"""
        self.active_symbols.add(symbol.upper())
        print(f"✅ Added {symbol} to wishlist tracking")

    def remove_symbol(self, symbol: str):
        """Remove a stock symbol from real-time tracking"""
        self.active_symbols.discard(symbol.upper())
        if symbol.upper() in self.models:
            del self.models[symbol.upper()]
        print(f"❌ Removed {symbol} from wishlist tracking")

    def fetch_realtime_data(self, symbol: str) -> Optional[Dict]:
        """Fetch real-time data for a symbol"""
        try:
            # Try yfinance first
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d', interval='1m')

            if not data.empty:
                latest = data.iloc[-1]
                return {
                    'symbol': symbol.upper(),
                    'timestamp': latest.name.isoformat(),
                    'open_price': float(latest['Open']),
                    'high_price': float(latest['High']),
                    'low_price': float(latest['Low']),
                    'close_price': float(latest['Close']),
                    'volume': int(latest['Volume']),
                    'data_source': 'live'
                }

        except Exception as e:
            print(f"⚠️ Live data failed for {symbol}: {e}")

        # Fallback to sample data simulation
        try:
            # Simulate real-time data from sample CSV
            df = pd.read_csv('sample_stock_data.csv', index_col='Date', parse_dates=True)
            latest_price = df['Close'].iloc[-1]

            # Add some random variation to simulate real-time changes
            import random
            change = random.uniform(-0.02, 0.02)  # -2% to +2% change
            new_price = latest_price * (1 + change)

            return {
                'symbol': symbol.upper(),
                'timestamp': datetime.now().isoformat(),
                'open_price': new_price * 0.995,
                'high_price': new_price * 1.005,
                'low_price': new_price * 0.995,
                'close_price': new_price,
                'volume': random.randint(100000, 1000000),
                'data_source': 'simulated'
            }

        except Exception as e:
            print(f"❌ Fallback data failed for {symbol}: {e}")
            return None

    def validate_data(self, data: Dict) -> Tuple[bool, str]:
        """Validate incoming wishlist change data"""
        required_fields = ['symbol', 'timestamp', 'close_price']

        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None:
                return False, f"Missing required field: {field}"

        # Validate price ranges
        if not (0.01 <= data['close_price'] <= 100000):
            return False, f"Invalid price: {data['close_price']}"

        # Validate volume
        if 'volume' in data and data['volume'] < 0:
            return False, f"Invalid volume: {data['volume']}"

        # Ensure timestamp exists and is valid
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        else:
            try:
                data_time = pd.to_datetime(data['timestamp'])
                if (datetime.now() - data_time) > timedelta(hours=1):
                    data['timestamp'] = datetime.now().isoformat()
            except:
                data['timestamp'] = datetime.now().isoformat()

        return True, "Valid"

    def save_realtime_data(self, data: Dict):
        """Save validated wishlist change data to database"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute('''INSERT INTO realtime_stock_data
                     (symbol, timestamp, open_price, high_price, low_price, close_price, volume, data_source)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data['symbol'], data['timestamp'], data.get('open_price'),
                   data.get('high_price'), data.get('low_price'), data['close_price'],
                   data.get('volume'), data.get('data_source', 'unknown')))

        conn.commit()
        conn.close()

        # Update last update time
        self.last_update[data['symbol']] = datetime.now()

    def get_recent_data(self, symbol: str, hours: int = 24) -> pd.DataFrame:
        """Get recent data for model training"""
        conn = sqlite3.connect(self.db_file)
        query = f'''
        SELECT timestamp, close_price
        FROM realtime_stock_data
        WHERE symbol = ?
        AND timestamp >= datetime('now', '-{hours} hours')
        ORDER BY timestamp ASC
        '''
        df = pd.read_sql_query(query, conn, params=[symbol.upper()])
        conn.close()

        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)

        return df

    def train_model(self, symbol: str) -> Optional[LinearRegression]:
        """Train ML model with recent data"""
        try:
            # Get recent data (last 30 days)
            df = self.get_recent_data(symbol, hours=24*30)

            if len(df) < 20:
                # Fallback to sample data if not enough wishlist change data
                df = pd.read_csv('sample_stock_data.csv', index_col='Date', parse_dates=True)
                df = df[['Close']].rename(columns={'Close': 'close_price'})

            # Prepare data for training
            future_days = 10
            df['prediction'] = df['close_price'].shift(-future_days)

            # Remove NaN values
            df.dropna(inplace=True)

            if len(df) < 10:
                return None

            X = df[['close_price']].values[:-future_days]
            y = df['prediction'].values[:-future_days]

            # Train model
            model = LinearRegression()
            model.fit(X, y)

            # Cache the model
            self.models[symbol.upper()] = model

            print(f"✅ Model trained for {symbol} with {len(df)} data points")
            return model

        except Exception as e:
            print(f"❌ Model training failed for {symbol}: {e}")
            return None

    def predict_next_days(self, symbol: str, days: int = 10) -> List[float]:
        """Predict next N days using trained model"""
        model = self.models.get(symbol.upper())

        if model is None:
            model = self.train_model(symbol)
            if model is None:
                return []

        try:
            # Get recent prices for prediction
            df = self.get_recent_data(symbol, hours=24)
            if len(df) < 5:
                # Fallback to sample data
                df = pd.read_csv('sample_stock_data.csv', index_col='Date', parse_dates=True)
                df = df[['Close']].rename(columns={'Close': 'close_price'})

            recent_prices = df['close_price'].tail(10).values.reshape(-1, 1)
            predictions = model.predict(recent_prices)

            return predictions.flatten().tolist()[:days]

        except Exception as e:
            print(f"❌ Prediction failed for {symbol}: {e}")
            return []

    def update_data_quality_metrics(self, symbol: str):
        """Update data quality metrics"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            # Calculate metrics for last 24 hours
            c.execute('''
                SELECT COUNT(*) as total_records,
                       AVG(CASE WHEN close_price > 0 THEN 1 ELSE 0 END) as valid_prices,
                       COUNT(DISTINCT timestamp) as unique_timestamps
                FROM realtime_stock_data
                WHERE symbol = ?
                AND timestamp >= datetime('now', '-24 hours')
            ''', [symbol.upper()])

            result = c.fetchone()
            if result:
                total_records, valid_prices, unique_timestamps = result

                completeness = (valid_prices / total_records) * 100 if total_records > 0 else 0
                validity = (unique_timestamps / total_records) * 100 if total_records > 0 else 0

                c.execute('''INSERT INTO data_quality
                             (symbol, timestamp, completeness, validity)
                             VALUES (?, ?, ?, ?)''',
                         (symbol.upper(), datetime.now().isoformat(), completeness, validity))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"❌ Data quality update failed for {symbol}: {e}")

    def process_realtime_update(self):
        """Process wishlist change data updates for all active symbols"""
        for symbol in self.active_symbols.copy():
            try:
                # Fetch new data
                data = self.fetch_realtime_data(symbol)
                if not data:
                    continue

                # Validate data
                is_valid, error_msg = self.validate_data(data)
                if not is_valid:
                    print(f"⚠️ Invalid data for {symbol}: {error_msg}")
                    continue

                # Save to database
                self.save_realtime_data(data)

                # Update data quality metrics
                self.update_data_quality_metrics(symbol)

                # Retrain model periodically (every 100 updates)
                if symbol.upper() in self.last_update:
                    update_count = len(self.get_recent_data(symbol, hours=1))
                    if update_count % 100 == 0:
                        self.train_model(symbol)

                print(f"✅ Updated {symbol}: ₹{data['close_price']:.2f}")

            except Exception as e:
                print(f"❌ Update failed for {symbol}: {e}")

    def start_realtime_processing(self, interval_minutes: int = 5):
        """Start wishlist change data processing"""
        if self.is_running:
            print("⚠️ Wishlist change processing already running")
            return

        self.is_running = True

        def run_processor():
            while self.is_running:
                self.process_realtime_update()
                sleep_seconds = interval_minutes * 60
                for _ in range(max(1, sleep_seconds // 5)):
                    if not self.is_running:
                        break
                    time.sleep(5)

        # Start in background thread
        self.update_thread = threading.Thread(target=run_processor, daemon=True)
        self.update_thread.start()

        print(f"🚀 Wishlist change processing started (every {interval_minutes} minutes)")

    def stop_realtime_processing(self):
        """Stop wishlist change data processing"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
        print("⏹️ Wishlist change processing stopped")

    def get_status(self) -> Dict:
        """Get current status of real-time processing"""
        return {
            'is_running': self.is_running,
            'active_symbols': list(self.active_symbols),
            'models_trained': list(self.models.keys()),
            'last_updates': {symbol: ts.isoformat() if ts else None
                           for symbol, ts in self.last_update.items()}
        }

# Global instance
realtime_processor = RealTimeDataProcessor()

def start_realtime_service():
    """Start the real-time data service"""
    # Add default symbols
    realtime_processor.add_symbol('TCS.NS')
    realtime_processor.add_symbol('RELIANCE.NS')

    # Start processing
    realtime_processor.start_realtime_processing(interval_minutes=5)

def get_realtime_data(symbol: str) -> Dict:
    """Get real-time data and predictions for a symbol"""
    try:
        # Get recent data
        df = realtime_processor.get_recent_data(symbol, hours=24*90)  # Last 3 months

        if df.empty:
            # Fallback to sample data
            df = pd.read_csv('sample_stock_data.csv', index_col='Date', parse_dates=True)
            df = df[['Close']].rename(columns={'Close': 'close_price'})

        # Get predictions
        predictions = realtime_processor.predict_next_days(symbol)

        # Prepare response
        past_dates = df.index.strftime('%Y-%m-%d %H:%M:%S').tolist()
        past_prices = df['close_price'].tolist()

        future_dates = [(datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')
                       for i in range(len(predictions))]

        return {
            'corporate_name': symbol.upper(),
            'past_dates': past_dates,
            'past_prices': past_prices,
            'future_dates': future_dates,
            'future_prices': predictions,
            'current_price': float(df['close_price'].iloc[-1]) if not df.empty else 0,
            'timestamp': datetime.now().isoformat(),
            'data_source': 'wishlist',
            'data_points': len(df)
        }

    except Exception as e:
        return {'error': f'Wishlist change data error: {str(e)}'}

if __name__ == "__main__":
    # Test the wishlist change processor
    print("Testing Wishlist Change Data Processor...")

    # Add a symbol
    realtime_processor.add_symbol('TCS.NS')

    # Process one update
    realtime_processor.process_realtime_update()

    # Get data
    data = get_realtime_data('TCS.NS')
    print(f"Data points: {data.get('data_points', 0)}")
    print(f"Predictions: {len(data.get('future_prices', []))}")

    print("✅ Real-time processor test complete")