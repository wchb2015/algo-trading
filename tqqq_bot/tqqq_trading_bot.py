"""
TQQQ Trading Bot - Paper Trading Version
Strategy: Buy/Sell TQQQ based on 7:00 AM vs Market Open price comparison
Exit: Always sell at 12:59 PM (1 minute before market close)
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.data.requests import StockLatestQuoteRequest
import pandas as pd

# Import notification module (we'll create this next)
from notifications import NotificationHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tqqq_trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TQQQTradingBot:
    def __init__(self, paper_trading=True):
        """Initialize the TQQQ Trading Bot"""
        self.symbol = "TQQQ"
        self.quantity = 1
        self.paper_trading = paper_trading
        
        # Set up timezone
        self.pdt = pytz.timezone('America/Los_Angeles')
        self.et = pytz.timezone('America/New_York')
        
        # Initialize API clients
        self._setup_api_clients()
        
        # Initialize notification handler
        self.notifier = NotificationHandler()
        
        # Trading state
        self.market_open_price = None
        self.seven_am_price = None
        self.position_opened = False
        self.today_trades = []
        
        logger.info(f"TQQQ Trading Bot initialized - {'PAPER' if paper_trading else 'LIVE'} TRADING MODE")
        self.notifier.send_notification(
            "Bot Started", 
            f"TQQQ Trading Bot initialized in {'PAPER' if paper_trading else 'LIVE'} mode"
        )
    
    def _setup_api_clients(self):
        """Set up Alpaca API clients"""
        api_key = os.getenv('ALPACA_API_KEY')
        api_secret = os.getenv('ALPACA_API_SECRET')
        
        if not api_key or not api_secret:
            raise ValueError("Please set ALPACA_API_KEY and ALPACA_API_SECRET in your .env file")
        
        # Use paper trading URL if in paper mode
        if self.paper_trading:
            base_url = "https://paper-api.alpaca.markets"
        else:
            base_url = "https://api.alpaca.markets"
        
        self.trading_client = TradingClient(
            api_key=api_key,
            secret_key=api_secret,
            paper=self.paper_trading
        )
        
        self.data_client = StockHistoricalDataClient(api_key, api_secret)
        
        # Verify connection
        account = self.trading_client.get_account()
        logger.info(f"Connected to Alpaca - Account Status: {account.status}")
        logger.info(f"Buying Power: ${account.buying_power}")
    
    def get_current_price(self, symbol=None):
        """Get the current price of a symbol"""
        if symbol is None:
            symbol = self.symbol
        
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quote = self.data_client.get_stock_latest_quote(request)
            
            if symbol in quote:
                price = quote[symbol].ask_price
                if price == 0 or price is None:
                    price = quote[symbol].bid_price
                logger.info(f"Current {symbol} price: ${price:.2f}")
                return float(price)
            else:
                logger.error(f"No quote data for {symbol}")
                return None
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            return None
    
    def is_market_open(self):
        """Check if the market is currently open"""
        clock = self.trading_client.get_clock()
        return clock.is_open
    
    def get_market_hours(self):
        """Get today's market hours"""
        clock = self.trading_client.get_clock()
        return clock.open, clock.close
    
    def wait_until_time(self, target_hour, target_minute):
        """Wait until a specific time (in PDT)"""
        now_pdt = datetime.now(self.pdt)
        target_time = now_pdt.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
        if now_pdt > target_time:
            logger.warning(f"Target time {target_hour}:{target_minute:02d} PDT has already passed")
            return False
        
        wait_seconds = (target_time - now_pdt).total_seconds()
        logger.info(f"Waiting until {target_hour}:{target_minute:02d} PDT ({wait_seconds:.0f} seconds)...")
        
        # Wait with periodic status updates
        while wait_seconds > 0:
            if wait_seconds > 60:
                time.sleep(60)
                wait_seconds -= 60
                if wait_seconds % 300 == 0:  # Update every 5 minutes
                    logger.info(f"Still waiting... {wait_seconds/60:.0f} minutes remaining")
            else:
                time.sleep(wait_seconds)
                break
        
        return True
    
    def place_order(self, side, quantity=None):
        """Place a market order"""
        if quantity is None:
            quantity = self.quantity
        
        try:
            # Create order request
            order_request = MarketOrderRequest(
                symbol=self.symbol,
                qty=quantity,
                side=side,
                time_in_force=TimeInForce.DAY
            )
            
            # Submit order
            order = self.trading_client.submit_order(order_request)
            
            # Log and notify
            action = "BUY" if side == OrderSide.BUY else "SELL"
            current_price = self.get_current_price()
            
            logger.info(f"Order placed: {action} {quantity} {self.symbol} at ~${current_price:.2f}")
            self.notifier.send_notification(
                f"Trade Executed: {action}",
                f"{action} {quantity} share of {self.symbol} at ~${current_price:.2f}\nOrder ID: {order.id}"
            )
            
            # Track trade
            self.today_trades.append({
                'time': datetime.now(self.pdt),
                'action': action,
                'quantity': quantity,
                'price': current_price,
                'order_id': order.id
            })
            
            return order
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            self.notifier.send_notification("Order Failed", f"Failed to place {side} order: {str(e)}")
            return None
    
    def get_position(self):
        """Get current position for TQQQ"""
        try:
            positions = self.trading_client.get_all_positions()
            for position in positions:
                if position.symbol == self.symbol:
                    return position
            return None
        except Exception as e:
            logger.error(f"Error getting position: {e}")
            return None
    
    def execute_morning_strategy(self):
        """Execute the morning trading strategy at 7:00 AM"""
        logger.info("=" * 50)
        logger.info("Executing morning strategy...")
        
        # Get 7:00 AM price
        self.seven_am_price = self.get_current_price()
        
        if self.seven_am_price is None or self.market_open_price is None:
            logger.error("Cannot execute strategy - missing price data")
            self.notifier.send_notification("Strategy Error", "Missing price data for strategy execution")
            return
        
        # Make trading decision
        price_change = self.seven_am_price - self.market_open_price
        price_change_pct = (price_change / self.market_open_price) * 100
        
        logger.info(f"Market Open Price (6:30 AM): ${self.market_open_price:.2f}")
        logger.info(f"Current Price (7:00 AM): ${self.seven_am_price:.2f}")
        logger.info(f"Price Change: ${price_change:.2f} ({price_change_pct:.2f}%)")
        
        if self.seven_am_price > self.market_open_price:
            # Price went up - BUY signal
            logger.info("SIGNAL: BUY - Price increased since market open")
            order = self.place_order(OrderSide.BUY)
            if order:
                self.position_opened = True
                self.notifier.send_notification(
                    "BUY Signal Executed",
                    f"Bought TQQQ at ${self.seven_am_price:.2f}\n"
                    f"Price increased {price_change_pct:.2f}% since open"
                )
        else:
            # Price went down or stayed same - SELL signal
            logger.info("SIGNAL: SELL - Price decreased or unchanged since market open")
            
            # Check if we have a position to sell
            position = self.get_position()
            if position and float(position.qty) > 0:
                order = self.place_order(OrderSide.SELL)
                if order:
                    self.notifier.send_notification(
                        "SELL Signal Executed",
                        f"Sold TQQQ at ${self.seven_am_price:.2f}\n"
                        f"Price decreased {abs(price_change_pct):.2f}% since open"
                    )
            else:
                logger.info("No position to sell - skipping SELL signal")
                self.notifier.send_notification(
                    "SELL Signal Skipped",
                    "No TQQQ position to sell"
                )
    
    def close_position(self):
        """Close any open position at 12:59 PM"""
        logger.info("=" * 50)
        logger.info("Executing end-of-day position close...")
        
        position = self.get_position()
        if position and float(position.qty) > 0:
            current_price = self.get_current_price()
            qty = float(position.qty)
            
            logger.info(f"Closing position: {qty} shares of {self.symbol}")
            order = self.place_order(OrderSide.SELL, quantity=qty)
            
            if order:
                # Calculate P&L if we opened position today
                if self.position_opened and self.seven_am_price:
                    pnl = (current_price - self.seven_am_price) * qty
                    pnl_pct = ((current_price - self.seven_am_price) / self.seven_am_price) * 100
                    
                    self.notifier.send_notification(
                        "Position Closed",
                        f"Sold {qty} shares at ${current_price:.2f}\n"
                        f"Day P&L: ${pnl:.2f} ({pnl_pct:.2f}%)"
                    )
                else:
                    self.notifier.send_notification(
                        "Position Closed",
                        f"Sold {qty} shares at ${current_price:.2f}"
                    )
        else:
            logger.info("No position to close")
            self.notifier.send_notification("No Position", "No position to close at market close")
    
    def generate_daily_summary(self):
        """Generate and send daily trading summary"""
        logger.info("=" * 50)
        logger.info("DAILY TRADING SUMMARY")
        
        summary = f"TQQQ Trading Bot - Daily Summary\n"
        summary += f"Date: {datetime.now(self.pdt).strftime('%Y-%m-%d')}\n"
        summary += f"{'='*40}\n"
        
        if self.market_open_price and self.seven_am_price:
            summary += f"Market Open Price: ${self.market_open_price:.2f}\n"
            summary += f"7:00 AM Price: ${self.seven_am_price:.2f}\n"
            summary += f"Signal: {'BUY' if self.seven_am_price > self.market_open_price else 'SELL'}\n"
        
        summary += f"\nTrades Executed: {len(self.today_trades)}\n"
        
        total_pnl = 0
        for i, trade in enumerate(self.today_trades, 1):
            summary += f"\nTrade {i}:\n"
            summary += f"  Time: {trade['time'].strftime('%H:%M:%S PDT')}\n"
            summary += f"  Action: {trade['action']}\n"
            summary += f"  Quantity: {trade['quantity']}\n"
            summary += f"  Price: ${trade['price']:.2f}\n"
        
        # Get account info
        account = self.trading_client.get_account()
        summary += f"\nAccount Status:\n"
        summary += f"  Buying Power: ${account.buying_power}\n"
        summary += f"  Portfolio Value: ${account.portfolio_value}\n"
        
        logger.info(summary)
        self.notifier.send_notification("Daily Summary", summary)
        
        # Save to file
        with open(f"trade_summary_{datetime.now(self.pdt).strftime('%Y%m%d')}.txt", 'w') as f:
            f.write(summary)
    
    def run(self):
        """Main execution loop"""
        try:
            logger.info("Starting TQQQ Trading Bot...")
            
            # Check if market is open
            if not self.is_market_open():
                logger.warning("Market is closed. Waiting for market open...")
                self.notifier.send_notification("Market Closed", "Bot is waiting for market to open")
                
                # You might want to wait until market opens or exit
                # For now, we'll proceed assuming market will open
            
            # Get market open price at 6:30 AM PDT
            logger.info("Waiting for market open (6:30 AM PDT)...")
            if self.wait_until_time(6, 30):
                time.sleep(5)  # Small delay to ensure market is fully open
                self.market_open_price = self.get_current_price()
                if self.market_open_price:
                    logger.info(f"Market open price captured: ${self.market_open_price:.2f}")
                    self.notifier.send_notification(
                        "Market Open",
                        f"TQQQ opened at ${self.market_open_price:.2f}"
                    )
            
            # Execute morning strategy at 7:00 AM PDT
            if self.wait_until_time(7, 0):
                self.execute_morning_strategy()
            
            # Close position at 12:59 PM PDT
            if self.wait_until_time(12, 59):
                self.close_position()
            
            # Generate daily summary
            self.generate_daily_summary()
            
            logger.info("Trading bot completed successfully")
            
        except KeyboardInterrupt:
            logger.info("Bot interrupted by user")
            self.notifier.send_notification("Bot Stopped", "Trading bot stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.notifier.send_notification("Bot Error", f"Unexpected error: {str(e)}")
            raise

if __name__ == "__main__":
    bot = TQQQTradingBot(paper_trading=True)
    bot.run()
