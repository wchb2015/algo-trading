# TQQQ Trading Bot 🤖📈

An automated trading bot for TQQQ (ProShares UltraPro QQQ) that executes a simple momentum-based strategy using the Alpaca Trading API.

## 📊 Trading Strategy

The bot implements a straightforward intraday momentum strategy:

1. **6:30 AM PDT**: Capture the market open price of TQQQ
2. **7:00 AM PDT**: Make trading decision:
   - If current price > open price → **BUY 1 share**
   - If current price ≤ open price → **SELL 1 share** (if position exists)
3. **12:59 PM PDT**: Close any open position (1 minute before market close)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Alpaca Trading Account (free paper trading account available)
- macOS, Linux, or Windows

### Installation

1. **Install required packages:**
```bash
pip install -r requirements.txt
```

2. **Set up your Alpaca API credentials:**

Your `.env` file already exists with your credentials. If you need to update them:
```bash
# Edit .env file with your Alpaca API credentials
ALPACA_API_KEY=your_api_key_here
ALPACA_API_SECRET=your_api_secret_here
```

3. **Test the setup:**
```bash
# Validate configuration
python run_tqqq_bot.py --validate-only

# Test notifications
python run_tqqq_bot.py --test-notifications
```

### Running the Bot

**Paper Trading (Recommended for testing):**
```bash
python run_tqqq_bot.py
```

**Live Trading (Use with caution!):**
```bash
python run_tqqq_bot.py --live
```

## 📁 File Structure

```
algo-trading/
├── tqqq_trading_bot.py      # Main trading bot logic
├── notifications.py          # Notification system (desktop, console, sound)
├── config.py                # Configuration settings
├── run_tqqq_bot.py          # Launcher script with validation
├── requirements.txt         # Python dependencies
├── .env                     # API credentials (not in git)
└── README_TQQQ_BOT.md      # This file
```

## 🔔 Notifications

The bot provides multiple notification channels:

- **Desktop Notifications**: Native OS notifications for trade executions
- **Console Output**: Color-coded terminal output with emojis
- **Sound Alerts**: Audio alerts for critical events (trades)
- **Log Files**: Detailed logs saved to `tqqq_trading_bot.log`

### Notification Events

- Bot start/stop
- Market open price capture
- Buy/sell signal execution
- Position closing
- Daily P&L summary
- Errors and warnings

## ⚙️ Configuration

Edit `config.py` to customize bot behavior:

### Key Settings

```python
TRADING_CONFIG = {
    'symbol': 'TQQQ',           # Symbol to trade
    'quantity': 1,               # Shares per trade
    'paper_trading': True,       # Paper vs Live mode
    
    # Trading times (PDT)
    'market_open_time': {'hour': 6, 'minute': 30},
    'entry_time': {'hour': 7, 'minute': 0},
    'exit_time': {'hour': 12, 'minute': 59},
}
```

### Notification Settings

```python
NOTIFICATION_CONFIG = {
    'enable_desktop': True,      # Desktop notifications
    'enable_console': True,      # Console output
    'enable_sound': True,        # Sound alerts
}
```

## 📈 Performance Tracking

The bot automatically tracks and logs:

- All trade executions with timestamps
- Entry and exit prices
- Daily P&L calculations
- Account balance and buying power
- Trade summaries saved to `trade_summary_YYYYMMDD.txt`

## 🛡️ Safety Features

- **Paper Trading Default**: Bot runs in paper trading mode by default
- **Position Limits**: Configurable maximum position size
- **Market Hours Check**: Only trades during regular market hours
- **Error Handling**: Comprehensive error handling with retries
- **Confirmation Prompts**: Requires confirmation before live trading

## 📝 Logs and Output

### Log Files

- `tqqq_trading_bot.log`: Main bot activity log
- `notifications_YYYYMMDD.log`: Daily notification log
- `trade_summary_YYYYMMDD.txt`: Daily trade summary

### Console Output Example

```
============================================================
📢 🔔 Trade Alert: BUY TQQQ
------------------------------------------------------------
BUY 1 shares of TQQQ
Price: $45.67
Total Value: $45.67
Order ID: abc123def456
============================================================
```

## 🧪 Testing

### Test Notifications
```bash
python run_tqqq_bot.py --test-notifications
```

### Validate Configuration
```bash
python run_tqqq_bot.py --validate-only
```

### Paper Trading Test
```bash
python run_tqqq_bot.py --paper
```

## 📅 Scheduling (Optional)

### Using Cron (Linux/Mac)

Add to crontab to run every weekday at 6:25 AM PDT:
```bash
25 6 * * 1-5 cd /path/to/algo-trading && /usr/bin/python3 run_tqqq_bot.py
```

### Using Task Scheduler (Windows)

Create a task that runs `python run_tqqq_bot.py` at 6:25 AM on weekdays.

## ⚠️ Important Notes

1. **Paper Trading First**: Always test with paper trading before using real money
2. **Market Hours**: Bot only works during regular market hours (6:30 AM - 1:00 PM PDT)
3. **Internet Connection**: Requires stable internet connection
4. **API Limits**: Be aware of Alpaca API rate limits
5. **Risk Management**: This is a simple strategy - use appropriate position sizing

## 🐛 Troubleshooting

### Common Issues

**Missing packages error:**
```bash
pip install -r requirements.txt
```

**API credentials error:**
- Check your `.env` file has correct credentials
- Ensure you're using paper trading credentials for paper mode

**Notification not working:**
- macOS: Allow terminal/Python in System Preferences > Notifications
- Install plyer: `pip install plyer`

**Time zone issues:**
- Bot automatically handles PDT/PST conversion
- All times in config are in PDT

## 📊 Strategy Performance

**Backtest Recommended**: Before running live, backtest the strategy to understand:
- Win rate
- Average profit/loss per trade
- Maximum drawdown
- Sharpe ratio

## 🔒 Security

- API credentials stored in `.env` file (not in git)
- Paper trading mode by default
- Confirmation required for live trading
- All trades logged for audit trail

## 📧 Support

For issues or questions:
1. Check the log files for error details
2. Verify configuration in `config.py`
3. Test with paper trading first
4. Review Alpaca API documentation

## 📜 Disclaimer

**IMPORTANT**: This bot is for educational purposes. Trading involves risk of loss. Past performance does not guarantee future results. Always test thoroughly with paper trading before using real money. The authors are not responsible for any financial losses incurred through use of this software.

## 🎯 Next Steps

1. **Test with paper trading** for at least 1 week
2. **Monitor performance** and adjust strategy if needed
3. **Set appropriate position sizes** based on your risk tolerance
4. **Consider adding stop-loss** and take-profit levels
5. **Backtest the strategy** with historical data

---

**Version**: 1.0.0  
**Last Updated**: September 2025  
**License**: MIT
