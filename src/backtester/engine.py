import pandas as pd
from src.scanner.signal_generator import SignalGenerator

class Backtester:
    def __init__(self, config):
        self.config = config
        self.generator = SignalGenerator(config)

    def run(self, df_1d, df_4h, df_15m):
        """
        Runs a backtest on historical data.
        """
        results = []
        # Simplified sliding window backtest
        for i in range(100, len(df_15m) - 20):
            current_15m = df_15m.iloc[:i]
            mt_data = {
                'trend': df_1d,
                'direction': df_4h,
                'entry': current_15m
            }
            
            # Simulate signal generation
            signal = self.generator.analyze_symbol("BACKTEST", mt_data, df_1d)
            
            if signal:
                # Track outcome in the next 20 candles
                future_data = df_15m.iloc[i:i+20]
                outcome = self._evaluate_outcome(signal, future_data)
                results.append({
                    'timestamp': df_15m['timestamp'].iloc[i],
                    'direction': signal['direction'],
                    'outcome': outcome,
                    'profit': 1.5 if outcome == 'WIN' else -1.0
                })
        
        return self._calculate_metrics(results)

    def _evaluate_outcome(self, signal, future_data):
        for _, row in future_data.iterrows():
            if signal['direction'] == 'BUY':
                if row['high'] >= signal['tp1']: return 'WIN'
                if row['low'] <= signal['stop_loss']: return 'LOSS'
            else:
                if row['low'] <= signal['tp1']: return 'WIN'
                if row['high'] >= signal['stop_loss']: return 'LOSS'
        return 'EXPIRED'

    def _calculate_metrics(self, results):
        if not results: return {}
        wins = len([r for r in results if r['outcome'] == 'WIN'])
        total = len(results)
        return {
            'total_trades': total,
            'win_rate': (wins / total * 100) if total > 0 else 0,
            'net_profit': sum([r['profit'] for r in results])
        }
