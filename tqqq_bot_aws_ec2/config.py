"""
Configuration file for TQQQ/SQQQ Trading Bot
Modify these settings to customize the bot's behavior
"""

# Trading Configuration
TRADING_CONFIG = {
    'tqqq_symbol': 'TQQQ',               # Long ETF symbol
    'sqqq_symbol': 'SQQQ',               # Inverse ETF symbol
    'quantity': 1,                        # Number of shares per trade
    'paper_trading': True,                # Use paper trading (True) or live trading (False)
    
    # Trading times (in PDT) - DO NOT CHANGE for this strategy
    'open_capture_time': {'hour': 6, 'minute': 30},    # Time to capture open price
    'entry_time': {'hour': 7, 'minute': 0},            # Time to make buy decision
    'exit_time': {'hour': 12, 'minute': 59},           # Time to close position
    
    # Risk Management
    'max_position_size': 10,             # Maximum shares to hold at once
    'enable_stop_loss': False,            # Enable stop loss (not recommended for this strategy)
    'stop_loss_percent': 5,               # Stop loss percentage if enabled
}

# AWS EC2 Configuration
AWS_CONFIG = {
    'region': 'us-west-2',                # AWS region for CloudWatch
    'enable_cloudwatch': False,           # Send metrics to CloudWatch
    'cloudwatch_namespace': 'TradingBot', # CloudWatch namespace
    'enable_sns': False,                  # Enable SNS notifications
    'sns_topic_arn': '',                  # SNS topic ARN for alerts
    'instance_id': None,                  # EC2 instance ID (auto-detected if None)
}

# Notification Settings
NOTIFICATION_CONFIG = {
    'enable_desktop': True,               # Desktop notifications (requires GUI)
    'enable_console': True,               # Console output with colors
    'enable_sound': False,                # Sound alerts (not available on EC2)
    'enable_email': False,                # Email notifications (requires setup)
    'enable_sns': False,                  # AWS SNS notifications
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
    'log_file_prefix': 'tqqq_sqqq_bot',  # Log file name prefix
    'keep_logs_days': 30,                # Number of days to keep log files
    'log_rotation': 'daily',             # 'daily', 'size', or 'none'
    'max_log_size_mb': 100,              # Max size per log file if rotation is 'size'
}

# Scheduling Configuration (for automated runs)
SCHEDULE_CONFIG = {
    'auto_run': True,                    # Enable automatic daily runs
    'run_on_weekends': False,            # Run on weekends (markets closed)
    'check_holidays': True,              # Check for market holidays
    'retry_on_failure': True,            # Retry if connection fails
    'max_retries': 3,                    # Maximum number of retries
    'retry_delay_seconds': 60,           # Delay between retries
    'health_check_port': 8080,          # Port for health check endpoint
    'enable_health_check': False,        # Enable HTTP health check endpoint
}

# Advanced Settings
ADVANCED_CONFIG = {
    'use_limit_orders': False,           # Use limit orders instead of market orders
    'limit_order_offset': 0.05,          # Price offset for limit orders ($)
    'order_timeout_seconds': 30,         # Timeout for order execution
    'price_fetch_retries': 3,            # Retries for fetching prices
    'connection_timeout': 10,            # API connection timeout (seconds)
    'time_sync_check': True,             # Check system time synchronization
    'max_time_drift_seconds': 5,         # Maximum allowed time drift
}

# Performance Tracking
PERFORMANCE_CONFIG = {
    'track_performance': True,            # Track and save performance metrics
    'save_trade_history': True,          # Save all trades to CSV
    'generate_reports': True,             # Generate daily/weekly reports
    'report_format': 'both',             # 'csv', 'json', or 'both'
    'calculate_metrics': True,           # Calculate performance metrics
    'metrics_window_days': 30,           # Rolling window for metrics calculation
}

# Systemd Service Configuration (for EC2)
SYSTEMD_CONFIG = {
    'service_name': 'tqqq-bot',         # Systemd service name
    'restart_policy': 'on-failure',     # always, on-failure, or no
    'restart_delay_seconds': 10,        # Delay before restart
    'max_restarts': 5,                  # Maximum restart attempts
    'user': 'ubuntu',                   # User to run service as
    'working_directory': '/home/ubuntu/tqqq_bot_aws_ec2',  # Working directory
}

def get_config():
    """Return the complete configuration dictionary"""
    return {
        'trading': TRADING_CONFIG,
        'aws': AWS_CONFIG,
        'notifications': NOTIFICATION_CONFIG,
        'email': EMAIL_CONFIG,
        'logging': LOGGING_CONFIG,
        'schedule': SCHEDULE_CONFIG,
        'advanced': ADVANCED_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'systemd': SYSTEMD_CONFIG,
    }

def validate_config():
    """Validate configuration settings"""
    errors = []
    warnings = []
    
    # Validate trading times - CRITICAL for this strategy
    if TRADING_CONFIG['open_capture_time'] != {'hour': 6, 'minute': 30}:
        errors.append("Open capture time MUST be 6:30 AM PDT for this strategy")
    
    if TRADING_CONFIG['entry_time'] != {'hour': 7, 'minute': 0}:
        errors.append("Entry time MUST be 7:00 AM PDT for this strategy")
    
    if TRADING_CONFIG['exit_time'] != {'hour': 12, 'minute': 59}:
        errors.append("Exit time MUST be 12:59 PM PDT for this strategy")
    
    # Validate quantities
    if TRADING_CONFIG['quantity'] <= 0:
        errors.append("Trade quantity must be positive")
    
    if TRADING_CONFIG['quantity'] != 1:
        warnings.append(f"Strategy designed for 1 share, but configured for {TRADING_CONFIG['quantity']}")
    
    if TRADING_CONFIG['max_position_size'] < TRADING_CONFIG['quantity']:
        errors.append("Max position size must be >= trade quantity")
    
    # Validate AWS settings if CloudWatch is enabled
    if AWS_CONFIG['enable_cloudwatch']:
        if not AWS_CONFIG['region']:
            errors.append("AWS region required when CloudWatch is enabled")
    
    if AWS_CONFIG['enable_sns']:
        if not AWS_CONFIG['sns_topic_arn']:
            errors.append("SNS topic ARN required when SNS is enabled")
    
    # Validate email settings if enabled
    if NOTIFICATION_CONFIG['enable_email']:
        if not EMAIL_CONFIG['sender_email'] or not EMAIL_CONFIG['sender_password']:
            errors.append("Email credentials required when email notifications are enabled")
    
    # Validate systemd settings
    if SYSTEMD_CONFIG['restart_policy'] not in ['always', 'on-failure', 'no']:
        errors.append("Invalid restart policy. Must be 'always', 'on-failure', or 'no'")
    
    # Check for EC2-specific settings
    if not NOTIFICATION_CONFIG['enable_desktop']:
        warnings.append("Desktop notifications disabled - appropriate for EC2 headless environment")
    
    return errors, warnings

def display_config():
    """Display current configuration in readable format"""
    import json
    config = get_config()
    
    print("\n" + "=" * 60)
    print("TQQQ/SQQQ TRADING BOT CONFIGURATION")
    print("=" * 60)
    
    # Trading settings
    print("\n📈 TRADING SETTINGS:")
    print(f"  Symbols: {TRADING_CONFIG['tqqq_symbol']} (Long) / {TRADING_CONFIG['sqqq_symbol']} (Inverse)")
    print(f"  Quantity per trade: {TRADING_CONFIG['quantity']} share(s)")
    print(f"  Mode: {'PAPER TRADING' if TRADING_CONFIG['paper_trading'] else '⚠️  LIVE TRADING'}")
    print(f"  Open Capture: {TRADING_CONFIG['open_capture_time']['hour']:02d}:{TRADING_CONFIG['open_capture_time']['minute']:02d} PDT")
    print(f"  Entry Time: {TRADING_CONFIG['entry_time']['hour']:02d}:{TRADING_CONFIG['entry_time']['minute']:02d} PDT")
    print(f"  Exit Time: {TRADING_CONFIG['exit_time']['hour']:02d}:{TRADING_CONFIG['exit_time']['minute']:02d} PDT")
    
    # AWS settings
    if AWS_CONFIG['enable_cloudwatch'] or AWS_CONFIG['enable_sns']:
        print("\n☁️  AWS SETTINGS:")
        if AWS_CONFIG['enable_cloudwatch']:
            print(f"  CloudWatch: Enabled (Region: {AWS_CONFIG['region']})")
        if AWS_CONFIG['enable_sns']:
            print(f"  SNS Alerts: Enabled")
    
    # Notification settings
    print("\n🔔 NOTIFICATION SETTINGS:")
    enabled_notifications = []
    if NOTIFICATION_CONFIG['enable_console']:
        enabled_notifications.append("Console")
    if NOTIFICATION_CONFIG['enable_desktop']:
        enabled_notifications.append("Desktop")
    if NOTIFICATION_CONFIG['enable_email']:
        enabled_notifications.append("Email")
    if NOTIFICATION_CONFIG['enable_sns']:
        enabled_notifications.append("AWS SNS")
    print(f"  Enabled channels: {', '.join(enabled_notifications) if enabled_notifications else 'None'}")
    
    # Schedule settings
    print("\n⏰ SCHEDULE SETTINGS:")
    print(f"  Auto-run: {'Enabled' if SCHEDULE_CONFIG['auto_run'] else 'Disabled'}")
    if SCHEDULE_CONFIG['auto_run']:
        print(f"  Run on weekends: {'Yes' if SCHEDULE_CONFIG['run_on_weekends'] else 'No'}")
        print(f"  Check holidays: {'Yes' if SCHEDULE_CONFIG['check_holidays'] else 'No'}")
        print(f"  Retry on failure: {'Yes' if SCHEDULE_CONFIG['retry_on_failure'] else 'No'}")
    
    # Validate configuration
    errors, warnings = validate_config()
    
    if errors:
        print("\n❌ CONFIGURATION ERRORS:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("\n⚠️  CONFIGURATION WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors and not warnings:
        print("\n✅ Configuration is valid!")
    
    print("\n" + "=" * 60)
    
    return len(errors) == 0

if __name__ == "__main__":
    # Display and validate configuration
    is_valid = display_config()
    
    if not is_valid:
        print("\n⚠️  Please fix configuration errors before running the bot!")
        exit(1)
    else:
        print("\n✅ Configuration validated successfully!")
