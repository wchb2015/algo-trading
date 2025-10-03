"""
Test script to verify Alpaca streaming API
"""

import os
import asyncio
from dotenv import load_dotenv
from alpaca.data.live import StockDataStream

# Load environment variables
load_dotenv()

async def quote_handler(data):
    """Handle quote updates"""
    print(f"Quote: {data.symbol} - Bid: ${data.bid_price:.2f} Ask: ${data.ask_price:.2f}")

async def trade_handler(data):
    """Handle trade updates"""
    print(f"Trade: {data.symbol} - Price: ${data.price:.2f} Size: {data.size}")

async def main():
    """Main async function"""
    # Get API credentials
    api_key = os.getenv('ALPACA_API_KEY')
    api_secret = os.getenv('ALPACA_API_SECRET')
    
    if not api_key or not api_secret:
        print("Please set ALPACA_API_KEY and ALPACA_API_SECRET in your .env file")
        return
    
    # Create stream client
    stream = StockDataStream(api_key, api_secret)
    
    # Subscribe to TSLA with handlers
    stream.subscribe_quotes(quote_handler, "TSLA")
    stream.subscribe_trades(trade_handler, "TSLA")
    
    print("Starting stream... Press Ctrl+C to stop")
    
    try:
        # Run the stream
        await stream.run()
    except KeyboardInterrupt:
        print("\nStopping stream...")
    finally:
        await stream.close()
        print("Stream closed")

if __name__ == "__main__":
    asyncio.run(main())
