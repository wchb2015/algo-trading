"""
Verify and analyze the fetched TSLA minute data
"""

import pandas as pd
from datetime import datetime

def verify_tsla_data():
    """
    Verify the TSLA minute data CSV file
    """
    # Read the CSV file
    df = pd.read_csv('tsla_minute_data_august_2025.csv')
    
    print("=" * 60)
    print("TSLA MINUTE DATA VERIFICATION")
    print("=" * 60)
    
    # Basic info
    print(f"\n📊 Data Overview:")
    print(f"Total records: {len(df):,}")
    print(f"Columns: {', '.join(df.columns)}")
    
    # Convert time to datetime for analysis
    df['time'] = pd.to_datetime(df['time'])
    
    # Date range
    print(f"\n📅 Date Range:")
    print(f"Start: {df['time'].min()}")
    print(f"End: {df['time'].max()}")
    
    # Extract hour from time for market hours verification
    df['hour'] = df['time'].dt.hour
    df['minute'] = df['time'].dt.minute
    
    # Check market hours (should be 6:30 AM - 1:00 PM PDT)
    print(f"\n⏰ Market Hours Check (PDT):")
    print(f"Earliest time in day: {df['hour'].min()}:{df['minute'][df['hour'] == df['hour'].min()].min():02d}")
    print(f"Latest time in day: {df['hour'].max()}:{df['minute'][df['hour'] == df['hour'].max()].max():02d}")
    
    # Trading days
    df['date'] = df['time'].dt.date
    unique_dates = df['date'].unique()
    print(f"\n📆 Trading Days:")
    print(f"Total trading days: {len(unique_dates)}")
    print(f"Average bars per day: {len(df) / len(unique_dates):.0f}")
    
    # Price statistics
    print(f"\n💰 Price Statistics:")
    print(f"Open  - Min: ${df['open'].min():.2f}, Max: ${df['open'].max():.2f}, Avg: ${df['open'].mean():.2f}")
    print(f"Close - Min: ${df['close'].min():.2f}, Max: ${df['close'].max():.2f}, Avg: ${df['close'].mean():.2f}")
    print(f"High  - Min: ${df['high'].min():.2f}, Max: ${df['high'].max():.2f}, Avg: ${df['high'].mean():.2f}")
    print(f"Low   - Min: ${df['low'].min():.2f}, Max: ${df['low'].max():.2f}, Avg: ${df['low'].mean():.2f}")
    print(f"VWAP  - Min: ${df['vwap'].min():.2f}, Max: ${df['vwap'].max():.2f}, Avg: ${df['vwap'].mean():.2f}")
    
    # Data quality checks
    print(f"\n✅ Data Quality Checks:")
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("✓ No missing values")
    else:
        print("✗ Missing values found:")
        print(missing[missing > 0])
    
    # Check if high >= low
    invalid_hl = df[df['high'] < df['low']]
    if len(invalid_hl) == 0:
        print("✓ All high prices >= low prices")
    else:
        print(f"✗ {len(invalid_hl)} rows where high < low")
    
    # Check if high >= open and close
    invalid_high = df[(df['high'] < df['open']) | (df['high'] < df['close'])]
    if len(invalid_high) == 0:
        print("✓ All high prices >= open and close prices")
    else:
        print(f"✗ {len(invalid_high)} rows where high < open or close")
    
    # Check if low <= open and close
    invalid_low = df[(df['low'] > df['open']) | (df['low'] > df['close'])]
    if len(invalid_low) == 0:
        print("✓ All low prices <= open and close prices")
    else:
        print(f"✗ {len(invalid_low)} rows where low > open or close")
    
    # Sample data
    print(f"\n📝 Sample Data (first 3 and last 3 rows):")
    print("\nFirst 3 rows:")
    print(df[['ticker', 'time', 'open', 'close', 'high', 'low', 'vwap']].head(3).to_string(index=False))
    print("\nLast 3 rows:")
    print(df[['ticker', 'time', 'open', 'close', 'high', 'low', 'vwap']].tail(3).to_string(index=False))
    
    print("\n" + "=" * 60)
    print("✅ Data verification complete!")
    print("=" * 60)
    
    return df

if __name__ == "__main__":
    df = verify_tsla_data()
