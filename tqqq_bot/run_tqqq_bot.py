#!/usr/bin/env python3
"""
Simple launcher script for TQQQ Trading Bot
Run this script to start the trading bot with proper configuration
"""

import sys
import os
import argparse
from datetime import datetime
import pytz
from config import get_config, validate_config
from tqqq_trading_bot import TQQQTradingBot
from notifications import NotificationHandler

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = {
        'alpaca': 'alpaca-py',
        'dotenv': 'python-dotenv',
        'pytz': 'pytz',
        'pandas': 'pandas'
    }
    
    missing_packages = []
    for module, package in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install missing packages:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("\nPlease create a .env file with your Alpaca API credentials:")
        print("  ALPACA_API_KEY=your_api_key_here")
        print("  ALPACA_API_SECRET=your_api_secret_here")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('ALPACA_API_KEY') or not os.getenv('ALPACA_API_SECRET'):
        print("❌ API credentials not found in .env file!")
        print("\nPlease add your Alpaca API credentials to the .env file")
        return False
    
    return True

def display_status():
    """Display current bot status and configuration"""
    config = get_config()
    pdt = pytz.timezone('America/Los_Angeles')
    now = datetime.now(pdt)
    
    print("\n" + "="*60)
    print("🤖 TQQQ TRADING BOT STATUS")
    print("="*60)
    
    print(f"\n📅 Current Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"📊 Symbol: {config['trading']['symbol']}")
    print(f"💰 Quantity per Trade: {config['trading']['quantity']} share(s)")
    print(f"🏦 Mode: {'PAPER TRADING' if config['trading']['paper_trading'] else '⚠️ LIVE TRADING'}")
    
    print("\n⏰ Schedule:")
    print(f"  • Market Open Capture: {config['trading']['market_open_time']['hour']:02d}:{config['trading']['market_open_time']['minute']:02d} PDT")
    print(f"  • Entry Decision: {config['trading']['entry_time']['hour']:02d}:{config['trading']['entry_time']['minute']:02d} PDT")
    print(f"  • Exit Position: {config['trading']['exit_time']['hour']:02d}:{config['trading']['exit_time']['minute']:02d} PDT")
    
    print("\n🔔 Notifications:")
    print(f"  • Desktop: {'✅' if config['notifications']['enable_desktop'] else '❌'}")
    print(f"  • Console: {'✅' if config['notifications']['enable_console'] else '❌'}")
    print(f"  • Sound: {'✅' if config['notifications']['enable_sound'] else '❌'}")
    
    print("\n" + "="*60)

def main():
    """Main entry point for the trading bot"""
    parser = argparse.ArgumentParser(description='TQQQ Trading Bot Launcher')
    parser.add_argument('--test-notifications', action='store_true', 
                       help='Test notification system')
    parser.add_argument('--validate-only', action='store_true',
                       help='Validate configuration without running')
    parser.add_argument('--paper', action='store_true',
                       help='Force paper trading mode')
    parser.add_argument('--live', action='store_true',
                       help='Force live trading mode (use with caution!)')
    
    args = parser.parse_args()
    
    # Test notifications if requested
    if args.test_notifications:
        print("Testing notification system...")
        notifier = NotificationHandler()
        notifier.send_notification("Test Alert", "TQQQ Bot notification test successful!")
        notifier.send_trade_alert("BUY", "TQQQ", 1, 45.67, "TEST123")
        print("✅ Notification test completed. Check your desktop for notifications.")
        return
    
    # Check requirements
    print("🔍 Checking requirements...")
    if not check_requirements():
        sys.exit(1)
    
    # Check environment file
    if not check_env_file():
        sys.exit(1)
    
    # Validate configuration
    print("🔍 Validating configuration...")
    errors = validate_config()
    if errors:
        print("❌ Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print("✅ All checks passed!")
    
    # Display current status
    display_status()
    
    # Validate-only mode
    if args.validate_only:
        print("\n✅ Configuration validated successfully. Exiting (--validate-only mode).")
        return
    
    # Determine trading mode
    config = get_config()
    paper_trading = config['trading']['paper_trading']
    
    if args.paper:
        paper_trading = True
        print("\n📝 Paper trading mode forced via command line")
    elif args.live:
        paper_trading = False
        print("\n⚠️  LIVE TRADING MODE forced via command line")
        response = input("Are you sure you want to run in LIVE mode? (type 'YES' to confirm): ")
        if response != 'YES':
            print("Live trading cancelled.")
            return
    
    # Confirm before starting
    mode_str = "PAPER" if paper_trading else "LIVE"
    print(f"\n🚀 Ready to start TQQQ Trading Bot in {mode_str} mode")
    print("\nStrategy:")
    print("  1. Capture TQQQ price at market open (6:30 AM PDT)")
    print("  2. At 7:00 AM PDT:")
    print("     - BUY 1 share if price > open price")
    print("     - SELL 1 share if price <= open price (if position exists)")
    print("  3. Close any position at 12:59 PM PDT")
    
    response = input("\nPress Enter to start the bot (or Ctrl+C to cancel): ")
    
    try:
        # Create and run the bot
        print("\n🤖 Starting TQQQ Trading Bot...")
        bot = TQQQTradingBot(paper_trading=paper_trading)
        bot.run()
        
    except KeyboardInterrupt:
        print("\n\n⛔ Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
