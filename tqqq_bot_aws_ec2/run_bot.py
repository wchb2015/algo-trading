#!/usr/bin/env python3
"""
Launcher script for TQQQ/SQQQ Trading Bot
Provides validation, testing, and safe execution
"""

import os
import sys
import argparse
import logging
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config, validate_config, display_config
from notifications import NotificationHandler

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if environment is properly configured"""
    errors = []
    warnings = []
    
    # Check for .env file
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_file):
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if not os.path.exists(env_file):
            errors.append("No .env file found. Please create one with your Alpaca API credentials.")
    
    # Check for API credentials
    api_key = os.getenv('ALPACA_API_KEY')
    api_secret = os.getenv('ALPACA_API_SECRET')
    
    if not api_key:
        errors.append("ALPACA_API_KEY not found in environment variables")
    if not api_secret:
        errors.append("ALPACA_API_SECRET not found in environment variables")
    
    # Check Python version
    if sys.version_info < (3, 8):
        errors.append(f"Python 3.8+ required. Current version: {sys.version}")
    
    # Check for required packages
    required_packages = ['alpaca', 'pandas', 'pytz', 'dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        errors.append(f"Missing required packages: {', '.join(missing_packages)}")
        errors.append("Run: pip install -r requirements.txt")
    
    # Check timezone
    try:
        pdt = pytz.timezone('America/Los_Angeles')
        current_time = datetime.now(pdt)
        logger.info(f"Current PDT time: {current_time.strftime('%Y-%m-%d %H:%M:%S PDT')}")
    except Exception as e:
        warnings.append(f"Timezone check warning: {e}")
    
    return errors, warnings

def test_notifications():
    """Test the notification system"""
    print("\n" + "=" * 60)
    print("TESTING NOTIFICATION SYSTEM")
    print("=" * 60)
    
    handler = NotificationHandler()
    handler.test_notifications()
    
    print("\n✅ Notification test complete!")
    return True

def validate_only():
    """Validate configuration without running the bot"""
    print("\n" + "=" * 60)
    print("VALIDATING CONFIGURATION")
    print("=" * 60)
    
    # Check environment
    env_errors, env_warnings = check_environment()
    
    # Check configuration
    config_errors, config_warnings = validate_config()
    
    # Display configuration
    display_config()
    
    # Combine all errors and warnings
    all_errors = env_errors + config_errors
    all_warnings = env_warnings + config_warnings
    
    if all_errors:
        print("\n❌ VALIDATION ERRORS:")
        for error in all_errors:
            print(f"  - {error}")
        return False
    
    if all_warnings:
        print("\n⚠️  VALIDATION WARNINGS:")
        for warning in all_warnings:
            print(f"  - {warning}")
    
    print("\n✅ Validation successful! Bot is ready to run.")
    return True

def run_bot(paper_trading=True, force=False):
    """Run the trading bot"""
    # Validate first
    if not validate_only():
        if not force:
            print("\n❌ Validation failed. Use --force to run anyway (not recommended)")
            return False
        else:
            print("\n⚠️  Running with validation errors (forced)...")
    
    # Import and run the bot
    from tqqq_sqqq_bot import TQQQSQQQTradingBot
    
    # Safety check for live trading
    if not paper_trading:
        print("\n" + "!" * 60)
        print("⚠️  WARNING: LIVE TRADING MODE")
        print("!" * 60)
        print("\nYou are about to run the bot in LIVE TRADING mode.")
        print("This will use REAL MONEY and execute REAL TRADES.")
        print("\nAre you absolutely sure you want to continue?")
        
        response = input("\nType 'YES I WANT LIVE TRADING' to confirm: ")
        if response != "YES I WANT LIVE TRADING":
            print("\n✅ Cancelled. Defaulting to paper trading for safety.")
            paper_trading = True
    
    # Create and run bot
    try:
        bot = TQQQSQQQTradingBot(paper_trading=paper_trading)
        bot.run()
        return True
    except KeyboardInterrupt:
        print("\n\n✅ Bot stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Error running bot: {e}")
        logger.error(f"Bot error: {e}", exc_info=True)
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='TQQQ/SQQQ Trading Bot Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_bot.py                    # Run in paper trading mode
  python run_bot.py --live             # Run in live trading mode (requires confirmation)
  python run_bot.py --validate-only    # Validate configuration without running
  python run_bot.py --test-notifications  # Test notification system
  
Trading Schedule (PDT):
  6:30 AM - Capture open price
  7:00 AM - Make buy decision (TQQQ if price up, SQQQ if price down/same)
  12:59 PM - Close position
        """
    )
    
    parser.add_argument(
        '--paper',
        action='store_true',
        default=True,
        help='Run in paper trading mode (default)'
    )
    
    parser.add_argument(
        '--live',
        action='store_true',
        help='Run in LIVE trading mode (requires confirmation)'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Validate configuration without running the bot'
    )
    
    parser.add_argument(
        '--test-notifications',
        action='store_true',
        help='Test the notification system'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force run even with validation errors (not recommended)'
    )
    
    parser.add_argument(
        '--config',
        action='store_true',
        help='Display current configuration'
    )
    
    args = parser.parse_args()
    
    # Display header
    print("\n" + "=" * 60)
    print("🤖 TQQQ/SQQQ TRADING BOT FOR AWS EC2")
    print("=" * 60)
    print(f"Version: 1.0.0")
    print(f"Strategy: Buy TQQQ/SQQQ based on 7AM vs 6:30AM price")
    print(f"Exit: Always at 12:59 PM PDT")
    print("=" * 60)
    
    # Handle different modes
    if args.config:
        display_config()
        return 0
    
    if args.test_notifications:
        return 0 if test_notifications() else 1
    
    if args.validate_only:
        return 0 if validate_only() else 1
    
    # Determine trading mode
    paper_trading = not args.live
    
    # Run the bot
    success = run_bot(paper_trading=paper_trading, force=args.force)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
