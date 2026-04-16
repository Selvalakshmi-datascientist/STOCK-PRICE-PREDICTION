#!/usr/bin/env python3
"""
Stock Prediction Website Launcher
Easy way to start the stock prediction web application
"""

import os
import sys
import subprocess
import time

def start_website():
    """Start the stock prediction website"""
    print("🚀 Starting Stock Prediction Website...")
    print("=" * 50)

    # Check if required files exist
    required_files = ['app.py', 'realtime_processor.py', 'templates/index.html']
    missing_files = []

    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False

    print("✅ All required files found")
    print("✅ Starting Flask web server...")

    try:
        # Start the Flask app
        cmd = [sys.executable, 'app.py']
        process = subprocess.Popen(cmd, cwd=os.getcwd())

        print("✅ Website started successfully!")
        print("🌐 Access your website at: http://localhost:5000")
        print()
        print("📊 Available Features:")
        print("• Stock Price Prediction with Charts")
        print("• Wishlist Change Data Processing")
        print("• Multiple Stock Symbol Support")
        print("• Historical Data Analysis")
        print("• Interactive Graphs")
        print()
        print("🎯 How to use:")
        print("1. Open http://localhost:5000 in your browser")
        print("2. Enter a stock symbol (e.g., TCS.NS, RELIANCE.NS)")
        print("3. Click 'Get Data' to see predictions")
        print("4. Use 'Wishlist Change' for live updates")
        print("5. Check 'Wishlist Status' for wishlist processing info")
        print()
        print("⚠️  Press Ctrl+C in terminal to stop the website")
        print("=" * 50)

        # Wait for user to stop
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping website...")
            process.terminate()
            process.wait()
            print("✅ Website stopped")

    except Exception as e:
        print(f"❌ Error starting website: {e}")
        return False

    return True

if __name__ == "__main__":
    start_website()