"""
TQQQ/SQQQ Trading Bot for AWS EC2
Strategy: Buy TQQQ or SQQQ based on 7:00 AM vs 6:30 AM price comparison
Exit: Always sell at 12:59 PM PDT
All times are in PDT (Pacific Daylight Time)
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
from alpaca.data.requests import StockLatestQuoteRequest
import signal
import json

# Import notification module
from notifications import NotificationHandler

# Load environment variables
load_dotenv()

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configure logging with more detailed format for EC2
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, f'tqqq_sqqq_bot_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TQQQSQQQTradingBot:
    def __init__(self, paper_trading=True):
        """Initialize the TQQQ/SQQQ Trading Bot for AWS EC2"""
        self.tqqq_symbol = "TQQQ"
        self.sqqq_symbol = "SQQQ"
        self.quantity = 1
        self.paper_trading = paper_trading
        
        # Set up timezone - ALWAYS use PDT for this bot
        self.pdt = pytz.timezone('America/Los_Angeles')
        self.et = pytz.timezone('America/New_York')
        
        # Initialize API clients
        self._setup_api_clients()
        
        # Initialize notification handler
        self.notifier = NotificationHandler()
        
        # Trading state
        self.open_price_630am = None
        self.current_price_7am = None
        self.position_symbol = None  # Track which symbol we bought
        self.position_opened = False
        self.today_trades = []
        
        # Setup graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
        
        logger.info(f"TQQQ/SQQQ Trading Bot initialized - {'PAPER' if paper_trading else 'LIVE'} TRADING MODE")
        logger.info(f"Current PDT time: {datetime.now(self.pdt).strftime('%Y-%m-%d %H:%M:%S PDT')}")
        
        self.notifier.send_notification(
            "Bot Started", 
            f"TQQQ/SQQQ Trading Bot initialized in {'PAPER' if paper_trading else 'LIVE'} mode\n"
            f"Time: {datetime.now(self.pdt).strftime('%Y-%m-%d %H:%M:%S PDT')}"
        )
    
    def _handle_shutdown(self, signum, frame):
        """Handle graceful shutdown"""
        logger.info("Received shutdown signal, cleaning up...")
        self.notifier.send_notification("Bot Shutdown", "Trading bot shutting down gracefully")
        sys.exit(0)
    
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
        try:
            account = self.trading_client.get_account()
            logger.info(f"Connected to Alpaca - Account Status: {account.status}")
            logger.info(f"Buying Power: ${account.buying_power}")
            logger.info(f"Portfolio Value: ${account.portfolio_value}")
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")
            raise
    
    def get_current_price(self, symbol):
        """Get the current price of a symbol with retry logic"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
                quote = self.data_client.get_stock_latest_quote(request)
                
                if symbol in quote:
                    # Try ask price first, then bid price
                    price = quote[symbol].ask_price
                    if price == 0 or price is None:
                        price = quote[symbol].bid_price
                    
                    if price and price > 0:
                        logger.info(f"Current {symbol} price: ${price:.2f}")
                        return float(price)
                    else:
                        logger.warning(f"Invalid price for {symbol}: {price}")
                else:
                    logger.error(f"No quote data for {symbol}")
                    
            except Exception as e:
                logger.error(f"Error getting price (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        return None
    
    def is_market_open(self):
        """Check if the market is currently open"""
        try:
            clock = self.trading_client.get_clock()
            return clock.is_open
        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            return False
    
    def wait_until_time(self, target_hour, target_minute):
        """Wait until a specific time (in PDT)"""
        now_pdt = datetime.now(self.pdt)
        target_time = now_pdt.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
        if now_pdt > target_time:
            logger.warning(f"Target time {target_hour}:{target_minute:02d} PDT has already passed")
            return False
        
        wait_seconds = (target_time - now_pdt).total_seconds()
        logger.info(f"Waiting until {target_hour}:{target_minute:02d} PDT ({wait_seconds:.0f} seconds)...")
        logger.info(f"Current time: {now_pdt.strftime('%H:%M:%S PDT')}")
        
        # Wait with periodic status updates
        while wait_seconds > 0:
            if wait_seconds > 60:
                time.sleep(60)
                wait_seconds -= 60
                if int(wait_seconds) % 300 == 0:  # Update every 5 minutes
                    logger.info(f"Still waiting... {wait_seconds/60:.0f} minutes remaining")
            else:
                time.sleep(wait_seconds)
                break
        
        return True
    
    def place_order(self, symbol, side, quantity=None):
        """Place a market order with error handling"""
        if quantity is None:
            quantity = self.quantity
        
        try:
            # Create order request
            order_request = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=side,
                time_in_force=TimeInForce.DAY
            )
            
            # Submit order
            order = self.trading_client.submit_order(order_request)
            
            # Log and notify
            action = "BUY" if side == OrderSide.BUY else "SELL"
            current_price = self.get_current_price(symbol)
            
            logger.info(f"Order placed: {action} {quantity} {symbol} at ~${current_price:.2f}")
            logger.info(f"Order ID: {order.id}")
            
            self.notifier.send_notification(
                f"Trade Executed: {action} {symbol}",
                f"{action} {quantity} share of {symbol} at ~${current_price:.2f}\n"
                f"Time: {datetime.now(self.pdt).strftime('%H:%M:%S PDT')}\n"
                f"Order ID: {order.id}"
            )
            
            # Track trade
            self.today_trades.append({
                'time': datetime.now(self.pdt),
                'action': action,
                'symbol': symbol,
                'quantity': quantity,
                'price': current_price,
                'order_id': order.id
            })
            
            return order
            
        except Exception as e:
            logger.error(f"Error placing order for {symbol}: {e}")
            self.notifier.send_notification(
                "Order Failed", 
                f"Failed to place {side} order for {symbol}: {str(e)}"
            )
            return None
    
    def get_position(self, symbol):
        """Get current position for a symbol"""
        try:
            positions = self.trading_client.get_all_positions()
            for position in positions:
                if position.symbol == symbol:
                    return position
            return None
        except Exception as e:
            logger.error(f"Error getting position for {symbol}: {e}")
            return None
    
    def capture_open_price(self):
        """Capture the open price at 6:30 AM PDT"""
        logger.info("=" * 60)
        logger.info("Capturing market open price at 6:30 AM PDT...")
        
        self.open_price_630am = self.get_current_price(self.tqqq_symbol)
        
        if self.open_price_630am:
            logger.info(f"✓ Open price captured at 6:30 AM PDT: ${self.open_price_630am:.2f}")
            self.notifier.send_notification(
                "Open Price Captured",
                f"TQQQ open price at 6:30 AM PDT: ${self.open_price_630am:.2f}"
            )
            return True
        else:
            logger.error("✗ Failed to capture open price")
            self.notifier.send_notification(
                "Error: Open Price",
                "Failed to capture TQQQ open price at 6:30 AM PDT"
            )
            return False
    
    def execute_entry_strategy(self):
        """Execute the entry strategy at 7:00 AM PDT"""
        logger.info("=" * 60)
        logger.info("Executing entry strategy at 7:00 AM PDT...")
        
        # Get current price at 7:00 AM
        self.current_price_7am = self.get_current_price(self.tqqq_symbol)
        
        if not self.current_price_7am or not self.open_price_630am:
            logger.error("Cannot execute strategy - missing price data")
            logger.error(f"Open price (6:30 AM): {self.open_price_630am}")
            logger.error(f"Current price (7:00 AM): {self.current_price_7am}")
            self.notifier.send_notification(
                "Strategy Error", 
                "Missing price data for strategy execution"
            )
            return
        
        # Calculate price change
        price_change = self.current_price_7am - self.open_price_630am
        price_change_pct = (price_change / self.open_price_630am) * 100
        
        logger.info(f"Open Price (6:30 AM PDT): ${self.open_price_630am:.2f}")
        logger.info(f"Current Price (7:00 AM PDT): ${self.current_price_7am:.2f}")
        logger.info(f"Price Change: ${price_change:.2f} ({price_change_pct:+.2f}%)")
        
        # Make trading decision based on the rule
        if self.current_price_7am > self.open_price_630am:
            # Price went up - BUY TQQQ
            logger.info("📈 SIGNAL: BUY TQQQ - Price increased since 6:30 AM")
            order = self.place_order(self.tqqq_symbol, OrderSide.BUY)
            if order:
                self.position_symbol = self.tqqq_symbol
                self.position_opened = True
                self.notifier.send_notification(
                    "📈 BUY TQQQ Signal",
                    f"Bought 1 share of TQQQ at ${self.current_price_7am:.2f}\n"
                    f"Price increased {price_change_pct:.2f}% since 6:30 AM open"
                )
        else:
            # Price went down or stayed same - BUY SQQQ
            logger.info("📉 SIGNAL: BUY SQQQ - Price decreased or unchanged since 6:30 AM")
            sqqq_price = self.get_current_price(self.sqqq_symbol)
            if sqqq_price:
                order = self.place_order(self.sqqq_symbol, OrderSide.BUY)
                if order:
                    self.position_symbol = self.sqqq_symbol
                    self.position_opened = True
                    self.notifier.send_notification(
                        "📉 BUY SQQQ Signal",
                        f"Bought 1 share of SQQQ at ${sqqq_price:.2f}\n"
                        f"TQQQ price decreased {abs(price_change_pct):.2f}% since 6:30 AM open"
                    )
            else:
                logger.error("Failed to get SQQQ price")
    
    def close_positions(self):
        """Close any open positions at 12:59 PM PDT"""
        logger.info("=" * 60)
        logger.info("Closing positions at 12:59 PM PDT...")
        
        positions_closed = []
        
        # Check and close TQQQ position
        tqqq_position = self.get_position(self.tqqq_symbol)
        if tqqq_position and float(tqqq_position.qty) > 0:
            current_price = self.get_current_price(self.tqqq_symbol)
            qty = float(tqqq_position.qty)
            
            logger.info(f"Closing TQQQ position: {qty} shares at ${current_price:.2f}")
            order = self.place_order(self.tqqq_symbol, OrderSide.SELL, quantity=qty)
            
            if order:
                # Calculate P&L if we bought TQQQ today
                if self.position_symbol == self.tqqq_symbol and self.current_price_7am:
                    pnl = (current_price - self.current_price_7am) * qty
                    pnl_pct = ((current_price - self.current_price_7am) / self.current_price_7am) * 100
                    positions_closed.append(
                        f"TQQQ: Sold {qty} shares at ${current_price:.2f}\n"
                        f"P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)"
                    )
                else:
                    positions_closed.append(f"TQQQ: Sold {qty} shares at ${current_price:.2f}")
        
        # Check and close SQQQ position
        sqqq_position = self.get_position(self.sqqq_symbol)
        if sqqq_position and float(sqqq_position.qty) > 0:
            current_price = self.get_current_price(self.sqqq_symbol)
            qty = float(sqqq_position.qty)
            
            logger.info(f"Closing SQQQ position: {qty} shares at ${current_price:.2f}")
            order = self.place_order(self.sqqq_symbol, OrderSide.SELL, quantity=qty)
            
            if order:
                # Calculate P&L if we bought SQQQ today
                if self.position_symbol == self.sqqq_symbol:
                    # Get the buy price from today's trades
                    buy_price = None
                    for trade in self.today_trades:
                        if trade['symbol'] == self.sqqq_symbol and trade['action'] == 'BUY':
                            buy_price = trade['price']
                            break
                    
                    if buy_price:
                        pnl = (current_price - buy_price) * qty
                        pnl_pct = ((current_price - buy_price) / buy_price) * 100
                        positions_closed.append(
                            f"SQQQ: Sold {qty} shares at ${current_price:.2f}\n"
                            f"P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)"
                        )
                    else:
                        positions_closed.append(f"SQQQ: Sold {qty} shares at ${current_price:.2f}")
        
        # Send notification
        if positions_closed:
            self.notifier.send_notification(
                "Positions Closed at 12:59 PM",
                "\n".join(positions_closed)
            )
        else:
            logger.info("No positions to close")
            self.notifier.send_notification(
                "No Positions", 
                "No positions to close at 12:59 PM PDT"
            )
    
    def generate_daily_summary(self):
        """Generate and send daily trading summary"""
        logger.info("=" * 60)
        logger.info("DAILY TRADING SUMMARY")
        
        summary_lines = [
            "TQQQ/SQQQ Trading Bot - Daily Summary",
            f"Date: {datetime.now(self.pdt).strftime('%Y-%m-%d')}",
            "=" * 40,
            "",
            "Market Data:",
            f"  Open Price (6:30 AM PDT): ${self.open_price_630am:.2f}" if self.open_price_630am else "  Open Price: Not captured",
            f"  7:00 AM Price: ${self.current_price_7am:.2f}" if self.current_price_7am else "  7:00 AM Price: Not captured",
        ]
        
        if self.open_price_630am and self.current_price_7am:
            change = self.current_price_7am - self.open_price_630am
            change_pct = (change / self.open_price_630am) * 100
            summary_lines.append(f"  Price Change: ${change:.2f} ({change_pct:+.2f}%)")
            summary_lines.append(f"  Signal Generated: {'BUY TQQQ' if self.current_price_7am > self.open_price_630am else 'BUY SQQQ'}")
        
        summary_lines.extend([
            "",
            f"Trades Executed: {len(self.today_trades)}",
        ])
        
        for i, trade in enumerate(self.today_trades, 1):
            summary_lines.extend([
                f"",
                f"Trade {i}:",
                f"  Time: {trade['time'].strftime('%H:%M:%S PDT')}",
                f"  Action: {trade['action']}",
                f"  Symbol: {trade['symbol']}",
                f"  Quantity: {trade['quantity']}",
                f"  Price: ${trade['price']:.2f}" if trade['price'] else "  Price: N/A",
            ])
        
        # Get account info
        try:
            account = self.trading_client.get_account()
            summary_lines.extend([
                "",
                "Account Status:",
                f"  Buying Power: ${account.buying_power}",
                f"  Portfolio Value: ${account.portfolio_value}",
            ])
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
        
        summary = "\n".join(summary_lines)
        logger.info(summary)
        self.notifier.send_notification("📊 Daily Summary", summary)
        
        # Save to file
        summary_file = os.path.join(log_dir, f"trade_summary_{datetime.now(self.pdt).strftime('%Y%m%d')}.txt")
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        # Also save as JSON for easier parsing
        json_file = os.path.join(log_dir, f"trade_data_{datetime.now(self.pdt).strftime('%Y%m%d')}.json")
        trade_data = {
            'date': datetime.now(self.pdt).strftime('%Y-%m-%d'),
            'open_price_630am': self.open_price_630am,
            'current_price_7am': self.current_price_7am,
            'position_symbol': self.position_symbol,
            'trades': [
                {
                    'time': trade['time'].isoformat(),
                    'action': trade['action'],
                    'symbol': trade['symbol'],
                    'quantity': trade['quantity'],
                    'price': trade['price'],
                    'order_id': trade['order_id']
                }
                for trade in self.today_trades
            ]
        }
        with open(json_file, 'w') as f:
            json.dump(trade_data, f, indent=2)
    
    def run(self):
        """Main execution loop"""
        try:
            logger.info("Starting TQQQ/SQQQ Trading Bot...")
            logger.info(f"Current system time: {datetime.now()}")
            logger.info(f"Current PDT time: {datetime.now(self.pdt).strftime('%Y-%m-%d %H:%M:%S PDT')}")
            
            # Check if market is open
            if not self.is_market_open():
                logger.warning("Market is currently closed")
                # Continue anyway as we might be waiting for market open
            
            # Capture open price at 6:30 AM PDT
            if self.wait_until_time(6, 30):
                # Wait a few seconds to ensure market data is available
                time.sleep(5)
                if not self.capture_open_price():
                    logger.error("Failed to capture open price, but continuing...")
            
            # Execute entry strategy at 7:00 AM PDT
            if self.wait_until_time(7, 0):
                self.execute_entry_strategy()
            
            # Close positions at 12:59 PM PDT
            if self.wait_until_time(12, 59):
                self.close_positions()
            
            # Generate daily summary
            self.generate_daily_summary()
            
            logger.info("Trading bot completed successfully")
            self.notifier.send_notification(
                "Bot Completed", 
                "Daily trading cycle completed successfully"
            )
            
        except KeyboardInterrupt:
            logger.info("Bot interrupted by user")
            self.notifier.send_notification("Bot Stopped", "Trading bot stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            self.notifier.send_notification("Bot Error", f"Unexpected error: {str(e)}")
            raise

if __name__ == "__main__":
    # Default to paper trading for safety
    bot = TQQQSQQQTradingBot(paper_trading=True)
    bot.run()
