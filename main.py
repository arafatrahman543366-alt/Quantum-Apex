import sys
import os
import uuid
import json
from src.config.loader import load_config, load_env
from src.core.logger import setup_logger
from src.database.models import init_db, Signal, Performance, Trade
from src.scanner.market_data import MarketScanner
from src.scanner.signal_generator import SignalGenerator
from src.tracking.trade_tracker import TradeTracker
from src.telegram.bot import TelegramBot
from src.images.generator import SignalCardGenerator
from src.analytics.performance import PerformanceTracker
from src.backtester.engine import Backtester
from sqlalchemy.orm import sessionmaker
from datetime import datetime

def run_scanner():
    config = load_config()
    env = load_env()
    logger = setup_logger("scanner", config["logging"]["file"])
    
    SessionFactory = init_db(env["DATABASE_URL"])
    scanner = MarketScanner(config["market"]["symbols"], config["market"]["timeframes"])
    generator = SignalGenerator(config)
    tracker = TradeTracker(SessionFactory, config)
    bot = TelegramBot(env["TELEGRAM_BOT_TOKEN"], env["TELEGRAM_CHAT_ID"])
    img_gen = SignalCardGenerator(config)

    logger.info("Starting market scan...")
    
    # Get BTC data for market health
    btc_data = scanner.fetch_ohlcv("BTC/USDT", "1d", limit=200)
    if btc_data is None:
        logger.error("Could not fetch BTC data. Aborting.")
        return

    for symbol in config["market"]["symbols"]:
        if not tracker.check_anti_spam(symbol):
            logger.info(f"Skipping {symbol} due to anti-spam.")
            continue
            
        mt_data = scanner.get_multi_timeframe_data(symbol)
        if not mt_data:
            logger.warning(f"Could not get multi-timeframe data for {symbol}.")
            continue
            
        signal_data = generator.analyze_symbol(symbol, mt_data, btc_data)
        
        if signal_data:
            logger.info(f"New Signal Generated for {symbol}")
            
            session = SessionFactory()
            trade_id = str(uuid.uuid4())[:8]
            new_signal = Signal(
                **signal_data,
                trade_id=trade_id
            )
            session.add(new_signal)
            session.commit()
            
            img_path = f"src/images/{trade_id}.png"
            img_gen.generate_card({**signal_data, "trade_id": trade_id}, img_path, df=mt_data["entry"])
            
            caption = bot.format_signal_message({**signal_data, "trade_id": trade_id})
            reply_markup = json.dumps(bot.get_inline_keyboard(trade_id))
            resp = bot.send_photo(img_path, caption=caption, reply_markup=reply_markup)
            
            if resp.get("ok"):
                new_signal.telegram_msg_id = str(resp["result"]["message_id"])
                session.commit()
            
            session.close()

def run_tracker():
    config = load_config()
    env = load_env()
    logger = setup_logger("tracker", config["logging"]["file"])
    
    SessionFactory = init_db(env["DATABASE_URL"])
    scanner = MarketScanner(config["market"]["symbols"], config["market"]["timeframes"])
    tracker = TradeTracker(SessionFactory, config)
    bot = TelegramBot(env["TELEGRAM_BOT_TOKEN"], env["TELEGRAM_CHAT_ID"])

    logger.info("Starting trade tracking...")
    
    current_prices = {}
    for symbol in config["market"]["symbols"]:
        try:
            ticker = scanner.exchange.fetch_ticker(symbol)
            current_prices[symbol] = ticker["last"]
        except Exception as e:
            logger.error(f"Could not fetch ticker for {symbol}: {e}")
            continue
        
    updates = tracker.update_trade_statuses(current_prices)
    
    for update in updates:
        logger.info(f"Update for {update["coin"]}: {update["new_status"]}")
        msg = bot.format_update_message(update)
        bot.send_message(msg)

def run_report():
    config = load_config()
    env = load_env()
    SessionFactory = init_db(env["DATABASE_URL"])
    tracker = PerformanceTracker(SessionFactory)
    bot = TelegramBot(env["TELEGRAM_BOT_TOKEN"], env["TELEGRAM_CHAT_ID"])
    
    tracker.update_daily_performance()
    report = tracker.generate_weekly_report()
    bot.send_message(report)

def run_backtest():
    config = load_config()
    env = load_env()
    logger = setup_logger("backtester", config["logging"]["file"])
    
    SessionFactory = init_db(env["DATABASE_URL"])
    scanner = MarketScanner(config["market"]["symbols"], config["market"]["timeframes"])
    backtester = Backtester(config)

    logger.info("Starting backtest...")
    
    # For simplicity, backtest only one symbol with pre-fetched data
    symbol = config["market"]["symbols"][0]
    df_1d = scanner.fetch_ohlcv(symbol, "1d", limit=500)
    df_4h = scanner.fetch_ohlcv(symbol, "4h", limit=500)
    df_15m = scanner.fetch_ohlcv(symbol, "15m", limit=500)

    if df_1d is None or df_4h is None or df_15m is None:
        logger.error(f"Could not fetch historical data for backtesting {symbol}. Aborting.")
        return

    results = backtester.run(df_1d, df_4h, df_15m)
    logger.info(f"Backtest Results for {symbol}: {results}")

    # Store results in DB (simplified)
    session = SessionFactory()
    new_backtest_result = Performance(
        date=datetime.utcnow(),
        total_signals=results.get("total_trades", 0),
        wins=results.get("wins", 0),
        win_rate=results.get("win_rate", 0.0),
        avg_rr=results.get("avg_rr", 0.0),
        monthly_profit=results.get("net_profit", 0.0)
    )
    session.add(new_backtest_result)
    session.commit()
    session.close()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "scan"
    
    if mode == "scan":
        run_scanner()
    elif mode == "track":
        run_tracker()
    elif mode == "report":
        run_report()
    elif mode == "backtest":
        run_backtest()
