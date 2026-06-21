# 💎 QUANTUM APEX | ULTRA QUANT ENGINE 💎

A production-ready, institutional-grade automated crypto signal system. **Quantum Apex** leverages advanced Smart Money Concepts (SMC), multi-timeframe algorithmic analysis, and dynamic risk management to deliver elite market insights.

## 🚀 Ultra Features

- **Advanced Market Scanning with Smart Money Concepts (SMC):** Incorporates **Order Blocks (OB)**, **Fair Value Gaps (FVG)**, and **Liquidity Zone** detection for high-precision entries and exits.
- **Dynamic Risk Management:** Features **Trailing Stop Losses** and **Dynamic Position Sizing** based on account balance and volatility, ensuring robust capital protection.
- **Interactive Telegram Bot:** Engage with the bot using **Telegram Inline Buttons** to manually close trades, request instant market scans, or view charts directly from the chat.
- **Polished Visual Signal Cards:** Automatically generates stunning, branded signal images with advanced charting overlays, including SMC elements, indicators, and clear entry/target zones.
- **Multi-Timeframe Analysis:** Scans multiple crypto pairs across Daily, 4H, 1H, and 15M timeframes for comprehensive market insights.
- **High-Quality Signal Logic:** Utilizes EMA crossovers, RSI, MACD, and Market Structure (BOS, HH/HL) for superior signal generation.
- **Enhanced Signal Scoring System:** Only sends signals with a confidence score of 90/100 or higher, now incorporating SMC factors.
- **Trade Tracking & Management:** Monitors Entry, TP1, TP2, TP3, and Stop Loss levels with real-time updates.
- **Anti-Spam & Cooldown:** Prevents duplicate signals for the same coin within a configurable timeframe.
- **Backtesting Engine:** A dedicated module to rigorously test signal strategies against historical data, providing statistical validation and optimization opportunities.
- **GitHub Actions Integration:** Runs efficiently and for free on GitHub Actions with automated scheduling for scanning, tracking, and reporting.
- **Free Market Data Sources:** Uses public market data from CCXT (Bybit) and CoinGecko, requiring no Binance API key.

## 🛠 Project Structure (Ultra Version)

```text
crypto_signal_bot/
├── src/
│   ├── core/          # Logging and common utilities
│   ├── scanner/       # Market data and signal generation
│   ├── indicators/    # Technical analysis (EMA, RSI, MACD, OB, FVG, ATR)
│   ├── filters/       # Scoring and market health filters
│   ├── telegram/      # Bot integration, formatting, interactive buttons
│   ├── database/      # SQLite models and connection
│   ├── tracking/      # Trade lifecycle management, trailing SL, position sizing
│   ├── analytics/     # Performance reporting, polished reports
│   ├── images/        # Advanced signal card generation with charting
│   ├── config/        # Configuration loader
│   ├── tests/         # Unit and integration tests
│   └── backtester/    # Backtesting engine and strategy validation
├── .github/           # GitHub Actions workflows
├── main.py            # Entry point
├── config.yaml        # System settings
└── requirements.txt   # Dependencies
```

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.11+
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- A Telegram Chat ID (where signals will be sent)

### 2. Local Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
4. Fill in your `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.

### 3. Running Locally
- **Scan for signals:** `python main.py scan`
- **Track active trades:** `python main.py track`
- **Generate performance report:** `python main.py report`
- **Run backtest:** `python main.py backtest`

### 4. GitHub Actions Deployment
1. Create a new GitHub repository.
2. Go to **Settings > Secrets and variables > Actions**.
3. Add the following secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Push the code to the repository.
5. The bot will start running automatically based on the cron schedule in `.github/workflows/bot_runner.yml`.

## 📈 Signal Scoring Logic
- **Trend (25pts):** Price above EMA200 on Daily/4H.
- **Structure (25pts):** Break of Structure (BOS) or Higher Highs/Lows.
- **Volume (20pts):** Increasing volume on the 15M entry timeframe.
- **Momentum (15pts):** RSI and MACD alignment.
- **Market Health (15pts):** BTC trend and volatility check.
- **SMC Bonus (up to 25pts):** Proximity to Order Blocks, Fair Value Gaps, and Liquidity Zones.

## ⚖️ Disclaimer
This software is for educational purposes only. Trading cryptocurrencies involves significant risk. Never trade more than you can afford to lose.
