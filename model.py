import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
from datetime import datetime, timedelta

class RealTimeStockPredictor:
    """Real-time stock prediction model with support for multiple stocks"""
    
    def __init__(self, symbol="TCS.NS", period="2y", future_days=10):
        self.symbol = symbol
        self.period = period
        self.future_days = future_days
        self.model = None
        self.data = None
        self.train_model()
    
    def train_model(self):
        """Train the prediction model with latest data"""
        try:
            self.data = yf.download(self.symbol, period=self.period, progress=False)
            self.data = self.data[['Close']]
            self.data.dropna(inplace=True)
            
            if len(self.data) < 20:
                raise ValueError(f"Insufficient data for {self.symbol}")
            
            self.data['Prediction'] = self.data['Close'].shift(-self.future_days)
            
            X = np.array(self.data[['Close']])[:-self.future_days]
            y = np.array(self.data['Prediction'])[:-self.future_days]
            
            self.model = LinearRegression()
            self.model.fit(X, y)
            
            print(f"OK: Model trained for {self.symbol}")
            return True
        except Exception as e:
            print(f"ERROR: Training model: {e}")
            return False
    
    def predict(self):
        if self.model is None:
            return None
        
        last_prices = np.array(self.data[['Close']].tail(self.future_days))
        predictions = self.model.predict(last_prices)
        return predictions
    
    def get_current_price(self):
        return float(self.data['Close'].iloc[-1])
    
    def get_report(self):
        predictions = self.predict()
        future_dates = [(datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(self.future_days)]
        
        if predictions is None:
            predictions_list = []
        else:
            predictions_list = predictions.flatten().tolist() if hasattr(predictions, 'flatten') else predictions.tolist()
        
        return {
            "symbol": self.symbol,
            "current_price": self.get_current_price(),
            "predictions": predictions_list,
            "future_dates": future_dates,
            "timestamp": datetime.now().isoformat()
        }

default_predictor = RealTimeStockPredictor("TCS.NS", period="2y")

def get_prediction(symbol="TCS.NS"):
    try:
        predictor = RealTimeStockPredictor(symbol)
        return predictor.get_report()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    report = default_predictor.get_report()
    print("\nStock Prediction Report:")
    print(f"Symbol: {report['symbol']}")
    print(f"Current Price: {report['current_price']:.2f}")
    print(f"Predictions: {report['predictions']}")
