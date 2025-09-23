"""
Fetch TSLA minute-level historical data during market hours only
Date Range: August 1-31, 2025
Market Hours: 6:30 AM - 1:00 PM PDT (9:30 AM - 4:00 PM ET)
"""

import pandas as pd
from datetime import datetime, timedelta
import pytz
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API credentials from environment variables
API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_API_SECRET')

if not API_KEY or not API_SECRET:
    raise ValueError("Please set ALPACA_API_KEY and ALPACA_API_SECRET in your .env file")

def fetch_tsla_minute_data():
    """
    Fetch TSLA minute-level data for August 2025 during market hours only
    """
    print("Initializing Alpaca client...")
    client = StockHistoricalDataClient(API_KEY, API_SECRET)
    
    # Define time zones
    et_tz = pytz.timezone('US/Eastern')
    pdt_tz = pytz.timezone('US/Pacific')
    
    # Date range for August 2025
    start_date = datetime(2025, 8, 1)
    end_date = datetime(2025, 8, 31, 23, 59, 59)
    
    print(f"Fetching TSLA minute data from {start_date.date()} to {end_date.date()}...")
    
    # Initialize list to store all data
    all_data = []
    
    # Fetch data in chunks (Alpaca has limits on data per request)
    current_date = start_date
    
    while current_date <= end_date:
        # Process one week at a time to avoid API limits
        chunk_end = min(current_date + timedelta(days=7), end_date)
        
        print(f"Fetching data from {current_date.date()} to {chunk_end.date()}...")
        
        try:
            # Create request for minute bars
            request_params = StockBarsRequest(
                symbol_or_symbols=["TSLA"],
                timeframe=TimeFrame.Minute,
                start=current_date,
                end=chunk_end
            )
            
            # Get the data
            bars = client.get_stock_bars(request_params)
            
            # Convert to DataFrame
            df = bars.df
            
            # Handle multi-index columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df = df["TSLA"]
            
            # Reset index to get timestamp as a column
            df = df.reset_index()
            
            # Process each bar
            for _, row in df.iterrows():
                # Convert timestamp to ET first (Alpaca returns UTC)
                timestamp_utc = row['timestamp']
                if timestamp_utc.tzinfo is None:
                    timestamp_utc = pytz.UTC.localize(timestamp_utc)
                else:
                    timestamp_utc = timestamp_utc.astimezone(pytz.UTC)
                
                # Convert to Eastern Time
                timestamp_et = timestamp_utc.astimezone(et_tz)
                
                # Check if it's during market hours (9:30 AM - 4:00 PM ET)
                market_open = timestamp_et.replace(hour=9, minute=30, second=0, microsecond=0)
                market_close = timestamp_et.replace(hour=16, minute=0, second=0, microsecond=0)
                
                if market_open <= timestamp_et < market_close:
                    # Convert to PDT for output
                    timestamp_pdt = timestamp_utc.astimezone(pdt_tz)
                    
                    # Add to our data list
                    all_data.append({
                        'ticker': 'TSLA',
                        'time': timestamp_pdt.strftime('%Y-%m-%d %H:%M:%S'),
                        'open': row['open'],
                        'close': row['close'],
                        'high': row['high'],
                        'low': row['low'],
                        'vwap': row['vwap']
                    })
            
            print(f"  Processed {len(df)} bars, kept {len(all_data)} market hours bars so far")
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error fetching data for {current_date.date()}: {e}")
        
        # Move to next chunk
        current_date = chunk_end + timedelta(seconds=1)
    
    # Create DataFrame from all collected data
    result_df = pd.DataFrame(all_data)
    
    # Save to CSV
    output_file = 'tsla_minute_data_august_2025.csv'
    result_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Data saved to {output_file}")
    print(f"Total records: {len(result_df)}")
    
    # Display sample of the data
    print("\nFirst 5 rows:")
    print(result_df.head())
    print("\nLast 5 rows:")
    print(result_df.tail())
    
    # Calculate some statistics
    if len(result_df) > 0:
        print("\n📊 Statistics:")
        print(f"Date range: {result_df['time'].min()} to {result_df['time'].max()}")
        print(f"Average close price: ${result_df['close'].mean():.2f}")
        print(f"Min close price: ${result_df['close'].min():.2f}")
        print(f"Max close price: ${result_df['close'].max():.2f}")
        print(f"Average VWAP: ${result_df['vwap'].mean():.2f}")
    
    return result_df

if __name__ == "__main__":
    df = fetch_tsla_minute_data()
