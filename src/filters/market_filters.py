class MarketFilters:
    def __init__(self, config):
        self.config = config['filters']

    def is_market_safe(self, btc_data):
        """
        Check if market conditions are safe based on BTC trend and volatility.
        """
        # Simplified BTC trend check (Price above EMA200 on Daily)
        from src.indicators.technical import TechnicalIndicators
        ti = TechnicalIndicators()
        
        ema200 = ti.calculate_ema(btc_data, 200)
        current_price = btc_data['close'].iloc[-1]
        
        btc_bullish = current_price > ema200.iloc[-1]
        
        if self.config['btc_trend_required'] and not btc_bullish:
            return False
            
        # Volatility check
        returns = btc_data['close'].pct_change()
        volatility = returns.std() * 100
        
        if volatility > self.config['max_volatility']:
            return False
            
        return True
