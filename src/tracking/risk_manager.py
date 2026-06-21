class RiskManager:
    def __init__(self, config):
        self.config = config

    def calculate_position_size(self, account_balance, entry_price, stop_loss, risk_percent=0.01):
        """
        Calculates position size based on fixed % risk per trade.
        """
        risk_amount = account_balance * risk_percent
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0
            
        position_size = risk_amount / price_risk
        return position_size

    def calculate_trailing_sl(self, direction, current_price, current_sl, entry_price, tp1):
        """
        Moves SL to entry once TP1 is hit, then trails at a distance.
        """
        new_sl = current_sl
        
        if direction == "BUY":
            # Move to entry after TP1
            if current_price >= tp1 and current_sl < entry_price:
                new_sl = entry_price
            # Trail after TP1
            elif current_price > tp1:
                trail_sl = current_price * 0.98 # 2% trail
                new_sl = max(current_sl, trail_sl)
        else: # SELL
            if current_price <= tp1 and current_sl > entry_price:
                new_sl = entry_price
            elif current_price < tp1:
                trail_sl = current_price * 1.02
                new_sl = min(current_sl, trail_sl)
                
        return new_sl
