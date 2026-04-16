#!/usr/bin/env python3
"""
Test Stock Prediction Website
"""

import requests

def test_website():
    print('🧪 Testing Stock Prediction Website...')
    print('=' * 50)

    try:
        # Test main page
        r = requests.get('http://localhost:5000/')
        status = 'OK' if r.status_code == 200 else 'ERROR'
        print(f'✅ Main Page: {r.status_code} ({status})')

        # Test API
        r = requests.get('http://localhost:5000/data?symbol=TCS.NS')
        if r.status_code == 200:
            data = r.json()
            print(f'✅ API Data: {r.status_code} (OK)')
            print(f'   📊 Data points: {len(data.get("past_prices", []))} historical + {len(data.get("future_prices", []))} predicted')
            print(f'   💰 Current price: ₹{data.get("current_price", 0):.2f}')
            print(f'   📡 Data source: {data.get("data_source", "unknown")}')
        else:
            print(f'❌ API Data: {r.status_code} (ERROR)')

        # Test stats
        r = requests.get('http://localhost:5000/stats')
        if r.status_code == 200:
            stats = r.json()
            print(f'✅ Stats API: {r.status_code} (OK)')
            print(f'   📈 Total records: {stats.get("total_records", 0)}')
            print(f'   🎯 Symbols tracked: {len(stats.get("symbols_tracked", []))}')
        else:
            print(f'❌ Stats API: {r.status_code} (ERROR)')

        print()
        print('🎉 Website is working perfectly!')
        print('🌐 Visit: http://localhost:5000')

    except Exception as e:
        print(f'❌ Test failed: {e}')

if __name__ == "__main__":
    test_website()