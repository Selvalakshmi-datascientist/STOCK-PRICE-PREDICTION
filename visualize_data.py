import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import seaborn as sns

# Set style for better looking graphs
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class StockDataVisualizer:
    """Class to visualize stock data and predictions"""

    def __init__(self, symbol="TCS.NS", period="2y", future_days=10):
        self.symbol = symbol
        self.period = period
        self.future_days = future_days
        self.data = None
        self.model = None
        self.predictions = None
        self.load_data()

    def load_data(self):
        """Load stock data from Yahoo Finance"""
        try:
            print(f"📊 Loading data for {self.symbol}...")
            self.data = yf.download(self.symbol, period=self.period, progress=False)
            self.data = self.data[['Close']]
            self.data.dropna(inplace=True)
            print(f"✅ Loaded {len(self.data)} data points")
        except Exception as e:
            print(f"❌ Error loading data: {e}")

    def train_model(self):
        """Train the prediction model"""
        if self.data is None or len(self.data) < 20:
            print("❌ Insufficient data for training")
            return False

        try:
            # Prepare data for training
            self.data['Prediction'] = self.data['Close'].shift(-self.future_days)

            X = np.array(self.data[['Close']])[:-self.future_days]
            y = np.array(self.data['Prediction'])[:-self.future_days]

            # Train model
            self.model = LinearRegression()
            self.model.fit(X, y)

            # Make predictions
            last_prices = np.array(self.data[['Close']].tail(self.future_days))
            self.predictions = self.model.predict(last_prices)

            print("✅ Model trained successfully")
            return True
        except Exception as e:
            print(f"❌ Error training model: {e}")
            return False

    def plot_historical_data(self, save_path=None):
        """Plot historical stock prices"""
        if self.data is None:
            print("❌ No data to plot")
            return

        plt.figure(figsize=(12, 6))
        plt.plot(self.data.index, self.data['Close'], linewidth=2, color='#2E86AB', label='Historical Prices')

        plt.title(f'{self.symbol} - Historical Stock Prices', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price (₹)', fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)

        # Format y-axis as currency
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Historical data plot saved to {save_path}")
        else:
            plt.show()

    def plot_predictions(self, save_path=None):
        """Plot historical data with future predictions"""
        if self.data is None:
            print("❌ No data to plot")
            return

        if not self.train_model():
            return

        plt.figure(figsize=(14, 7))

        # Historical data
        plt.plot(self.data.index, self.data['Close'], linewidth=2, color='#2E86AB',
                label='Historical Prices', alpha=0.8)

        # Future predictions
        future_dates = pd.date_range(start=self.data.index[-1] + timedelta(days=1),
                                   periods=self.future_days, freq='D')

        plt.plot(future_dates, self.predictions, linewidth=2, color='#F24236',
                linestyle='--', marker='o', markersize=6, label='Predictions',
                alpha=0.9)

        # Current price marker
        current_price = self.data['Close'].iloc[-1]
        plt.scatter(self.data.index[-1], current_price, color='#F24236',
                   s=100, zorder=5, label=f'Current Price: ₹{current_price:.2f}')

        plt.title(f'{self.symbol} - Stock Price Prediction', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price (₹)', fontsize=12)
        plt.legend(fontsize=12, loc='upper left')
        plt.grid(True, alpha=0.3)

        # Format y-axis as currency
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))

        # Add prediction confidence note
        plt.figtext(0.02, 0.02, 'Note: Predictions are based on Linear Regression model',
                   fontsize=10, style='italic', alpha=0.7)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Prediction plot saved to {save_path}")
        else:
            plt.show()

    def plot_price_distribution(self, save_path=None):
        """Plot price distribution and statistics"""
        if self.data is None:
            print("❌ No data to plot")
            return

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

        # Price distribution histogram
        ax1.hist(self.data['Close'], bins=30, alpha=0.7, color='#2E86AB', edgecolor='black')
        ax1.set_title('Price Distribution', fontweight='bold')
        ax1.set_xlabel('Price (₹)')
        ax1.set_ylabel('Frequency')
        ax1.grid(True, alpha=0.3)

        # Price over time with moving averages
        ax2.plot(self.data.index, self.data['Close'], alpha=0.7, color='#2E86AB', label='Close Price')
        ax2.plot(self.data.index, self.data['Close'].rolling(window=20).mean(),
                color='#F24236', linewidth=2, label='20-day MA')
        ax2.plot(self.data.index, self.data['Close'].rolling(window=50).mean(),
                color='#00A676', linewidth=2, label='50-day MA')
        ax2.set_title('Price with Moving Averages', fontweight='bold')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Price (₹)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Daily returns distribution
        daily_returns = self.data['Close'].pct_change().dropna()
        ax3.hist(daily_returns * 100, bins=30, alpha=0.7, color='#F2A541', edgecolor='black')
        ax3.set_title('Daily Returns Distribution', fontweight='bold')
        ax3.set_xlabel('Daily Return (%)')
        ax3.set_ylabel('Frequency')
        ax3.grid(True, alpha=0.3)

        # Price statistics
        stats_text = ".2f"".2f"".2f"".2f"".2f"f"""
Price Statistics:
• Mean: ₹{self.data['Close'].mean():.2f}
• Median: ₹{self.data['Close'].median():.2f}
• Std Dev: ₹{self.data['Close'].std():.2f}
• Min: ₹{self.data['Close'].min():.2f}
• Max: ₹{self.data['Close'].max():.2f}
• Current: ₹{self.data['Close'].iloc[-1]:.2f}
"""
        ax4.text(0.1, 0.5, stats_text, transform=ax4.transAxes,
                fontsize=11, verticalalignment='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0"))
        ax4.set_title('Statistics Summary', fontweight='bold')
        ax4.axis('off')

        plt.suptitle(f'{self.symbol} - Comprehensive Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Analysis plot saved to {save_path}")
        else:
            plt.show()

    def show_all_plots(self):
        """Show all available plots"""
        print(f"\n📈 Generating visualizations for {self.symbol}...\n")

        print("1️⃣ Historical Data Plot:")
        self.plot_historical_data()

        print("\n2️⃣ Prediction Plot:")
        self.plot_predictions()

        print("\n3️⃣ Comprehensive Analysis:")
        self.plot_price_distribution()

def main():
    """Main function to demonstrate visualizations"""
    print("🎯 Stock Data Visualization Tool")
    print("=" * 40)

    # Create visualizer
    visualizer = StockDataVisualizer("TCS.NS", period="2y", future_days=10)

    # Show all plots
    visualizer.show_all_plots()

if __name__ == "__main__":
    main()