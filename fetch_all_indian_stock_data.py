import math
import time
import pandas as pd
import yfinance as yf
from stock_list import get_all_stocks

OUTPUT_CSV = 'all_indian_stock_data.csv'
FAIL_LOG = 'failed_symbols.log'
PERIOD = '5y'
CHUNK_SIZE = 20


def normalize_dataframe(df, symbol):
    # Flatten multiindex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        if df.columns.nlevels == 2:
            df = df.loc[:, (slice(None), symbol)].copy()
            df.columns = df.columns.droplevel(1)
        else:
            df.columns = [col[-1] if isinstance(col, tuple) else col for col in df.columns]
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    df['Symbol'] = symbol
    df.reset_index(inplace=True)
    return df


def fetch_chunk(tickers):
    data = yf.download(tickers=tickers, period=PERIOD, progress=False, threads=True)
    if data.empty:
        return {}, tickers

    fetched = {}
    missing = []

    if isinstance(data.columns, pd.MultiIndex):
        symbols_in_data = set(data.columns.get_level_values(1))
        for symbol in tickers:
            if symbol in symbols_in_data:
                try:
                    df_symbol = normalize_dataframe(data, symbol)
                    if not df_symbol.empty:
                        fetched[symbol] = df_symbol
                    else:
                        missing.append(symbol)
                except Exception:
                    missing.append(symbol)
            else:
                missing.append(symbol)
    else:
        # Single ticker result
        symbol = tickers[0]
        try:
            df_symbol = normalize_dataframe(data, symbol)
            if not df_symbol.empty:
                fetched[symbol] = df_symbol
            else:
                missing.append(symbol)
        except Exception:
            missing.append(symbol)

    return fetched, missing


def main():
    stocks = get_all_stocks()
    print(f"Total symbols to fetch: {len(stocks)}")

    all_frames = []
    failed_symbols = []
    total_symbols = len(stocks)

    for idx in range(0, total_symbols, CHUNK_SIZE):
        chunk = stocks[idx: idx + CHUNK_SIZE]
        print(f"Fetching chunk {idx // CHUNK_SIZE + 1}/{math.ceil(total_symbols / CHUNK_SIZE)}: {len(chunk)} symbols")

        fetched, missing = fetch_chunk(chunk)
        for symbol, df_symbol in fetched.items():
            all_frames.append(df_symbol)
        failed_symbols.extend(missing)

        print(f"  fetched: {len(fetched)}  failed: {len(missing)}")
        time.sleep(1)

    if all_frames:
        combined_df = pd.concat(all_frames, ignore_index=True)
        combined_df.sort_values(['Date', 'Symbol'], inplace=True)
        combined_df.to_csv(OUTPUT_CSV, index=False)
        print(f"✅ Saved combined dataset: {OUTPUT_CSV} ({len(combined_df)} rows)")
    else:
        print("No data fetched; nothing saved.")

    if failed_symbols:
        with open(FAIL_LOG, 'w', encoding='utf-8') as f:
            for symbol in sorted(set(failed_symbols)):
                f.write(symbol + '\n')
        print(f"⚠️ Failed symbols logged: {FAIL_LOG} ({len(set(failed_symbols))} unique symbols)")


if __name__ == '__main__':
    main()
