# Stock Prediction Project - Real-Time Edition

A comprehensive real-time stock price prediction application with machine learning, live data streaming, and advanced analytics.

## 🚀 New Features (Real-Time)

### ⚡ Real-Time Data Processing
- **Live Data Streaming**: Continuous data fetching from Yahoo Finance
- **Background Processing**: Automated updates every 5 minutes
- **Multi-Symbol Tracking**: Monitor multiple stocks simultaneously
- **Data Validation**: Quality checks and error handling
- **Model Retraining**: Automatic model updates with new data

### 📊 Advanced Analytics
- **Data Quality Metrics**: Completeness, accuracy, timeliness tracking
- **Model Performance**: MSE, MAE, R² score monitoring
- **Real-Time Database**: SQLite with optimized schema
- **Historical + Real-Time**: Combined analysis capabilities

### 🔧 API Endpoints

#### Real-Time Management
```
POST /realtime/start          # Start real-time processing
POST /realtime/stop           # Stop real-time processing
GET  /realtime/status         # Get processing status
GET  /realtime/symbols        # List active symbols
POST /realtime/add_symbol     # Add symbol to tracking
POST /realtime/remove_symbol  # Remove symbol from tracking
```

#### Data Retrieval
```
GET /data?symbol=TCS.NS&realtime=true  # Real-time data + predictions
GET /data?symbol=TCS.NS               # Historical data + predictions
GET /stats                            # Database statistics
```

## 🏗️ Architecture

### Real-Time Data Pipeline
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│  Real-Time       │───▶│   Validation    │
│                 │    │  Processor       │    │   & Cleaning    │
│ • Yahoo Finance │    │                  │    │                 │
│ • CSV Fallback  │    │ • Fetching       │    │ • Quality       │
│ • API Feeds     │    │ • Processing     │    │ • Filtering     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐             │
│   ML Models     │◀───│  Model Training  │◀────────────┘
│                 │    │                  │
│ • Linear Reg.   │    │ • Feature Eng.   │
│ • Auto Updates  │    │ • Validation     │
└─────────────────┘    └──────────────────┘
```

### Database Schema
```sql
-- Real-time stock data
CREATE TABLE realtime_stock_data (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    timestamp TEXT,
    open_price REAL, high_price REAL, low_price REAL,
    close_price REAL, volume INTEGER,
    data_source TEXT
);

-- Model performance tracking
CREATE TABLE model_performance (
    id INTEGER PRIMARY KEY,
    symbol TEXT, timestamp TEXT,
    mse REAL, mae REAL, r2_score REAL,
    prediction_accuracy REAL
);

-- Data quality metrics
CREATE TABLE data_quality (
    id INTEGER PRIMARY KEY,
    symbol TEXT, timestamp TEXT,
    completeness REAL, accuracy REAL,
    timeliness REAL, validity REAL
);
```

## 🚀 Quick Start

### Start the Website
```bash
# Easy way to start the website
python start_website.py

# Or start directly
python app.py
```

### Access the Website
Visit `http://localhost:5000` in your browser

### Features Available
- ✅ **Stock Price Prediction** - Enter any stock symbol
- ✅ **Interactive Charts** - Historical + predicted prices
- ✅ **Real-Time Mode** - Live data processing
- ✅ **Multiple Symbols** - Track different stocks
- ✅ **Data Visualization** - Beautiful graphs and statistics
- ✅ **Statistics Dashboard** - Database stats and tracking info

## 📈 Real-Time Features

### Live Data Streaming
- **Automatic Updates**: Every 5 minutes (configurable)
- **Multi-Source**: Yahoo Finance + CSV fallback
- **Error Recovery**: Graceful handling of network issues
- **Data Validation**: Quality checks on all incoming data

### Advanced Analytics
- **Real-Time Predictions**: Updated forecasts with new data
- **Performance Monitoring**: Track model accuracy over time
- **Data Quality Dashboard**: Monitor data reliability
- **Historical Comparison**: Compare real-time vs historical performance

### Background Processing
- **Thread-Safe**: Non-blocking real-time updates
- **Resource Efficient**: Optimized database operations
- **Scalable**: Support for multiple symbols
- **Configurable**: Adjustable update intervals

## 🔧 Configuration

### Real-Time Settings
```python
# In realtime_processor.py
UPDATE_INTERVAL = 5  # minutes
DEFAULT_SYMBOLS = ['TCS.NS', 'RELIANCE.NS']
DATA_RETENTION_DAYS = 30
```

### Model Parameters
```python
# Prediction settings
FUTURE_DAYS = 10
TRAINING_PERIOD_DAYS = 30
MIN_DATA_POINTS = 20
```

## 📊 Data Visualization

### Generate Graphs
```bash
# Create visualizations of your stock data
python show_graphs.py

# View information about generated graphs
python view_graphs.py
```

### Available Graphs
- **📈 Historical Chart** (`TCS.NS_historical.png`) - Historical stock prices over time
- **🔮 Prediction Chart** (`TCS.NS_predictions.png`) - Historical data + future predictions
- **📊 Analysis Dashboard** (`TCS.NS_analysis.png`) - Comprehensive statistics and analysis

### Graph Features
- ✅ **High-Quality PNG** - 300 DPI resolution
- ✅ **Professional Styling** - Seaborn themes with custom colors
- ✅ **Currency Formatting** - Indian Rupee (₹) symbols
- ✅ **Statistical Analysis** - Mean, median, standard deviation
- ✅ **Moving Averages** - 20-day and 50-day trend lines
- ✅ **Return Distribution** - Daily return histograms

## 🎯 Use Cases

### For Traders
- **Live Price Monitoring**: Real-time price updates
- **Prediction Alerts**: Automated forecast updates
- **Multi-Asset Tracking**: Monitor portfolio stocks
- **Risk Assessment**: Real-time volatility analysis

### For Analysts
- **Data Quality Monitoring**: Track data reliability
- **Model Performance**: Evaluate prediction accuracy
- **Historical Analysis**: Compare predictions vs actuals
- **Trend Analysis**: Identify market patterns

### For Developers
- **API Integration**: RESTful endpoints for data access
- **Custom Models**: Extensible ML pipeline
- **Real-Time Processing**: Background data collection
- **Database Analytics**: Query historical data

## 🔍 Monitoring & Debugging

### Real-Time Status
```javascript
// Check processing status
fetch('/realtime/status')
  .then(res => res.json())
  .then(data => console.log(data));
```

### Data Quality Metrics
```sql
-- Check data completeness
SELECT symbol, AVG(completeness) as avg_completeness
FROM data_quality
GROUP BY symbol;
```

### Performance Monitoring
```sql
-- Model accuracy over time
SELECT symbol, timestamp, r2_score
FROM model_performance
ORDER BY timestamp DESC;
```

## 🚨 Troubleshooting

### Real-Time Not Starting
```bash
# Check processor status
curl http://localhost:5000/realtime/status

# Manual start
curl -X POST http://localhost:5000/realtime/start \
  -H "Content-Type: application/json" \
  -d '{"symbol": "TCS.NS"}'
```

### Data Quality Issues
- Check internet connection for live data
- Verify stock symbols are valid
- Review data quality metrics in database
- Switch to sample data for testing

### Performance Problems
- Reduce update frequency
- Limit number of tracked symbols
- Check database size and optimize queries
- Monitor system resources

## 🔮 Future Enhancements

### Planned Features
- [ ] **WebSocket Streaming**: Real-time price updates
- [ ] **Advanced ML Models**: LSTM, Random Forest
- [ ] **Technical Indicators**: RSI, MACD, Bollinger Bands
- [ ] **Portfolio Optimization**: Risk-adjusted predictions
- [ ] **Alert System**: Price and prediction notifications
- [ ] **Multi-Timeframe**: 1m, 5m, 1h, 1d analysis

### API Expansions
- [ ] **REST API**: Full CRUD operations
- [ ] **GraphQL**: Flexible data queries
- [ ] **Webhooks**: Event-driven notifications
- [ ] **Bulk Operations**: Batch data processing

## 📝 License & Contributing

This project demonstrates advanced real-time data processing techniques. Feel free to contribute improvements to the real-time pipeline, ML models, or API endpoints.

---

**🎯 Ready for Real-Time Trading?** Your stock prediction app now processes live market data with enterprise-grade reliability!