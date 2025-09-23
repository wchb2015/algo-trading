from alpaca.data.live import StockDataStream
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API credentials from environment variables
API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_API_SECRET')

if not API_KEY or not API_SECRET:
    raise ValueError("Please set ALPACA_API_KEY and ALPACA_API_SECRET in your .env file")
stream = StockDataStream(
    API_KEY,
    API_SECRET
)

async def handle_trade(data):
    print(data)

stream.subscribe_quotes(handle_trade, "SNAP")
stream.run()
