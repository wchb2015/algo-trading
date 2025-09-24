# 🚀 TQQQ Trading Bot - Quick Start Guide

## ✅ Setup Complete!

Your TQQQ trading bot is ready to use with the following configuration:

### 📊 Current Settings
- **Symbol**: TQQQ
- **Mode**: Paper Trading (safe testing mode)
- **Strategy**: Buy if price rises by 7:00 AM, sell at 12:59 PM
- **Position Size**: 1 share per trade

### 🕐 Trading Schedule (PDT)
- **6:30 AM**: Capture market open price
- **7:00 AM**: Execute buy/sell decision
- **12:59 PM**: Close position before market close

## 🎯 How to Run the Bot

### 1️⃣ First Time - Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Test Everything Works
```bash
# Test notifications (you should see/hear alerts)
python run_tqqq_bot.py --test-notifications

# Validate configuration
python run_tqqq_bot.py --validate-only
```

### 3️⃣ Run the Bot (Paper Trading)
```bash
python run_tqqq_bot.py
```

The bot will:
1. Connect to Alpaca paper trading
2. Wait until 6:30 AM PDT to capture open price
3. At 7:00 AM PDT, buy or sell based on price movement
4. At 12:59 PM PDT, close any open position
5. Send you notifications for all trades
6. Generate a daily summary

## 📱 Notifications

You'll receive notifications for:
- ✅ Bot start/stop
- 📈 Market open price
- 💰 Buy/sell executions
- 📊 Position closing
- 📋 Daily P&L summary

Notifications appear as:
- Desktop popups (macOS native)
- Colored console output
- Sound alerts for trades
- Log files for history

## ⚠️ Important Reminders

1. **Currently in PAPER TRADING mode** - No real money at risk
2. **Bot must be running before 6:30 AM PDT** to capture market open
3. **Keep terminal open** while bot is running
4. **Check logs** in `tqqq_trading_bot.log` for details

## 📅 Daily Schedule

For best results, start the bot at **6:25 AM PDT** on trading days:
```bash
# Run every trading day at 6:25 AM PDT
python run_tqqq_bot.py
```

## 🔍 Monitor Performance

After each trading day, check:
- `trade_summary_YYYYMMDD.txt` - Daily trade summary
- `tqqq_trading_bot.log` - Detailed activity log
- `notifications_YYYYMMDD.log` - All notifications

## 🛠️ Customization

To adjust settings, edit `config.py`:
- Change position size
- Modify trading times
- Adjust notification preferences

## 📞 Need Help?

1. Check `README_TQQQ_BOT.md` for detailed documentation
2. Review log files for error messages
3. Ensure market is open (weekdays only)
4. Verify internet connection

## 🎉 You're Ready!

Your bot is configured and ready to trade TQQQ automatically. Start with paper trading to test the strategy before considering live trading.

**Remember**: Always monitor the bot's performance and adjust as needed!
