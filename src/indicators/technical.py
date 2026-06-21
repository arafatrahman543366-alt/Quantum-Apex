import pandas as pd
import numpy as np

class TechnicalIndicators:
    @staticmethod
    def calculate_ema(df, period):
        return df['close'].ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(df, period=14):
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_macd(df, fast=12, slow=26, signal=9):
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def detect_market_structure(df):
        """
        Simple logic to detect Higher Highs (HH), Higher Lows (HL), 
        Break of Structure (BOS), and Retests.
        """
        # This is a simplified version for the MVP
        highs = df['high'].rolling(window=5, center=True).max()
        lows = df['low'].rolling(window=5, center=True).min()
        
        last_high = highs.iloc[-2]
        prev_high = highs.iloc[-10] # Simplified lookback
        
        last_low = lows.iloc[-2]
        prev_low = lows.iloc[-10]
        
        hh = last_high > prev_high
        hl = last_low > prev_low
        
        # BOS: Break of previous high
        bos = df['close'].iloc[-1] > prev_high
        
        return {
            'hh': hh,
            'hl': hl,
            'bos': bos
        }
