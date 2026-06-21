import pandas as pd
import numpy as np

class SMCIndicators:
    @staticmethod
    def detect_order_blocks(df, lookback=20):
        """
        Detects potential Order Blocks (Institutional Supply/Demand zones).
        """
        obs = []
        for i in range(len(df) - lookback, len(df)):
            # Bullish OB: Last down candle before a strong up move
            if df['close'].iloc[i] < df['open'].iloc[i]:
                # Check for strong move after
                if i + 2 < len(df) and df['close'].iloc[i+2] > df['high'].iloc[i]:
                    obs.append({
                        'type': 'BULLISH',
                        'price_high': df['high'].iloc[i],
                        'price_low': df['low'].iloc[i],
                        'timestamp': df['timestamp'].iloc[i]
                    })
            
            # Bearish OB: Last up candle before a strong down move
            elif df['close'].iloc[i] > df['open'].iloc[i]:
                if i + 2 < len(df) and df['close'].iloc[i+2] < df['low'].iloc[i]:
                    obs.append({
                        'type': 'BEARISH',
                        'price_high': df['high'].iloc[i],
                        'price_low': df['low'].iloc[i],
                        'timestamp': df['timestamp'].iloc[i]
                    })
        return obs

    @staticmethod
    def detect_fvg(df, lookback=20):
        """
        Detects Fair Value Gaps (FVG) / Imbalances.
        """
        fvgs = []
        for i in range(len(df) - lookback, len(df) - 2):
            # Bullish FVG: Low of candle 3 is higher than High of candle 1
            if df['low'].iloc[i+2] > df['high'].iloc[i]:
                fvgs.append({
                    'type': 'BULLISH',
                    'top': df['low'].iloc[i+2],
                    'bottom': df['high'].iloc[i],
                    'timestamp': df['timestamp'].iloc[i+1]
                })
            # Bearish FVG: High of candle 3 is lower than Low of candle 1
            elif df['high'].iloc[i+2] < df['low'].iloc[i]:
                fvgs.append({
                    'type': 'BEARISH',
                    'top': df['low'].iloc[i],
                    'bottom': df['high'].iloc[i+2],
                    'timestamp': df['timestamp'].iloc[i+1]
                })
        return fvgs

    @staticmethod
    def calculate_atr(df, period=14):
        """
        Calculates Average True Range for volatility-based SL.
        """
        high_low = df['high'] - df['low']
        high_cp = np.abs(df['high'] - df['close'].shift())
        low_cp = np.abs(df['low'] - df['close'].shift())
        
        tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
