"""
TSLA Real-time Price Tracker - Final Version
Supports both polling and streaming modes with proper error handling
"""

import os
import sys
import time
import logging
from datetime import datetime
import pytz
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.data.requests import StockLatestQuoteRequest, StockLatestTradeRequest
from alpaca.trading.client import TradingClient
from colorama import init, Fore, Style
import pandas as pd
import asyncio
from typing import Optional

# Initialize colorama for colored output
init(autoreset=True)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tsla_realtime.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TSLARealtimeTracker:
    def __init__(self, mode='polling', paper_trading=True):
        """
        Initialize the TSLA Real-time Tracker
        
        Args:
            mode: 'polling' or 'streaming'
            paper_trading: Use paper trading endpoints (True) or live (False)
        """
        self.symbol = "TSLA"
        self.mode = mode
        self.paper_trading = paper_trading
        
        # Price tracking
        self.last_price = None
        self.last_bid = None
        self.last_ask = None
        self.daily_high = None
        self.daily_low = None
        self.volume = 0
        
        # Timezone
        self.et = pytz.timezone('America/New_York')
        self.pdt = pytz.timezone('America/Los_Angeles')
        
        # Data storage
        self.price_history = []
        self.save_to_csv = False
        
        # Initialize API clients
        self._setup_api_clients()
        
        logger.info(f"TSLA Real-time Tracker initialized - Mode: {mode.upper()}")
        print(f"{Fore.GREEN}✓ TSLA Real-time Tracker initialized")
        print(f"  Mode: {Fore.CYAN}{mode.upper()}")
        print(f"  Paper Trading: {Fore.YELLOW}{'Yes' if paper_trading else 'No'}{Style.RESET_ALL}")
    
    def _setup_api_clients(self):
        """Set up Alpaca API clients"""
        api_key = os.getenv('ALPACA_API_KEY')
        api_secret = os.getenv('ALPACA_API_SECRET')
        
        if not api_key or not api_secret:
            raise ValueError("Please set ALPACA_API_KEY and ALPACA_API_SECRET in your .env file")
        
        # Historical data client for polling
        self.data_client = StockHistoricalDataClient(api_key, api_secret)
        
        # Trading client for account info
        self.trading_client = TradingClient(
            api_key=api_key,
            secret_key=api_secret,
            paper=self.paper_trading
        )
        
        # Streaming client for real-time data
        if self.mode == 'streaming':
            # Use the correct feed parameter
            self.stream_client = StockDataStream(
                api_key, 
                api_secret,
                feed='iex'  # or 'sip' for premium data
            )
        
        # Verify connection
        account = self.trading_client.get_account()
        logger.info(f"Connected to Alpaca - Account Status: {account.status}")
    
    async def _handle_quote(self, data):
        """Handle incoming quote data from stream"""
        try:
            quote_data = {
                'bid_price': float(data.bid_price) if data.bid_price else 0,
                'ask_price': float(data.ask_price) if data.ask_price else 0,
                'bid_size': data.bid_size,
                'ask_size': data.ask_size,
                'timestamp': data.timestamp
            }
            self.display_price_update(quote_data)
        except Exception as e:
            logger.error(f"Error handling quote: {e}")
    
    async def _handle_trade(self, data):
        """Handle incoming trade data from stream"""
        try:
            trade_data = {
                'price': float(data.price),
                'size': data.size,
                'timestamp': data.timestamp
            }
            # For trades, create a minimal quote
            quote_data = {
                'bid_price': float(data.price) - 0.01,
                'ask_price': float(data.price) + 0.01,
                'bid_size': 0,
                'ask_size': 0,
                'timestamp': data.timestamp
            }
            self.display_price_update(quote_data, trade_data)
        except Exception as e:
            logger.error(f"Error handling trade: {e}")
    
    def get_latest_quote(self):
        """Get the latest quote for TSLA (polling method)"""
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=self.symbol)
            quote = self.data_client.get_stock_latest_quote(request)
            
            if self.symbol in quote:
                quote_data = quote[self.symbol]
                return {
                    'bid_price': float(quote_data.bid_price) if quote_data.bid_price else 0,
                    'ask_price': float(quote_data.ask_price) if quote_data.ask_price else 0,
                    'bid_size': quote_data.bid_size,
                    'ask_size': quote_data.ask_size,
                    'timestamp': quote_data.timestamp
                }
            return None
        except Exception as e:
            logger.error(f"Error getting quote: {e}")
            return None
    
    def get_latest_trade(self):
        """Get the latest trade for TSLA"""
        try:
            request = StockLatestTradeRequest(symbol_or_symbols=self.symbol)
            trade = self.data_client.get_stock_latest_trade(request)
            
            if self.symbol in trade:
                trade_data = trade[self.symbol]
                return {
                    'price': float(trade_data.price),
                    'size': trade_data.size,
                    'timestamp': trade_data.timestamp
                }
            return None
        except Exception as e:
            logger.error(f"Error getting trade: {e}")
            return None
    
    def display_price_update(self, quote_data: dict, trade_data: Optional[dict] = None):
        """Display formatted price update in console"""
        timestamp = datetime.now(self.et)
        
        # Calculate spread
        bid = quote_data.get('bid_price', 0)
        ask = quote_data.get('ask_price', 0)
        spread = ask - bid if (ask and bid) else 0
        
        # Get last trade price
        last_price = trade_data['price'] if trade_data else (bid + ask) / 2 if (bid and ask) else 0
        
        # Calculate price change
        price_change = 0
        price_change_pct = 0
        color = Fore.WHITE
        
        if self.last_price and last_price:
            price_change = last_price - self.last_price
            price_change_pct = (price_change / self.last_price) * 100
            
            if price_change > 0:
                color = Fore.GREEN
                symbol = "▲"
            elif price_change < 0:
                color = Fore.RED
                symbol = "▼"
            else:
                color = Fore.YELLOW
                symbol = "="
        else:
            symbol = "•"
        
        # Clear line and display update
        print(f"\r{' ' * 100}", end='')  # Clear line
        print(f"\r{Fore.CYAN}[{timestamp.strftime('%H:%M:%S')}] "
              f"{Fore.WHITE}TSLA: "
              f"{color}${last_price:.2f} {symbol} "
              f"({price_change:+.2f}, {price_change_pct:+.2f}%) "
              f"{Fore.BLUE}Bid: ${bid:.2f} "
              f"{Fore.MAGENTA}Ask: ${ask:.2f} "
              f"{Fore.YELLOW}Spread: ${spread:.2f}", end='', flush=True)
        
        # Update last price
        self.last_price = last_price
        self.last_bid = bid
        self.last_ask = ask
        
        # Store in history
        self.price_history.append({
            'timestamp': timestamp,
            'last_price': last_price,
            'bid': bid,
            'ask': ask,
            'spread': spread,
            'bid_size': quote_data.get('bid_size', 0),
            'ask_size': quote_data.get('ask_size', 0),
            'trade_size': trade_data.get('size', 0) if trade_data else 0
        })
    
    def run_polling(self, interval=1.0, duration=None):
        """
        Run in polling mode
        
        Args:
            interval: Seconds between updates
            duration: Total seconds to run (None for infinite)
        """
        print(f"\n{Fore.GREEN}Starting TSLA real-time price tracker (Polling Mode)")
        print(f"{Fore.YELLOW}Update interval: {interval} seconds")
        print(f"{Fore.CYAN}Press Ctrl+C to stop\n")
        
        start_time = time.time()
        
        try:
            while True:
                # Get latest data
                quote = self.get_latest_quote()
                trade = self.get_latest_trade()
                
                if quote:
                    self.display_price_update(quote, trade)
                
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    break
                
                # Wait for next update
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Stopping price tracker...")
        finally:
            self._save_data_if_enabled()
            self._display_summary()
    
    async def run_streaming(self):
        """Run in streaming mode with WebSocket connection"""
        print(f"\n{Fore.GREEN}Starting TSLA real-time price tracker (Streaming Mode)")
        print(f"{Fore.YELLOW}Connecting to Alpaca WebSocket...")
        print(f"{Fore.CYAN}Press Ctrl+C to stop\n")
        
        # Track connection attempts
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Subscribe to TSLA quotes and trades with handler functions
                self.stream_client.subscribe_quotes(self._handle_quote, self.symbol)
                self.stream_client.subscribe_trades(self._handle_trade, self.symbol)
                
                print(f"{Fore.GREEN}✓ Subscribed to {self.symbol} real-time data")
                print(f"{Fore.YELLOW}Note: Live data is only available during market hours (9:30 AM - 4:00 PM ET)")
                print(f"{Fore.CYAN}Current time: {datetime.now(self.et).strftime('%I:%M %p ET')}\n")
                
                # Run the stream
                await self.stream_client._run_forever()
                break  # If successful, exit the retry loop
                
            except ValueError as e:
                if "connection limit exceeded" in str(e):
                    retry_count += 1
                    wait_time = 5 * retry_count  # Exponential backoff
                    print(f"\n{Fore.YELLOW}Connection limit exceeded. Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}Stopping price tracker...")
                break
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                print(f"\n{Fore.RED}Streaming error: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 5 * retry_count
                    print(f"{Fore.YELLOW}Retrying in {wait_time} seconds... (Attempt {retry_count}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"{Fore.RED}Max retries reached. Exiting.")
                    break
        
        # Cleanup
        try:
            if hasattr(self.stream_client, '_ws') and self.stream_client._ws:
                await self.stream_client._ws.close()
        except:
            pass
        
        self._save_data_if_enabled()
        self._display_summary()
    
    def enable_csv_logging(self, filename=None):
        """Enable saving price data to CSV"""
        self.save_to_csv = True
        if filename:
            self.csv_filename = filename
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.csv_filename = f"tsla_prices_{timestamp}.csv"
        print(f"{Fore.GREEN}CSV logging enabled: {self.csv_filename}")
    
    def _save_data_if_enabled(self):
        """Save collected data to CSV if enabled"""
        if self.save_to_csv and self.price_history:
            df = pd.DataFrame(self.price_history)
            df.to_csv(self.csv_filename, index=False)
            print(f"\n{Fore.GREEN}✓ Data saved to {self.csv_filename}")
            print(f"  {len(self.price_history)} price points recorded")
    
    def _display_summary(self):
        """Display summary statistics"""
        if not self.price_history:
            return
        
        df = pd.DataFrame(self.price_history)
        
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.WHITE}TSLA Trading Session Summary")
        print(f"{Fore.CYAN}{'='*50}")
        
        if 'last_price' in df.columns and len(df) > 0:
            print(f"{Fore.WHITE}Price Range: ${df['last_price'].min():.2f} - ${df['last_price'].max():.2f}")
            print(f"Average Price: ${df['last_price'].mean():.2f}")
            print(f"Average Spread: ${df['spread'].mean():.2f}")
            print(f"Total Updates: {len(df)}")
            
            # Calculate session change
            if len(df) > 1:
                session_change = df['last_price'].iloc[-1] - df['last_price'].iloc[0]
                session_change_pct = (session_change / df['last_price'].iloc[0]) * 100
                
                color = Fore.GREEN if session_change > 0 else Fore.RED
                print(f"Session Change: {color}{session_change:+.2f} ({session_change_pct:+.2f}%)")


def main():
    """Main function with example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TSLA Real-time Price Tracker')
    parser.add_argument('--mode', choices=['polling', 'streaming'], default='polling',
                       help='Data fetching mode (default: polling)')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='Update interval in seconds for polling mode (default: 1.0)')
    parser.add_argument('--duration', type=int, default=None,
                       help='Duration in seconds to run (default: infinite)')
    parser.add_argument('--save-csv', action='store_true',
                       help='Save price data to CSV file')
    parser.add_argument('--paper', action='store_true', default=True,
                       help='Use paper trading (default: True)')
    
    args = parser.parse_args()
    
    # Create tracker
    tracker = TSLARealtimeTracker(mode=args.mode, paper_trading=args.paper)
    
    # Enable CSV logging if requested
    if args.save_csv:
        tracker.enable_csv_logging()
    
    # Run based on mode
    if args.mode == 'polling':
        tracker.run_polling(interval=args.interval, duration=args.duration)
    else:
        # Run streaming mode
        try:
            asyncio.run(tracker.run_streaming())
        except Exception as e:
            print(f"{Fore.RED}Failed to run streaming: {e}")
            print(f"{Fore.YELLOW}Try using polling mode instead: --mode polling")


if __name__ == "__main__":
    main()
