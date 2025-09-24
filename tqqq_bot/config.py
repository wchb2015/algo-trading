"""
Configuration file for TQQQ Trading Bot
Modify these settings to customize the bot's behavior
"""

# Trading Configuration
TRADING_CONFIG = {
    'symbol': 'TQQQ',                    # Symbol to trade
    'quantity': 1,                        # Number of shares per trade
    'paper_trading': True,                # Use paper trading (True) or live trading (False)
    
    # Trading times (in PDT)
    'market_open_time': {'hour': 6, 'minute': 30},     # Market open time to capture price
    'entry_time': {'hour': 7, 'minute': 0},            # Time to make buy/sell decision
    'exit_time': {'hour': 12, 'minute': 59},           # Time to close position
    
    # Risk Management
    'max_position_size': 10,             # Maximum shares to hold at once
    'stop_loss_percent': None,            # Optional: Stop loss percentage (e.g., 5 for 5%)
    'take_profit_percent': None,          # Optional: Take profit percentage
}

# Notification Settings
NOTIFICATION_CONFIG = {
    'enable_desktop': True,               # Desktop notifications
    'enable_console': True,               # Console output with colors
    'enable_sound': True,                 # Sound alerts for critical events
    'enable_email': False,                # Email notifications (requires setup)
}

# Email Configuration (optional - only if enable_email is True)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your_email@gmail.com',
    'sender_password': 'your_app_password',  # Use app-specific password
    'recipient_email': 'recipient@gmail.com',
}

# Logging Configuration
LOGGING_CONFIG = {
    'log_level': 'INFO',                 # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'log_to_file': True,                 # Save logs to file
    'log_file_prefix': 'tqqq_bot',       # Log file name prefix
    'keep_logs_days': 30,                # Number of days to keep log files
}

# Scheduling Configuration (for automated runs)
SCHEDULE_CONFIG = {
    'auto_run': False,                   # Enable automatic daily runs
    'run_on_weekends': False,            # Run on weekends (markets closed)
    'check_holidays': True,              # Check for market holidays
    'retry_on_failure': True,            # Retry if connection fails
    'max_retries': 3,                    # Maximum number of retries
    'retry_delay_seconds': 60,           # Delay between retries
}

# Advanced Settings
ADVANCED_CONFIG = {
    'use_limit_orders': False,           # Use limit orders instead of market orders
    'limit_order_offset': 0.05,          # Price offset for limit orders ($)
    'order_timeout_seconds': 30,         # Timeout for order execution
    'price_fetch_retries': 3,            # Retries for fetching prices
    'connection_timeout': 10,            # API connection timeout (seconds)
}

# Backtesting Configuration
BACKTEST_CONFIG = {
    'enabled': False,                    # Enable backtesting mode
    'start_date': '2024-01-01',         # Backtest start date
    'end_date': '2024-12-31',           # Backtest end date
    'initial_capital': 10000,           # Starting capital for backtest
    'commission_per_trade': 0,          # Commission per trade
}

# Performance Tracking
PERFORMANCE_CONFIG = {
    'track_performance': True,           # Track and save performance metrics
    'save_trade_history': True,         # Save all trades to CSV
    'generate_reports': True,            # Generate daily/weekly reports
    'report_format': 'csv',             # 'csv', 'json', or 'both'
}

def get_config():
    """Return the complete configuration dictionary"""
    return {
        'trading': TRADING_CONFIG,
        'notifications': NOTIFICATION_CONFIG,
        'email': EMAIL_CONFIG,
        'logging': LOGGING_CONFIG,
        'schedule': SCHEDULE_CONFIG,
        'advanced': ADVANCED_CONFIG,
        'backtest': BACKTEST_CONFIG,
        'performance': PERFORMANCE_CONFIG,
    }

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Validate trading times
    if TRADING_CONFIG['entry_time']['hour'] < TRADING_CONFIG['market_open_time']['hour']:
        errors.append("Entry time cannot be before market open time")
    
    if TRADING_CONFIG['exit_time']['hour'] > 13:  # 1 PM PDT is market close
        errors.append("Exit time cannot be after market close (1:00 PM PDT)")
    
    # Validate quantities
    if TRADING_CONFIG['quantity'] <= 0:
        errors.append("Trade quantity must be positive")
    
    if TRADING_CONFIG['max_position_size'] < TRADING_CONFIG['quantity']:
        errors.append("Max position size must be >= trade quantity")
    
    # Validate percentages
    if TRADING_CONFIG['stop_loss_percent'] and TRADING_CONFIG['stop_loss_percent'] <= 0:
        errors.append("Stop loss percentage must be positive")
    
    if TRADING_CONFIG['take_profit_percent'] and TRADING_CONFIG['take_profit_percent'] <= 0:
        errors.append("Take profit percentage must be positive")
    
    return errors

if __name__ == "__main__":
    # Test configuration validation
    errors = validate_config()
    if errors:
        print("Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration is valid!")
    
    # Display current configuration
    import json
    config = get_config()
    print("\nCurrent Configuration:")
    print(json.dumps(config, indent=2, default=str))
