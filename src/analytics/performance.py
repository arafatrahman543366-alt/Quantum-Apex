from datetime import datetime, timedelta
from src.database.models import Signal, Performance
import json

class PerformanceTracker:
    def __init__(self, session_factory):
        self.SessionFactory = session_factory

    def update_daily_performance(self):
        session = self.SessionFactory()
        try:
            today = datetime.utcnow().date()
            start_of_day = datetime.combine(today, datetime.min.time())
            
            signals = session.query(Signal).filter(
                Signal.created_at >= start_of_day
            ).all()
            
            if not signals:
                return
                
            total = len(signals)
            wins = len([s for s in signals if 'TP' in s.status or s.status == 'COMPLETED'])
            losses = len([s for s in signals if s.status == 'SL HIT'])
            
            win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
            avg_rr = sum([s.risk_reward for s in signals]) / total if total > 0 else 0
            
            perf = session.query(Performance).filter(Performance.date == start_of_day).first()
            if not perf:
                perf = Performance(date=start_of_day)
                session.add(perf)
                
            perf.total_signals = total
            perf.wins = wins
            perf.losses = losses
            perf.win_rate = win_rate
            perf.avg_rr = avg_rr
            
            session.commit()
        finally:
            session.close()

    def generate_weekly_report(self):
        session = self.SessionFactory()
        try:
            one_week_ago = datetime.utcnow() - timedelta(days=7)
            signals = session.query(Signal).filter(
                Signal.created_at >= one_week_ago
            ).all()
            
            if not signals:
                return "No signals generated in the last 7 days."
                
            total = len(signals)
            wins = len([s for s in signals if 'TP' in s.status or s.status == 'COMPLETED'])
            losses = len([s for s in signals if s.status == 'SL HIT'])
            total_closed = wins + losses
            win_rate = (wins / total_closed * 100) if total_closed > 0 else 0
            
            report = (
                f"🏆 *QUANTUM APEX | PERFORMANCE REPORT* 🏆\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📊 *QUANT STATS:*\n"
                f"🔢 Total Executions: `{total}`\n"
                f"✅ Successful: `{wins}`\n"
                f"❌ Failed: `{losses}`\n"
                f"📈 Win Rate: `{win_rate:.2f}%`\n\n"
                f"🔥 *ELITE ASSETS:*\n"
                f"{self._get_top_coins(signals)}\n\n"
                f"🛡 _Algorithmic precision for elite traders._"
            )
            return report
        finally:
            session.close()

    def _get_top_coins(self, signals):
        coin_stats = {}
        for s in signals:
            if s.coin not in coin_stats:
                coin_stats[s.coin] = 0
            if 'TP' in s.status or s.status == 'COMPLETED':
                coin_stats[s.coin] += 1
        
        sorted_coins = sorted(coin_stats.items(), key=lambda x: x[1], reverse=True)
        return ", ".join([f"{c} ({v})" for c, v in sorted_coins[:3]])
