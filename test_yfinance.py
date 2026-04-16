import yfinance as yf

def test_yfinance():
    print("Testing yfinance integration...")
    
    # Test with TCS.NS
    ticker = yf.Ticker('TCS.NS')
    data = ticker.history(period='5d', interval='1d')
    
    if data.empty:
        print("❌ No data received from yfinance")
        return False
    
    print(f"✅ Data shape: {data.shape}")
    print(f"✅ Latest price: ₹{data['Close'].iloc[-1]:.2f}")
    print(f"✅ Date range: {data.index[0]} to {data.index[-1]}")
    print("✅ yfinance integration working!")
    
    # Test real-time data
    realtime_data = ticker.history(period="1d", interval="1m")
    if not realtime_data.empty:
        print(f"✅ Real-time data available: {len(realtime_data)} data points")
        print(f"✅ Current price: ₹{realtime_data['Close'].iloc[-1]:.2f}")
    
    return True

if __name__ == "__main__":
    test_yfinance()
