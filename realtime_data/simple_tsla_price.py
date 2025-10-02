"""
Simple TSLA Real-time Price Fetcher
A minimal example for getting real-time TSLA stock prices
"""

import os
import time
from datetime import datetime
import pytz
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockLatestTradeRequest

# Load environment variables
load_dotenv()

def get_tsla_price():
    """Get current TSLA price from Alpaca API"""
    
    # Get API credentials
    api_key = os.getenv('ALPACA_API_KEY')
    api_secret = os.getenv('ALPACA_API_SECRET')
    
    if not api_key or not api_secret:
        print("Error: Please set ALPACA_API_KEY and ALPACA_API_SECRET in your .env file")
        return None
    
    # Create data client
    client = StockHistoricalDataClient(api_key, api_secret)
    
    try:
        # Get latest quote
        quote_request = StockLatestQuoteRequest(symbol_or_symbols="TSLA")
        quote = client.get_stock_latest_quote(quote_request)
        
        # Get latest trade
        trade_request = StockLatestTradeRequest(symbol_or_symbols="TSLA")
        trade = client.get_stock_latest_trade(trade_request)
        
        if "TSLA" in quote and "TSLA" in trade:
            quote_data = quote["TSLA"]
            trade_data = trade["TSLA"]
            
            # Extract prices
            bid_price = float(quote_data.bid_price) if quote_data.bid_price else 0
            ask_price = float(quote_data.ask_price) if quote_data.ask_price else 0
            last_price = float(trade_data.price) if trade_data.price else 0
            
            # Calculate spread
            spread = ask_price - bid_price if (ask_price and bid_price) else 0
            
            return {
                'timestamp': datetime.now(pytz.timezone('America/New_York')),
                'last_price': last_price,
                'bid': bid_price,
                'ask': ask_price,
                'spread': spread,
                'bid_size': quote_data.bid_size,
                'ask_size': quote_data.ask_size,
                'trade_size': trade_data.size
            }
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    
    return None


def display_price(price_data):
    """Display price data in a formatted way"""
    if not price_data:
        print("No price data available")
        return
    
    print(f"\n{'='*50}")
    print(f"TSLA Real-time Price Update")
    print(f"Time: {price_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"{'='*50}")
    print(f"Last Trade:  ${price_data['last_price']:.2f} ({price_data['trade_size']} shares)")
    print(f"Bid:         ${price_data['bid']:.2f} ({price_data['bid_size']} shares)")
    print(f"Ask:         ${price_data['ask']:.2f} ({price_data['ask_size']} shares)")
    print(f"Spread:      ${price_data['spread']:.2f}")
    print(f"{'='*50}")


def run_continuous(interval=1):
    """Run continuous price updates"""
    print(f"Starting TSLA real-time price monitor...")
    print(f"Update interval: {interval} second(s)")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            price_data = get_tsla_price()
            
            if price_data:
                # Clear screen for cleaner display (optional)
                # os.system('clear' if os.name == 'posix' else 'cls')
                
                # Display inline update
                timestamp = price_data['timestamp'].strftime('%H:%M:%S')
                print(f"\r[{timestamp}] TSLA: ${price_data['last_price']:.2f} | "
                      f"Bid: ${price_data['bid']:.2f} | "
                      f"Ask: ${price_data['ask']:.2f} | "
                      f"Spread: ${price_data['spread']:.2f}", end='', flush=True)
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n\nStopped by user")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        # Run continuous updates
        interval = float(sys.argv[2]) if len(sys.argv) > 2 else 1
        run_continuous(interval)
    else:
        # Get single price update
        print("Fetching TSLA price...")
        price_data = get_tsla_price()
        display_price(price_data)
        
        print("\nTip: Run with --continuous for real-time updates")
        print("Example: python simple_tsla_price.py --continuous 1")
