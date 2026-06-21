import ccxt
import pandas as pd
import time

class MarketScanner:
    def __init__(self, symbols, timeframes):
        self.exchange = ccxt.bybit()
        self.symbols = symbols
        self.timeframes = timeframes

    def fetch_ohlcv(self, symbol, timeframe, limit=100):
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol} on {timeframe}: {e}")
            return None

    def get_multi_timeframe_data(self, symbol):
        data = {}
        for tf_name, tf_value in self.timeframes.items():
            df = self.fetch_ohlcv(symbol, tf_value)
            if df is not None:
                data[tf_name] = df
            time.sleep(0.1) # Rate limiting
        return data
