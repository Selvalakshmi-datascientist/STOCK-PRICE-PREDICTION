from flask import Flask, render_template, jsonify, request
import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
from datetime import datetime
import sqlite3
import os
import threading
from realtime_processor import realtime_processor, get_realtime_data
from stock_list import get_all_stocks

app = Flask(__name__)

# Database setup
DB_FILE = 'stock_data.db'

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS stock_history')
    c.execute('''CREATE TABLE stock_history
                 (id INTEGER PRIMARY KEY, corporate_name TEXT, data_time TEXT, price REAL, prediction REAL)''')
    c.execute('DROP TABLE IF EXISTS watchlist_items')
    c.execute('''CREATE TABLE watchlist_items
                 (id INTEGER PRIMARY KEY,
                  corporate_name TEXT,
                  data_time TEXT,
                  current_price REAL,
                  prediction_day1 REAL,
                  prediction_day2 REAL,
                  prediction_day3 REAL,
                  created_at TEXT)''')
    conn.commit()
    conn.close()

init_db()

def save_to_db(corporate_name, data_time, price, prediction=None):
    """Save stock data to database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO stock_history (corporate_name, data_time, price, prediction) VALUES (?, ?, ?, ?)',
              (corporate_name, data_time, price, prediction))
    conn.commit()
    conn.close()


def save_watchlist_item(corporate_name, date_time, current_price, prediction_day1, prediction_day2, prediction_day3):
    """Save a watchlist item with 3-day prediction"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO watchlist_items (corporate_name, data_time, current_price, prediction_day1, prediction_day2, prediction_day3, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
              (corporate_name, date_time, current_price, prediction_day1, prediction_day2, prediction_day3, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_watchlist_items():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT corporate_name, data_time, current_price, prediction_day1, prediction_day2, prediction_day3, created_at FROM watchlist_items ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return [
        {
            'corporate_name': row[0],
            'data_time': row[1],
            'current_price': row[2],
            'prediction_day1': row[3],
            'prediction_day2': row[4],
            'prediction_day3': row[5],
            'created_at': row[6]
        }
        for row in rows
    ]

def get_stock_data(corporate_name, save=True):
    """Fetch and predict stock data - uses yfinance or fallback to CSV"""
    try:
        # Try to get live data from yfinance
        df = yf.download(corporate_name, period="3mo", progress=False)
        df = df[['Close']]
        df.dropna(inplace=True)

        if len(df) < 20:
            raise ValueError(f"Insufficient live data for {corporate_name}")
        
        data_source = "live"
        
    except Exception as e:
        print(f"Live data unavailable for {corporate_name}: {e}")
        print("Using sample dataset as fallback...")
        
        # Fallback to CSV data
        try:
            df = pd.read_csv('sample_stock_data.csv', index_col='Date', parse_dates=True)
            df = df[['Close']]
            df.dropna(inplace=True)
            data_source = "sample"
        except FileNotFoundError:
            return {"error": "No data available - both live and sample data failed"}

    if len(df) < 20:
        return {"error": f"Insufficient data for {corporate_name}"}

    # Prepare ML model
    future_days = 10
    df['Prediction'] = df['Close'].shift(-future_days)

    X = np.array(df[['Close']])[:-future_days]
    y = np.array(df['Prediction'])[:-future_days]

    model = LinearRegression()
    model.fit(X, y)

    # Future prediction
    future_input = np.array(df[['Close']].tail(future_days))
    future_pred = model.predict(future_input)

    # Data for graph
    past_dates = df.index.strftime('%Y-%m-%d').tolist()
    past_prices = df['Close'].values.flatten().tolist()
    future_dates = [(pd.Timestamp.now() + pd.Timedelta(days=i+1)).strftime('%Y-%m-%d')
                   for i in range(future_days)]

    latest_price = float(past_prices[-1])
    future_prices_list = future_pred.flatten().tolist() if hasattr(future_pred, 'flatten') else future_pred.tolist()

    if save:
        for pred in future_prices_list:
            save_to_db(corporate_name, datetime.now().isoformat(), latest_price, float(pred))

    return {
        "corporate_name": corporate_name,
        "past_dates": past_dates,
        "past_prices": past_prices,
        "future_dates": future_dates,
        "future_prices": future_prices_list,
        "current_price": latest_price,
        "data_points": len(past_prices),
        "timestamp": datetime.now().isoformat(),
        "data_source": data_source
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data', methods=['GET'])
def data():
    """Get stock data and predictions"""
    corporate_name = request.args.get('corporate_name', 'TCS.NS').upper()
    use_wishlist = request.args.get('wishlist', 'false').lower() == 'true'

    if use_wishlist:
        # Use wishlist processor
        result = get_realtime_data(corporate_name)
        if 'error' in result:
            # Fallback to regular method
            result = get_stock_data(corporate_name)
    else:
        # Use regular method
        result = get_stock_data(corporate_name)

    return jsonify(result)

def get_intraday_data(corporate_name):
    """Fetch today's intraday data (hourly intervals)"""
    try:
        # Try to get intraday data from yfinance
        df = yf.download(corporate_name, period="1d", interval="1h", progress=False)
        
        if df.empty or len(df) < 2:
            raise ValueError("Insufficient intraday data")
        
        df = df[['Close']]
        df.dropna(inplace=True)
        data_source = "live"
        
    except Exception as e:
        print(f"Intraday data unavailable for {corporate_name}: {e}")
        print("Using fallback 5-minute interval...")
        
        try:
            # Fallback to 5-minute interval
            df = yf.download(corporate_name, period="1d", interval="5m", progress=False)
            if df.empty or len(df) < 2:
                raise ValueError("Insufficient 5-minute data")
            df = df[['Close']]
            df.dropna(inplace=True)
            data_source = "live"
        except Exception as e2:
            print(f"5-minute data also failed: {e2}")
            return {
                "error": f"No intraday data available for {corporate_name}",
                "corporate_name": corporate_name,
                "intraday_dates": [],
                "intraday_prices": [],
                "current_price": 0,
                "data_source": "none"
            }

    # Extract data for chart
    intraday_dates = df.index.strftime('%H:%M').tolist()
    intraday_prices = df['Close'].values.flatten().tolist()
    current_price = float(intraday_prices[-1]) if intraday_prices else 0
    opening_price = float(intraday_prices[0]) if intraday_prices else 0
    
    return {
        "corporate_name": corporate_name,
        "intraday_dates": intraday_dates,
        "intraday_prices": intraday_prices,
        "current_price": current_price,
        "opening_price": opening_price,
        "data_source": data_source,
        "timestamp": datetime.now().isoformat()
    }

@app.route('/intraday', methods=['GET'])
def intraday():
    """Get today's intraday data"""
    corporate_name = request.args.get('corporate_name', 'TCS.NS').upper()
    result = get_intraday_data(corporate_name)
    return jsonify(result)

@app.route('/watchlist/add', methods=['POST'])
def add_watchlist():
    """Add a stock to the watchlist with 3-day prediction"""
    try:
        corporate_name = request.json.get('corporate_name', '').upper()
        if not corporate_name:
            return jsonify({'status': 'error', 'message': 'Corporate name required'}), 400

        stock_data = get_stock_data(corporate_name, save=False)
        if 'error' in stock_data:
            return jsonify({'status': 'error', 'message': stock_data['error']}), 400

        prediction_prices = stock_data['future_prices'][:3]
        prediction_day1 = float(prediction_prices[0]) if len(prediction_prices) > 0 else stock_data['current_price']
        prediction_day2 = float(prediction_prices[1]) if len(prediction_prices) > 1 else prediction_day1
        prediction_day3 = float(prediction_prices[2]) if len(prediction_prices) > 2 else prediction_day2

        save_watchlist_item(
            corporate_name,
            datetime.now().isoformat(),
            stock_data['current_price'],
            prediction_day1,
            prediction_day2,
            prediction_day3
        )

        return jsonify({
            'status': 'success',
            'message': f'{corporate_name} added to watchlist',
            'watchlist_item': {
                'corporate_name': corporate_name,
                'data_time': datetime.now().isoformat(),
                'current_price': stock_data['current_price'],
                'prediction_day1': prediction_day1,
                'prediction_day2': prediction_day2,
                'prediction_day3': prediction_day3
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/watchlist/list', methods=['GET'])
def watchlist_list():
    """Return current watchlist items"""
    try:
        items = get_watchlist_items()
        return jsonify({'watchlist': items, 'count': len(items)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/watchlist/remove', methods=['POST'])
def remove_watchlist():
    """Remove a stock from the watchlist"""
    try:
        corporate_name = request.json.get('corporate_name', '').upper()
        if not corporate_name:
            return jsonify({'status': 'error', 'message': 'Corporate name required'}), 400

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('DELETE FROM watchlist_items WHERE corporate_name = ?', (corporate_name,))
        conn.commit()
        conn.close()

        return jsonify({'status': 'success', 'message': f'{corporate_name} removed from watchlist'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/wishlist/start', methods=['POST'])
def start_wishlist():
    """Start wishlist change processing"""
    try:
        corporate_name = request.json.get('corporate_name', 'TCS.NS').upper()
        interval = request.json.get('interval', 5)  # minutes

        realtime_processor.add_symbol(corporate_name)

        if not realtime_processor.is_running:
            realtime_processor.start_realtime_processing(interval)

        return jsonify({
            'status': 'success',
            'message': f'Wishlist change processing started for {corporate_name}',
            'interval_minutes': interval
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/wishlist/stop', methods=['POST'])
def stop_wishlist():
    """Stop wishlist change processing"""
    try:
        realtime_processor.stop_realtime_processing()
        return jsonify({
            'status': 'success',
            'message': 'Wishlist change processing stopped'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/wishlist/status', methods=['GET'])
def wishlist_status():
    """Get wishlist change processing status"""
    try:
        status = realtime_processor.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/wishlist/symbols', methods=['GET'])
def get_symbols():
    """Get list of active symbols"""
    try:
        symbols = list(realtime_processor.active_symbols)
        return jsonify({
            'active_symbols': symbols,
            'count': len(symbols)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/available_stocks', methods=['GET'])
def available_stocks():
    """Get all available stocks for selection"""
    try:
        all_stocks = get_all_stocks()
        stock_options = [{'symbol': stock} for stock in all_stocks]
        return jsonify({
            'available_stocks': stock_options,
            'count': len(stock_options)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/wishlist/add_corporate_name', methods=['POST'])
def add_corporate_name():
    """Add a corporate name for wishlist tracking"""
    try:
        corporate_name = request.json.get('corporate_name', '').upper()
        if not corporate_name:
            return jsonify({'status': 'error', 'message': 'Corporate name required'}), 400

        realtime_processor.add_symbol(corporate_name)
        return jsonify({
            'status': 'success',
            'message': f'Added {corporate_name} to wishlist tracking'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/wishlist/remove_corporate_name', methods=['POST'])
def remove_corporate_name():
    """Remove a corporate name from wishlist tracking"""
    try:
        corporate_name = request.json.get('corporate_name', '').upper()
        if not corporate_name:
            return jsonify({'status': 'error', 'message': 'Corporate name required'}), 400

        realtime_processor.remove_symbol(corporate_name)
        return jsonify({
            'status': 'success',
            'message': f'Removed {corporate_name} from wishlist tracking'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/stats', methods=['GET'])
def stats():
    """Get database statistics"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM stock_history')
    total_records = c.fetchone()[0]
    c.execute('SELECT DISTINCT corporate_name FROM stock_history')
    corporate_names = [row[0] for row in c.fetchall()]
    conn.close()
    
    return jsonify({
        "total_records": total_records,
        "corporate_names_tracked": corporate_names
    })

@app.route('/clear_data', methods=['POST'])
def clear_data():
    """Clear all data from the database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('DELETE FROM stock_history')
        conn.commit()
        conn.close()
        return jsonify({
            'status': 'success',
            'message': 'All data cleared from database'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/clear_failed', methods=['POST'])
def clear_failed():
    """Clear failed predictions (NULL predictions) from the database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('DELETE FROM stock_history WHERE prediction IS NULL')
        deleted_count = c.rowcount
        conn.commit()
        conn.close()
        return jsonify({
            'status': 'success',
            'message': f'Cleared {deleted_count} failed predictions from database'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    print("🚀 Initializing Real-Time Stock Processor...")
    
    # Load top 20 stocks automatically for background processing
    # (Loading all 500+ would be resource-intensive at startup)
    top_stocks = get_all_stocks()[:20]
    
    for stock in top_stocks:
        realtime_processor.add_symbol(stock)

    realtime_processor.start_realtime_processing(interval_minutes=5)

    print(f"✅ Real-time processor started with {len(top_stocks)} stocks")
    print(f"✅ Total {len(get_all_stocks())} stocks available for selection")
    print("✅ Access the app at http://localhost:5000")
    app.run(debug=True)