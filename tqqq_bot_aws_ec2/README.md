# TQQQ/SQQQ Trading Bot for AWS EC2 🤖📈

An automated trading bot designed for AWS EC2 deployment that trades TQQQ (3x Long QQQ) and SQQQ (3x Short QQQ) based on a simple momentum strategy.

## 📊 Trading Strategy

The bot implements a straightforward intraday momentum strategy with strict time-based rules:

### Entry Rules (All times in PDT)
1. **6:30 AM PDT**: Capture TQQQ opening price
2. **7:00 AM PDT**: Make trading decision:
   - If current price > 6:30 AM price → **BUY 1 share of TQQQ**
   - If current price ≤ 6:30 AM price → **BUY 1 share of SQQQ**

### Exit Rules
- **12:59 PM PDT**: Close any open position (TQQQ or SQQQ)

## 🚀 Quick Start

### Prerequisites

- AWS EC2 instance (Amazon Linux 2023 or Ubuntu 20.04/22.04)
- Python 3.8 or higher
- Alpaca Trading Account ([Get free paper trading account](https://alpaca.markets/))
- Stable internet connection

### Local Installation

1. **Clone or copy the bot directory:**
```bash
cd /path/to/your/workspace
# Copy the tqqq_bot_aws_ec2 directory here
```

2. **Install dependencies:**
```bash
cd tqqq_bot_aws_ec2
pip install -r requirements.txt
```

3. **Configure API credentials:**
```bash
# Create .env file
cp .env.example .env
# Edit with your Alpaca credentials
nano .env
```

4. **Test the setup:**
```bash
python run_bot.py --validate-only
python run_bot.py --test-notifications
```

5. **Run the bot (paper trading):**
```bash
python run_bot.py
```

## 🌩️ AWS EC2 Deployment

### Step 1: Launch EC2 Instance

1. Launch an Amazon Linux 2023 EC2 instance (or Ubuntu 20.04/22.04)
2. Instance type: t3.micro is sufficient
3. Security group: Allow SSH (port 22) from your IP
4. Storage: 8-10 GB is sufficient

### Step 2: Connect and Setup

1. **SSH into your instance:**
```bash
# For Amazon Linux 2023:
ssh -i your-key.pem ec2-user@your-ec2-ip

# For Ubuntu:
ssh -i your-key.pem ubuntu@your-ec2-ip
```

2. **Upload the bot files:**
```bash
# From your local machine
# For Amazon Linux 2023:
scp -i your-key.pem -r tqqq_bot_aws_ec2/ ec2-user@your-ec2-ip:~/

# For Ubuntu:
scp -i your-key.pem -r tqqq_bot_aws_ec2/ ubuntu@your-ec2-ip:~/
```

3. **Run the setup script:**
```bash
cd ~/tqqq_bot_aws_ec2
chmod +x setup_ec2.sh
./setup_ec2.sh
```

4. **Configure your API credentials:**
```bash
nano .env
# Add your Alpaca API key and secret
```

### Step 3: Configure Systemd Service

1. **Test the configuration:**
```bash
./test_bot.sh
```

2. **Enable the service:**
```bash
sudo systemctl enable tqqq-bot.service
sudo systemctl start tqqq-bot.service
```

3. **Check status:**
```bash
sudo systemctl status tqqq-bot.service
```

4. **View logs:**
```bash
sudo journalctl -u tqqq-bot.service -f
```

### Step 4: Enable Automatic Daily Runs

**Option 1: Using systemd timer**
```bash
sudo systemctl enable tqqq-bot.timer
sudo systemctl start tqqq-bot.timer
```

**Option 2: Using cron (already configured by setup script)**
```bash
crontab -l  # View the cron job
```

## 📁 File Structure

```
tqqq_bot_aws_ec2/
├── tqqq_sqqq_bot.py      # Main trading bot logic
├── notifications.py       # Notification system
├── config.py             # Configuration settings
├── run_bot.py            # Launcher with validation
├── requirements.txt      # Python dependencies
├── setup_ec2.sh          # EC2 setup script (Amazon Linux 2023 & Ubuntu)
├── tqqq_bot.service      # Systemd service file
├── .env.example          # Environment variables template
├── README.md             # This file
└── logs/                 # Log directory (created automatically)
```

## ⚙️ Configuration

Edit `config.py` to customize bot behavior:

### Key Settings

```python
TRADING_CONFIG = {
    'tqqq_symbol': 'TQQQ',           # Long ETF
    'sqqq_symbol': 'SQQQ',           # Inverse ETF
    'quantity': 1,                    # Shares per trade
    'paper_trading': True,            # Paper vs Live mode
    
    # Trading times (PDT) - DO NOT CHANGE
    'open_capture_time': {'hour': 6, 'minute': 30},
    'entry_time': {'hour': 7, 'minute': 0},
    'exit_time': {'hour': 12, 'minute': 59},
}
```

### AWS Integration (Optional)

```python
AWS_CONFIG = {
    'enable_cloudwatch': False,       # Send metrics to CloudWatch
    'enable_sns': False,              # SNS notifications
    'sns_topic_arn': '',             # Your SNS topic ARN
}
```

## 🔔 Notifications

The bot provides multiple notification channels:

- **Console Output**: Color-coded terminal output with emojis
- **Log Files**: Detailed logs in `logs/` directory
- **Desktop Notifications**: Native OS notifications (if GUI available)
- **AWS SNS**: Optional cloud notifications

## 📈 Performance Tracking

The bot automatically tracks:

- All trade executions with timestamps
- Entry and exit prices
- Daily P&L calculations
- Account balance and buying power
- JSON and text format trade summaries

### Log Files

- `logs/tqqq_sqqq_bot_YYYYMMDD.log` - Main bot activity
- `logs/notifications_YYYYMMDD.log` - Notification history
- `logs/trade_summary_YYYYMMDD.txt` - Daily trade summary
- `logs/trade_data_YYYYMMDD.json` - Structured trade data

## 🛡️ Safety Features

- **Paper Trading Default**: Always starts in paper mode
- **Time Validation**: Ensures trades only during market hours
- **Position Limits**: Configurable maximum position size
- **Error Handling**: Comprehensive error handling with retries
- **Graceful Shutdown**: Handles SIGTERM signals properly
- **Time Sync**: Automatic time synchronization check

## 🧪 Testing

### Test Configuration
```bash
python run_bot.py --validate-only
```

### Test Notifications
```bash
python run_bot.py --test-notifications
```

### Test in Paper Mode
```bash
python run_bot.py --paper
```

### View Configuration
```bash
python run_bot.py --config
```

## 📊 Monitoring on EC2

### Service Status
```bash
sudo systemctl status tqqq-bot.service
```

### Real-time Logs
```bash
sudo journalctl -u tqqq-bot.service -f
```

### Check Timer
```bash
sudo systemctl list-timers --all | grep tqqq
```

### Manual Run
```bash
# For Amazon Linux 2023:
cd /home/ec2-user/tqqq_bot_aws_ec2
./start_bot.sh

# For Ubuntu:
cd /home/ubuntu/tqqq_bot_aws_ec2
./start_bot.sh
```

## 🐛 Troubleshooting

### Common Issues

**Bot doesn't start:**
- Check API credentials in `.env`
- Verify Python version: `python3 --version`
- Check logs: `sudo journalctl -u tqqq-bot.service -n 50`

**Time sync issues:**
- Verify timezone: `timedatectl`
- Check time sync: `chronyc sources`
- Restart chrony: `sudo systemctl restart chrony`

**Connection errors:**
- Check internet: `ping api.alpaca.markets`
- Verify API credentials are correct
- Check if using paper trading credentials for paper mode

**Missing packages:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 📅 Market Hours

The bot operates during regular US market hours:
- **Market Open**: 6:30 AM PDT / 9:30 AM EDT
- **Market Close**: 1:00 PM PDT / 4:00 PM EDT
- **Trading Days**: Monday - Friday (excludes market holidays)

## ⚠️ Important Notes

1. **Paper Trading First**: Always test with paper trading before using real money
2. **Time Zones**: All times are in PDT - the bot handles DST automatically
3. **Market Holidays**: Bot will not trade on market holidays
4. **Position Size**: Default is 1 share per trade
5. **Risk Management**: This is a simple strategy - use appropriate position sizing

## 🔒 Security Best Practices

1. **Never commit `.env` file to git**
2. **Use IAM roles for EC2 if using AWS services**
3. **Restrict SSH access to your IP only**
4. **Enable CloudWatch monitoring**
5. **Set up SNS alerts for critical events**
6. **Regularly update system packages**

## 📜 Disclaimer

**IMPORTANT**: This bot is for educational purposes. Trading involves risk of loss. Past performance does not guarantee future results. Always test thoroughly with paper trading before using real money. The authors are not responsible for any financial losses incurred through use of this software.

## 🎯 Strategy Performance Considerations

Before deploying with real money, consider:

1. **Backtest the strategy** with historical data
2. **Paper trade for at least 30 days**
3. **Monitor key metrics**:
   - Win rate
   - Average profit/loss per trade
   - Maximum drawdown
   - Sharpe ratio
4. **Adjust position sizing** based on your risk tolerance
5. **Consider transaction costs** and slippage

## 📧 Support

For issues:
1. Check the logs in `logs/` directory
2. Verify configuration with `--validate-only`
3. Test with paper trading first
4. Review Alpaca API documentation

## 🔄 Updates and Maintenance

### Update the bot:
```bash
cd /home/ubuntu/tqqq_bot_aws_ec2
git pull  # If using git
sudo systemctl restart tqqq-bot.service
```

### Backup trade data:
```bash
tar -czf trade_logs_backup.tar.gz logs/
```

### Clean old logs:
```bash
find logs/ -name "*.log" -mtime +30 -delete
```

---

**Version**: 1.1.0  
**Last Updated**: September 2025  
**License**: MIT  
**Strategy**: TQQQ/SQQQ Momentum Trading  
**Supported OS**: Amazon Linux 2023, Ubuntu 20.04/22.04
