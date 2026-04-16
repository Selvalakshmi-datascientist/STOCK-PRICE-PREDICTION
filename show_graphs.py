import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import seaborn as sns
import os

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
        self.output_dir = "graphs"
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

    def plot_historical_data(self):
        """Plot historical stock prices and save to file"""
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

        # Save plot
        os.makedirs(self.output_dir, exist_ok=True)
        filename = f"{self.output_dir}/{self.symbol}_historical.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"💾 Historical data plot saved to {filename}")

    def plot_predictions(self):
        """Plot historical data with future predictions and save to file"""
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
        close_value = self.data['Close'].values.flatten()[-1]
        current_price = float(close_value)
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

        # Save plot
        os.makedirs(self.output_dir, exist_ok=True)
        filename = f"{self.output_dir}/{self.symbol}_predictions.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"💾 Prediction plot saved to {filename}")

    def plot_price_distribution(self):
        """Plot price distribution and statistics and save to file"""
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
        close_prices = self.data['Close'].values.flatten()
        mean_val = float(close_prices.mean())
        median_val = float(np.median(close_prices))
        std_val = float(close_prices.std())
        min_val = float(close_prices.min())
        max_val = float(close_prices.max())
        current_val = float(close_prices[-1])

        stats_text = f"""
Price Statistics:
• Mean: ₹{mean_val:.2f}
• Median: ₹{median_val:.2f}
• Std Dev: ₹{std_val:.2f}
• Min: ₹{min_val:.2f}
• Max: ₹{max_val:.2f}
• Current: ₹{current_val:.2f}
"""
        ax4.text(0.1, 0.5, stats_text, transform=ax4.transAxes,
                fontsize=11, verticalalignment='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0"))
        ax4.set_title('Statistics Summary', fontweight='bold')
        ax4.axis('off')

        plt.suptitle(f'{self.symbol} - Comprehensive Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()

        # Save plot
        os.makedirs(self.output_dir, exist_ok=True)
        filename = f"{self.output_dir}/{self.symbol}_analysis.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"💾 Analysis plot saved to {filename}")

    def generate_all_plots(self):
        """Generate all plots and save to files"""
        print(f"\n📈 Generating visualizations for {self.symbol}...\n")

        print("1️⃣ Historical Data Plot:")
        self.plot_historical_data()

        print("\n2️⃣ Prediction Plot:")
        self.plot_predictions()

        print("\n3️⃣ Comprehensive Analysis:")
        self.plot_price_distribution()

        print("\n✅ All graphs saved successfully!")
        print(f"📁 Check the '{self.output_dir}' folder for your graphs")

def main():
    """Main function to demonstrate visualizations"""
    print("🎯 Stock Data Visualization Tool")
    print("=" * 40)

    # Create visualizer
    visualizer = StockDataVisualizer("TCS.NS", period="2y", future_days=10)

    # Generate all plots
    visualizer.generate_all_plots()

    print("\n" + "=" * 50)
    print("📊 Graph Files Created:")
    print("• TCS.NS_historical.png - Historical price chart")
    print("• TCS.NS_predictions.png - Price predictions")
    print("• TCS.NS_analysis.png - Comprehensive analysis")
    print("=" * 50)

if __name__ == "__main__":
    main()