import pandas as pd
from src.indicators.technical import TechnicalIndicators
from src.indicators.smc import SMCIndicators
from src.filters.scoring import SignalScorer
from src.filters.market_filters import MarketFilters

class SignalGenerator:
    def __init__(self, config):
        self.config = config
        self.ti = TechnicalIndicators()
        self.smc = SMCIndicators()
        self.scorer = SignalScorer(config)
        self.filters = MarketFilters(config)

    def analyze_symbol(self, symbol, mt_data, btc_data):
        # 1. Market Health Check
        if not self.filters.is_market_safe(btc_data):
            return None

        daily = mt_data['trend']
        h4 = mt_data['direction']
        m15 = mt_data['entry']

        # 2. Advanced Analysis
        # SMC Factors
        obs = self.smc.detect_order_blocks(m15)
        fvgs = self.smc.detect_fvg(m15)
        atr = self.smc.calculate_atr(m15).iloc[-1]
        
        # Trend
        ema200_d = self.ti.calculate_ema(daily, 200).iloc[-1]
        current_price = m15['close'].iloc[-1]
        trend_bullish = current_price > ema200_d

        # 3. Scoring (Enhanced for Ultra)
        smc_score = 0
        if trend_bullish:
            # Check if price is near a Bullish Order Block
            recent_bull_ob = [ob for ob in obs if ob['type'] == 'BULLISH']
            if recent_bull_ob and current_price <= recent_bull_ob[-1]['price_high'] * 1.01:
                smc_score += 15
            
            # Check for Bullish FVG below price (attraction)
            recent_bull_fvg = [f for f in fvgs if f['type'] == 'BULLISH']
            if recent_bull_fvg:
                smc_score += 10

        analysis_results = {
            'trend_aligned': trend_bullish,
            'structure': self.ti.detect_market_structure(m15),
            'volume_increasing': m15['volume'].iloc[-1] > m15['volume'].iloc[-5:].mean(),
            'momentum_positive': self.ti.calculate_rsi(m15).iloc[-1] > 50,
            'market_healthy': True,
            'smc_bonus': smc_score
        }
        
        base_score = self.scorer.calculate_score(analysis_results)
        final_score = base_score + smc_score
        
        if final_score >= self.config['scoring']['thresholds']['premium']:
            direction = "BUY" if trend_bullish else "SELL"
            entry = current_price
            
            # ATR-Based SL (Ultra Feature)
            sl_distance = atr * 2.5
            sl = entry - sl_distance if direction == "BUY" else entry + sl_distance
            
            risk = abs(entry - sl)
            
            return {
                'coin': symbol,
                'direction': direction,
                'entry_price': entry,
                'stop_loss': sl,
                'tp1': entry + (risk * 1.5) if direction == "BUY" else entry - (risk * 1.5),
                'tp2': entry + (risk * 3.0) if direction == "BUY" else entry - (risk * 3.0),
                'tp3': entry + (risk * 5.0) if direction == "BUY" else entry - (risk * 5.0),
                'confidence': min(final_score, 100),
                'risk_reward': 3.0,
                'reasons': f"Ultra Score: {final_score}. SMC OB/FVG detected.",
                'status': 'PENDING'
            }
            
        return None
