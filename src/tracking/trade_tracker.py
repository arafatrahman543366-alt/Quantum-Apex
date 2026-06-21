from datetime import datetime, timedelta
from src.database.models import Signal, Trade

class TradeTracker:
    def __init__(self, session_factory, config):
        self.SessionFactory = session_factory
        self.config = config

    def check_anti_spam(self, coin):
        """
        Prevent duplicate signals based on active signals and cooldown.
        """
        session = self.SessionFactory()
        try:
            # Check for active signals
            active_signal = session.query(Signal).filter(
                Signal.coin == coin,
                Signal.status.in_(['PENDING', 'ACTIVE', 'TP1 HIT', 'TP2 HIT'])
            ).first()
            
            if active_signal:
                return False
                
            # Check cooldown
            cooldown_time = datetime.utcnow() - timedelta(hours=self.config['anti_spam']['cooldown_hours'])
            recent_signal = session.query(Signal).filter(
                Signal.coin == coin,
                Signal.created_at > cooldown_time
            ).first()
            
            if recent_signal:
                return False
                
            return True
        finally:
            session.close()

    def update_trade_statuses(self, current_prices):
        """
        Monitor active signals and update their status based on price action.
        """
        session = self.SessionFactory()
        try:
            active_signals = session.query(Signal).filter(
                Signal.status.in_(['PENDING', 'ACTIVE', 'TP1 HIT', 'TP2 HIT'])
            ).all()
            
            updates = []
            for signal in active_signals:
                price = current_prices.get(signal.coin)
                if not price:
                    continue
                
                old_status = signal.status
                new_status = old_status
                
                # Risk Management: Trailing SL
                from src.tracking.risk_manager import RiskManager
                rm = RiskManager(self.config)
                
                if old_status in ['ACTIVE', 'TP1 HIT', 'TP2 HIT']:
                    new_sl = rm.calculate_trailing_sl(
                        signal.direction, price, signal.stop_loss, 
                        signal.entry_price, signal.tp1
                    )
                    if new_sl != signal.stop_loss:
                        signal.stop_loss = new_sl
                        # Note: logger is passed during initialization or use standard logging
                        import logging
                        logging.info(f"Trailing SL updated for {signal.coin} to {new_sl}")

                # Logic for status updates
                if signal.direction == "BUY":
                    if old_status == 'PENDING' and price >= signal.entry_price:
                        new_status = 'ACTIVE'
                    elif price <= signal.stop_loss:
                        new_status = 'SL HIT'
                    elif price >= signal.tp3:
                        new_status = 'COMPLETED'
                    elif price >= signal.tp2:
                        new_status = 'TP2 HIT'
                    elif price >= signal.tp1:
                        new_status = 'TP1 HIT'
                else: # SELL
                    if old_status == 'PENDING' and price <= signal.entry_price:
                        new_status = 'ACTIVE'
                    elif price >= signal.stop_loss:
                        new_status = 'SL HIT'
                    elif price <= signal.tp3:
                        new_status = 'COMPLETED'
                    elif price <= signal.tp2:
                        new_status = 'TP2 HIT'
                    elif price <= signal.tp1:
                        new_status = 'TP1 HIT'
                
                # Check for expiry
                if old_status == 'PENDING':
                    expiry_time = signal.created_at + timedelta(hours=self.config['trade_management']['expiry_hours'])
                    if datetime.utcnow() > expiry_time:
                        new_status = 'EXPIRED'
                
                if new_status != old_status:
                    signal.status = new_status
                    signal.updated_at = datetime.utcnow()
                    updates.append({
                        'signal_id': signal.id,
                        'coin': signal.coin,
                        'old_status': old_status,
                        'new_status': new_status,
                        'msg_id': signal.telegram_msg_id
                    })
            
            session.commit()
            return updates
        finally:
            session.close()
