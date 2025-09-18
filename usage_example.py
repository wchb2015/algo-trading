"""
Usage Examples for Alpaca BarSet Exploration
==============================================

This file demonstrates how to explore and visualize your Alpaca BarSet data.
"""

from datetime import datetime, timedelta
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from explore_alpaca_data import explore_barset, create_visualizations

# If you already have a BarSet object named 'df' from your notebook:
# You can use it directly with the functions

def example_with_existing_barset(df):
    """
    Example using an existing BarSet object
    
    Args:
        df: Your existing alpaca.data.models.bars.BarSet object
    """
    print("=" * 60)
    print("EXAMPLE 1: Using existing BarSet")
    print("=" * 60)
    
    # Method 1: Access raw bars
    bars = df["AAPL"]  # Returns list of Bar objects
    print(f"\nYou have {len(bars)} bars for AAPL")
    
    # Method 2: Convert to pandas DataFrame (most useful)
    df_pandas = df.df
    print(f"\nDataFrame shape: {df_pandas.shape}")
    print("\nFirst few rows:")
    print(df_pandas.head())
    
    # Method 3: Access individual bar properties
    if bars:
        first_bar = bars[0]
        print(f"\nFirst bar date: {first_bar.timestamp}")
        print(f"First bar close: ${first_bar.close:.2f}")
        print(f"First bar volume: {first_bar.volume:,}")
    
    return df_pandas


def example_quick_exploration():
    """
    Quick exploration example
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Quick Exploration")
    print("=" * 60)
    
    # Setup (use your existing credentials)
    API_KEY = "PKJCOVJ8NBAT2HVHKCSC"
    API_SECRET = "dm3BAs0Xh0qdctMB6BPMZyqHPIphB7gdVUoUqNyN"
    
    data_client = StockHistoricalDataClient(API_KEY, API_SECRET)
    
    # Get historical data (avoiding recent data to prevent subscription issues)
    end_date = datetime.now() - timedelta(days=15)
    start_date = end_date - timedelta(days=30)
    
    request_params = StockBarsRequest(
        symbol_or_symbols=["AAPL"],
        timeframe=TimeFrame.Day,
        start=start_date,
        end=end_date
    )
    
    # Fetch data
    df = data_client.get_stock_bars(request_params)
    
    # Explore the data structure
    explore_barset(df, "AAPL")
    
    return df


def example_visualization():
    """
    Visualization example
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Creating Visualizations")
    print("=" * 60)
    
    # Get data
    API_KEY = "PKJCOVJ8NBAT2HVHKCSC"
    API_SECRET = "dm3BAs0Xh0qdctMB6BPMZyqHPIphB7gdVUoUqNyN"
    
    data_client = StockHistoricalDataClient(API_KEY, API_SECRET)
    
    end_date = datetime.now() - timedelta(days=15)
    start_date = end_date - timedelta(days=60)  # Get more data for better visualization
    
    request_params = StockBarsRequest(
        symbol_or_symbols=["AAPL"],
        timeframe=TimeFrame.Day,
        start=start_date,
        end=end_date
    )
    
    df = data_client.get_stock_bars(request_params)
    
    # Create visualizations
    print("\nCreating interactive and static visualizations...")
    create_visualizations(df, "AAPL")
    
    print("\n✅ Check the following files:")
    print("   - AAPL_interactive_analysis.html (open in browser)")
    print("   - AAPL_analysis_dashboard.png")
    
    return df


def example_data_manipulation():
    """
    Example of data manipulation and analysis
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Data Manipulation")
    print("=" * 60)
    
    import pandas as pd
    import numpy as np
    
    # Get data
    API_KEY = "PKJCOVJ8NBAT2HVHKCSC"
    API_SECRET = "dm3BAs0Xh0qdctMB6BPMZyqHPIphB7gdVUoUqNyN"
    
    data_client = StockHistoricalDataClient(API_KEY, API_SECRET)
    
    end_date = datetime.now() - timedelta(days=15)
    start_date = end_date - timedelta(days=30)
    
    request_params = StockBarsRequest(
        symbol_or_symbols=["AAPL"],
        timeframe=TimeFrame.Day,
        start=start_date,
        end=end_date
    )
    
    barset = data_client.get_stock_bars(request_params)
    
    # Convert to DataFrame
    df = barset.df
    
    # Handle multi-symbol DataFrames
    if isinstance(df.columns, pd.MultiIndex):
        aapl_df = df['AAPL'].copy()
    else:
        aapl_df = df.copy()
    
    # Calculate technical indicators
    print("\nCalculating technical indicators...")
    
    # Daily returns
    aapl_df['daily_return'] = aapl_df['close'].pct_change()
    
    # Moving averages
    aapl_df['MA_5'] = aapl_df['close'].rolling(window=5).mean()
    aapl_df['MA_20'] = aapl_df['close'].rolling(window=20).mean()
    
    # Bollinger Bands
    rolling_mean = aapl_df['close'].rolling(window=20).mean()
    rolling_std = aapl_df['close'].rolling(window=20).std()
    aapl_df['BB_upper'] = rolling_mean + (rolling_std * 2)
    aapl_df['BB_lower'] = rolling_mean - (rolling_std * 2)
    
    # RSI (Relative Strength Index)
    delta = aapl_df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    aapl_df['RSI'] = 100 - (100 / (1 + rs))
    
    # Display results
    print("\nLast 5 rows with indicators:")
    print(aapl_df[['close', 'MA_5', 'MA_20', 'RSI', 'daily_return']].tail())
    
    # Trading signals
    print("\nSimple Trading Signals:")
    
    # Golden Cross (MA5 crosses above MA20)
    aapl_df['signal'] = 0
    aapl_df.loc[aapl_df['MA_5'] > aapl_df['MA_20'], 'signal'] = 1
    aapl_df.loc[aapl_df['MA_5'] < aapl_df['MA_20'], 'signal'] = -1
    
    # Count signals
    buy_signals = (aapl_df['signal'] == 1).sum()
    sell_signals = (aapl_df['signal'] == -1).sum()
    
    print(f"  Buy signals (MA5 > MA20): {buy_signals}")
    print(f"  Sell signals (MA5 < MA20): {sell_signals}")
    
    # RSI signals
    oversold = (aapl_df['RSI'] < 30).sum()
    overbought = (aapl_df['RSI'] > 70).sum()
    
    print(f"  Oversold days (RSI < 30): {oversold}")
    print(f"  Overbought days (RSI > 70): {overbought}")
    
    return aapl_df


if __name__ == "__main__":
    print("Alpaca BarSet Exploration Examples")
    print("===================================\n")
    
    # Run examples
    try:
        # Example 2: Quick exploration
        df = example_quick_exploration()
        
        # Example 3: Visualization
        # Uncomment to run (will create files and show plots)
        # example_visualization()
        
        # Example 4: Data manipulation
        analyzed_df = example_data_manipulation()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: If you get subscription errors, try using older dates.")
