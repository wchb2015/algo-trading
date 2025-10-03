"""
Fixed TSLA Real-time Streaming with Alpaca
Works with the current alpaca-py library
"""

import os
import asyncio
from datetime import datetime
import pytz
from dotenv import load_dotenv
from alpaca.data.live import StockDataStream
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

class TSLAStreamTracker:
    def __init__(self):
        self.symbol = "TSLA"
        self.last_price = None
        self.et = pytz.timezone('America/New_York')
        
        # Get API credentials
        api_key = os.getenv('ALPACA_API_KEY')
        api_secret = os.getenv('ALPACA_API_SECRET')
        
        if not api_key or not api_secret:
            raise ValueError("Please set ALPACA_API_KEY and ALPACA_API_SECRET in your .env file")
        
        # Create stream client
        self.stream = StockDataStream(api_key, api_secret)
        
    async def handle_quote(self, data):
        """Handle incoming quote data"""
        timestamp = datetime.now(self.et)
        bid = float(data.bid_price) if data.bid_price else 0
        ask = float(data.ask_price) if data.ask_price else 0
        spread = ask - bid if (ask and bid) else 0
        
        # Display quote
        print(f"{Fore.CYAN}[{timestamp.strftime('%H:%M:%S')}] "
              f"{Fore.WHITE}TSLA Quote: "
              f"{Fore.BLUE}Bid: ${bid:.2f} "
              f"{Fore.MAGENTA}Ask: ${ask:.2f} "
              f"{Fore.YELLOW}Spread: ${spread:.2f}")
    
    async def handle_trade(self, data):
        """Handle incoming trade data"""
        timestamp = datetime.now(self.et)
        price = float(data.price)
        size = data.size
        
        # Calculate price change
        if self.last_price:
            change = price - self.last_price
            change_pct = (change / self.last_price) * 100
            
            if change > 0:
                color = Fore.GREEN
                symbol = "▲"
            elif change < 0:
                color = Fore.RED
                symbol = "▼"
            else:
                color = Fore.YELLOW
                symbol = "="
            
            change_str = f"{color}{symbol} ({change:+.2f}, {change_pct:+.2f}%)"
        else:
            change_str = ""
        
        # Display trade
        print(f"{Fore.CYAN}[{timestamp.strftime('%H:%M:%S')}] "
              f"{Fore.WHITE}TSLA Trade: "
              f"{Fore.GREEN}${price:.2f} "
              f"{Fore.WHITE}Size: {size} "
              f"{change_str}")
        
        self.last_price = price
    
    async def run(self):
        """Run the streaming tracker"""
        print(f"\n{Fore.GREEN}Starting TSLA Real-time Streaming")
        print(f"{Fore.YELLOW}Connecting to Alpaca WebSocket...")
        print(f"{Fore.CYAN}Press Ctrl+C to stop\n")
        
        # Subscribe to TSLA data
        self.stream.subscribe_quotes(self.handle_quote, self.symbol)
        self.stream.subscribe_trades(self.handle_trade, self.symbol)
        
        print(f"{Fore.GREEN}✓ Subscribed to {self.symbol} real-time data\n")
        
        try:
            # Use _run_forever directly instead of run()
            await self.stream._run_forever()
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Stopping stream...")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}")
        finally:
            if hasattr(self.stream, '_ws') and self.stream._ws:
                await self.stream._ws.close()
            print(f"{Fore.GREEN}Stream closed")

async def main():
    """Main function"""
    tracker = TSLAStreamTracker()
    await tracker.run()

if __name__ == "__main__":
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Program terminated by user")
