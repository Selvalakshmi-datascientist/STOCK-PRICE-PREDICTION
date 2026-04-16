import requests
import json
import time

def activate_realtime_mode():
    """Activate real-time stock monitoring"""
    
    base_url = "http://localhost:5000"
    
    # Stocks to monitor
    stocks_to_track = ['TCS.NS', 'RELIANCE.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS']
    
    print("=== Activating Real-Time Stock Monitoring ===")
    print(f"Target URL: {base_url}")
    print(f"Stocks to track: {stocks_to_track}")
    
    # Step 1: Add stocks to wishlist tracking
    print("\n1. Adding stocks to tracking...")
    for stock in stocks_to_track:
        try:
            response = requests.post(
                f"{base_url}/wishlist/add_corporate_name",
                json={"corporate_name": stock},
                timeout=5
            )
            if response.status_code == 200:
                print(f"   + Added {stock} to tracking")
            else:
                print(f"   - Failed to add {stock}: {response.status_code}")
        except Exception as e:
            print(f"   - Error adding {stock}: {e}")
    
    # Step 2: Start real-time processing
    print("\n2. Starting real-time data processing...")
    try:
        response = requests.post(
            f"{base_url}/wishlist/start",
            json={"corporate_name": "TCS.NS", "interval": 5},  # 5-minute intervals
            timeout=5
        )
        if response.status_code == 200:
            print("   + Real-time processing started successfully")
            print("   + Processing interval: 5 minutes")
        else:
            print(f"   - Failed to start processing: {response.status_code}")
    except Exception as e:
        print(f"   - Error starting processing: {e}")
    
    # Step 3: Check status
    print("\n3. Checking system status...")
    try:
        response = requests.get(f"{base_url}/wishlist/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"   + Processing active: {status.get('is_running', False)}")
            print(f"   + Active symbols: {status.get('active_symbols', [])}")
            print(f"   + Last update: {status.get('last_update', 'N/A')}")
        else:
            print(f"   - Failed to get status: {response.status_code}")
    except Exception as e:
        print(f"   - Error getting status: {e}")
    
    # Step 4: Test data fetching
    print("\n4. Testing real-time data fetching...")
    for stock in stocks_to_track[:2]:  # Test first 2 stocks
        try:
            response = requests.get(f"{base_url}/data", 
                                  params={"corporate_name": stock, "wishlist": "true"}, 
                                  timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'error' not in data:
                    print(f"   + {stock}: Current price = {data.get('current_price', 'N/A')}")
                    print(f"     Data source: {data.get('data_source', 'N/A')}")
                else:
                    print(f"   - {stock}: {data.get('error')}")
            else:
                print(f"   - {stock}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   - {stock}: Error - {e}")
    
    # Step 5: Test yfinance direct endpoint
    print("\n5. Testing yfinance direct endpoint...")
    try:
        response = requests.get(f"{base_url}/yfinance/data", 
                              params={"corporate_name": "TCS.NS"}, 
                              timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   + TCS.NS yfinance: Current price = {data.get('current_price', 'N/A')}")
            print(f"     Data source: {data.get('data_source', 'N/A')}")
            print(f"     Data points: {data.get('data_points', 'N/A')}")
        else:
            print(f"   - YFinance endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   - YFinance endpoint error: {e}")
    
    print("\n=== Real-Time Mode Activation Complete ===")
    print("Web interface available at: http://localhost:5000")
    print("Real-time monitoring is now active!")

if __name__ == "__main__":
    activate_realtime_mode()
