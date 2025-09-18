"""
Alpaca BarSet Data Exploration and Visualization
This script provides comprehensive methods to explore and visualize Alpaca trading data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

def explore_barset(barset, symbol="AAPL"):
    """
    Explore the structure and content of an Alpaca BarSet object
    
    Args:
        barset: alpaca.data.models.bars.BarSet object
        symbol: Stock symbol to explore
    """
    print("=" * 60)
    print("ALPACA BARSET EXPLORATION")
    print("=" * 60)
    
    # 1. Basic Information
    print("\n1. BASIC INFORMATION:")
    print(f"   Type: {type(barset)}")
    print(f"   Available symbols: {list(barset.data.keys())}")
    
    # 2. Access raw data
    print("\n2. RAW DATA ACCESS:")
    bars_list = barset[symbol]
    print(f"   Number of bars for {symbol}: {len(bars_list)}")
    
    if bars_list:
        first_bar = bars_list[0]
        last_bar = bars_list[-1]
        print(f"   First bar timestamp: {first_bar.timestamp}")
        print(f"   Last bar timestamp: {last_bar.timestamp}")
        print(f"   Bar attributes: {dir(first_bar)}")
        
        # Sample bar details
        print(f"\n   Sample Bar (First):")
        print(f"   - Open: ${first_bar.open:.2f}")
        print(f"   - High: ${first_bar.high:.2f}")
        print(f"   - Low: ${first_bar.low:.2f}")
        print(f"   - Close: ${first_bar.close:.2f}")
        print(f"   - Volume: {first_bar.volume:,}")
        print(f"   - VWAP: ${first_bar.vwap:.2f}")
        print(f"   - Trade Count: {first_bar.trade_count:,}")
    
    # 3. Convert to DataFrame
    print("\n3. DATAFRAME CONVERSION:")
    df = barset.df
    print(f"   DataFrame shape: {df.shape}")
    print(f"   DataFrame columns: {list(df.columns)}")
    print(f"   Index type: {type(df.index)}")
    print(f"   Index name: {df.index.name}")
    
    # Display DataFrame info
    print("\n   DataFrame Info:")
    print(df.info())
    
    # Display first few rows
    print("\n   First 5 rows:")
    print(df.head())
    
    # 4. Statistical Summary
    print("\n4. STATISTICAL SUMMARY:")
    print(df.describe())
    
    # 5. Calculate additional metrics
    print("\n5. CALCULATED METRICS:")
    
    # For multi-symbol DataFrames, select the symbol
    if isinstance(df.columns, pd.MultiIndex):
        symbol_df = df[symbol]
    else:
        symbol_df = df
    
    # Daily returns
    symbol_df['daily_return'] = symbol_df['close'].pct_change()
    
    # Moving averages
    symbol_df['MA_5'] = symbol_df['close'].rolling(window=5).mean()
    symbol_df['MA_10'] = symbol_df['close'].rolling(window=10).mean()
    
    # Volatility (standard deviation of returns)
    volatility = symbol_df['daily_return'].std()
    
    print(f"   Average Close Price: ${symbol_df['close'].mean():.2f}")
    print(f"   Max Close Price: ${symbol_df['close'].max():.2f}")
    print(f"   Min Close Price: ${symbol_df['close'].min():.2f}")
    print(f"   Total Volume: {symbol_df['volume'].sum():,}")
    print(f"   Average Daily Volume: {symbol_df['volume'].mean():,.0f}")
    print(f"   Daily Return Volatility: {volatility:.4f} ({volatility*100:.2f}%)")
    print(f"   Total Return: {((symbol_df['close'].iloc[-1] / symbol_df['close'].iloc[0]) - 1) * 100:.2f}%")
    
    return df


def create_visualizations(barset, symbol="AAPL"):
    """
    Create comprehensive visualizations for Alpaca BarSet data
    
    Args:
        barset: alpaca.data.models.bars.BarSet object
        symbol: Stock symbol to visualize
    """
    # Convert to DataFrame
    df = barset.df
    
    # Handle multi-symbol DataFrames
    if isinstance(df.columns, pd.MultiIndex):
        symbol_df = df[symbol].copy()
    else:
        symbol_df = df.copy()
    
    # Calculate technical indicators
    symbol_df['MA_5'] = symbol_df['close'].rolling(window=5).mean()
    symbol_df['MA_20'] = symbol_df['close'].rolling(window=20).mean()
    symbol_df['daily_return'] = symbol_df['close'].pct_change()
    
    # Bollinger Bands
    rolling_mean = symbol_df['close'].rolling(window=20).mean()
    rolling_std = symbol_df['close'].rolling(window=20).std()
    symbol_df['BB_upper'] = rolling_mean + (rolling_std * 2)
    symbol_df['BB_lower'] = rolling_mean - (rolling_std * 2)
    
    # Reset index to have timestamp as a column
    symbol_df = symbol_df.reset_index()
    
    # 1. Interactive Candlestick Chart with Plotly
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{symbol} Stock Price', 'Volume', 'Daily Returns'),
        row_heights=[0.5, 0.2, 0.3]
    )
    
    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=symbol_df['timestamp'],
            open=symbol_df['open'],
            high=symbol_df['high'],
            low=symbol_df['low'],
            close=symbol_df['close'],
            name='OHLC'
        ),
        row=1, col=1
    )
    
    # Moving Averages
    fig.add_trace(
        go.Scatter(
            x=symbol_df['timestamp'],
            y=symbol_df['MA_5'],
            name='MA 5',
            line=dict(color='orange', width=1)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=symbol_df['timestamp'],
            y=symbol_df['MA_20'],
            name='MA 20',
            line=dict(color='blue', width=1)
        ),
        row=1, col=1
    )
    
    # Bollinger Bands
    fig.add_trace(
        go.Scatter(
            x=symbol_df['timestamp'],
            y=symbol_df['BB_upper'],
            name='BB Upper',
            line=dict(color='gray', width=0.5),
            opacity=0.3
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=symbol_df['timestamp'],
            y=symbol_df['BB_lower'],
            name='BB Lower',
            line=dict(color='gray', width=0.5),
            fill='tonexty',
            fillcolor='rgba(128, 128, 128, 0.1)',
            opacity=0.3
        ),
        row=1, col=1
    )
    
    # Volume
    colors = ['red' if row['close'] < row['open'] else 'green' 
              for _, row in symbol_df.iterrows()]
    
    fig.add_trace(
        go.Bar(
            x=symbol_df['timestamp'],
            y=symbol_df['volume'],
            name='Volume',
            marker_color=colors,
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Daily Returns
    return_colors = ['red' if r < 0 else 'green' for r in symbol_df['daily_return']]
    fig.add_trace(
        go.Bar(
            x=symbol_df['timestamp'],
            y=symbol_df['daily_return'] * 100,
            name='Daily Return %',
            marker_color=return_colors,
            showlegend=False
        ),
        row=3, col=1
    )
    
    # Update layout
    fig.update_layout(
        title=f'{symbol} Stock Analysis',
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
        hovermode='x unified'
    )
    
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="Return (%)", row=3, col=1)
    
    # Save interactive plot
    fig.write_html(f"{symbol}_interactive_analysis.html")
    print(f"\nInteractive chart saved as {symbol}_interactive_analysis.html")
    
    # 2. Static Matplotlib Visualizations
    fig2, axes = plt.subplots(4, 2, figsize=(15, 12))
    fig2.suptitle(f'{symbol} Stock Analysis Dashboard', fontsize=16)
    
    # Price and Moving Averages
    ax1 = axes[0, 0]
    ax1.plot(symbol_df['timestamp'], symbol_df['close'], label='Close Price', linewidth=2)
    ax1.plot(symbol_df['timestamp'], symbol_df['MA_5'], label='MA 5', alpha=0.7)
    ax1.plot(symbol_df['timestamp'], symbol_df['MA_20'], label='MA 20', alpha=0.7)
    ax1.fill_between(symbol_df['timestamp'], symbol_df['BB_lower'], symbol_df['BB_upper'], 
                     alpha=0.1, color='gray', label='Bollinger Bands')
    ax1.set_title('Price with Technical Indicators')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Volume
    ax2 = axes[0, 1]
    ax2.bar(symbol_df['timestamp'], symbol_df['volume'], color=colors, alpha=0.7)
    ax2.set_title('Trading Volume')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Volume')
    ax2.grid(True, alpha=0.3)
    
    # Daily Returns Distribution
    ax3 = axes[1, 0]
    returns = symbol_df['daily_return'].dropna()
    ax3.hist(returns * 100, bins=30, edgecolor='black', alpha=0.7)
    ax3.axvline(x=0, color='red', linestyle='--', alpha=0.5)
    ax3.set_title('Daily Returns Distribution')
    ax3.set_xlabel('Return (%)')
    ax3.set_ylabel('Frequency')
    ax3.grid(True, alpha=0.3)
    
    # Add statistics text
    mean_return = returns.mean() * 100
    std_return = returns.std() * 100
    ax3.text(0.05, 0.95, f'Mean: {mean_return:.3f}%\nStd: {std_return:.3f}%', 
             transform=ax3.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Cumulative Returns
    ax4 = axes[1, 1]
    cumulative_returns = (1 + returns).cumprod() - 1
    ax4.plot(symbol_df['timestamp'][1:], cumulative_returns * 100, linewidth=2)
    ax4.set_title('Cumulative Returns')
    ax4.set_xlabel('Date')
    ax4.set_ylabel('Cumulative Return (%)')
    ax4.grid(True, alpha=0.3)
    
    # Price vs Volume Scatter
    ax5 = axes[2, 0]
    scatter = ax5.scatter(symbol_df['volume'], symbol_df['close'], 
                         c=range(len(symbol_df)), cmap='viridis', alpha=0.6)
    ax5.set_title('Price vs Volume Relationship')
    ax5.set_xlabel('Volume')
    ax5.set_ylabel('Price ($)')
    plt.colorbar(scatter, ax=ax5, label='Time')
    ax5.grid(True, alpha=0.3)
    
    # VWAP vs Close Price
    ax6 = axes[2, 1]
    ax6.plot(symbol_df['timestamp'], symbol_df['close'], label='Close', alpha=0.7)
    ax6.plot(symbol_df['timestamp'], symbol_df['vwap'], label='VWAP', alpha=0.7)
    ax6.set_title('Close Price vs VWAP')
    ax6.set_xlabel('Date')
    ax6.set_ylabel('Price ($)')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    # High-Low Spread
    ax7 = axes[3, 0]
    spread = symbol_df['high'] - symbol_df['low']
    ax7.plot(symbol_df['timestamp'], spread, linewidth=1, color='purple')
    ax7.fill_between(symbol_df['timestamp'], 0, spread, alpha=0.3, color='purple')
    ax7.set_title('Daily High-Low Spread')
    ax7.set_xlabel('Date')
    ax7.set_ylabel('Spread ($)')
    ax7.grid(True, alpha=0.3)
    
    # Trade Count
    ax8 = axes[3, 1]
    ax8.plot(symbol_df['timestamp'], symbol_df['trade_count'], linewidth=1, color='brown')
    ax8.set_title('Number of Trades per Day')
    ax8.set_xlabel('Date')
    ax8.set_ylabel('Trade Count')
    ax8.grid(True, alpha=0.3)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(f'{symbol}_analysis_dashboard.png', dpi=100, bbox_inches='tight')
    print(f"Static dashboard saved as {symbol}_analysis_dashboard.png")
    
    plt.show()
    
    return fig, fig2


def main():
    """
    Main function to demonstrate usage
    """
    # API credentials (replace with your own)
    API_KEY = "PKJCOVJ8NBAT2HVHKCSC"
    API_SECRET = "dm3BAs0Xh0qdctMB6BPMZyqHPIphB7gdVUoUqNyN"
    
    # Initialize client
    data_client = StockHistoricalDataClient(API_KEY, API_SECRET)
    
    # Request parameters
    request_params = StockBarsRequest(
        symbol_or_symbols=["AAPL"],
        timeframe=TimeFrame.Day,
        start=datetime(2025, 8, 1),
        end=datetime(2025, 8, 31)
    )
    
    # Get data
    barset = data_client.get_stock_bars(request_params)
    
    # Explore the data
    df = explore_barset(barset, "AAPL")
    
    # Create visualizations
    create_visualizations(barset, "AAPL")
    
    return barset, df


if __name__ == "__main__":
    barset, df = main()
