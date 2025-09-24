"""
Quick script to display the key results from TSLA ATR analysis
Using correct ATR calculation: High - Low
Using moving median instead of moving average
"""

import pandas as pd
import numpy as np

# Load the TSLA minute data
df = pd.read_csv('tsla_minute_data_august_2025.csv')
df['time'] = pd.to_datetime(df['time'])
df['date'] = df['time'].dt.date

# Calculate daily prices
daily_prices = df.groupby('date').agg({
    'open': 'first',
    'close': 'last',
    'high': 'max',
    'low': 'min'
}).reset_index()

daily_prices.columns = ['date', 'daily_open', 'daily_close', 'daily_high', 'daily_low']

# Calculate intraday ATR (High - Low)
daily_prices['intraday_atr'] = daily_prices['daily_high'] - daily_prices['daily_low']

# Calculate 20-day moving median
daily_prices['atr_median20'] = daily_prices['intraday_atr'].rolling(window=20, min_periods=1).median()

# Also calculate moving average for comparison
daily_prices['atr_ma20'] = daily_prices['intraday_atr'].rolling(window=20, min_periods=1).mean()

# Calculate ATR as percentage
daily_prices['atr_pct'] = (daily_prices['intraday_atr'] / daily_prices['daily_close']) * 100

# Display results
print("=" * 60)
print("TSLA INTRADAY ATR ANALYSIS - KEY RESULTS")
print("(Using correct ATR: High - Low)")
print("=" * 60)
print(f"\nData Period: August 2025")
print(f"Total Trading Days: {len(daily_prices)}")

print("\n📊 DAILY ATR STATISTICS (High - Low):")
print(f"  Mean ATR: ${daily_prices['intraday_atr'].mean():.2f}")
print(f"  Median ATR: ${daily_prices['intraday_atr'].median():.2f}")
print(f"  Max ATR: ${daily_prices['intraday_atr'].max():.2f}")
print(f"  Min ATR: ${daily_prices['intraday_atr'].min():.2f}")
print(f"  Std Dev: ${daily_prices['intraday_atr'].std():.2f}")

print("\n📈 20-DAY MOVING MEDIAN ATR:")
print(f"  Current (Last Day): ${daily_prices['atr_median20'].iloc[-1]:.2f}")
print(f"  Average of Medians: ${daily_prices['atr_median20'].mean():.2f}")
print(f"  Max: ${daily_prices['atr_median20'].max():.2f}")
print(f"  Min: ${daily_prices['atr_median20'].min():.2f}")

print("\n📊 COMPARISON: MEDIAN vs MEAN:")
print(f"  20-Day Moving Median (Last): ${daily_prices['atr_median20'].iloc[-1]:.2f}")
print(f"  20-Day Moving Average (Last): ${daily_prices['atr_ma20'].iloc[-1]:.2f}")
print(f"  Difference: ${abs(daily_prices['atr_median20'].iloc[-1] - daily_prices['atr_ma20'].iloc[-1]):.2f}")

print("\n📅 LAST 5 DAYS DETAIL:")
print("-" * 70)
print(f"{'Date':<12} {'High':<8} {'Low':<8} {'ATR':<8} {'ATR%':<8} {'20-Median':<10}")
print("-" * 70)
for _, row in daily_prices.tail(5).iterrows():
    print(f"{str(row['date']):<12} ${row['daily_high']:<7.2f} ${row['daily_low']:<7.2f} ${row['intraday_atr']:<7.2f} {row['atr_pct']:<7.2f}% ${row['atr_median20']:<9.2f}")

# Volatility analysis
avg_price = daily_prices['daily_close'].mean()
atr_pct_mean = daily_prices['atr_pct'].mean()

print("\n💡 VOLATILITY INSIGHTS:")
print(f"  ATR as % of Average Price: {atr_pct_mean:.2f}%")
print(f"  Days with ATR > $15: {len(daily_prices[daily_prices['intraday_atr'] > 15])} ({len(daily_prices[daily_prices['intraday_atr'] > 15])/len(daily_prices)*100:.1f}%)")
print(f"  Days with ATR > $20: {len(daily_prices[daily_prices['intraday_atr'] > 20])} ({len(daily_prices[daily_prices['intraday_atr'] > 20])/len(daily_prices)*100:.1f}%)")
print(f"  Days with ATR > $25: {len(daily_prices[daily_prices['intraday_atr'] > 25])} ({len(daily_prices[daily_prices['intraday_atr'] > 25])/len(daily_prices)*100:.1f}%)")

# Compare with open-close range
daily_prices['open_close_range'] = abs(daily_prices['daily_close'] - daily_prices['daily_open'])
print("\n📐 ATR vs OPEN-CLOSE RANGE:")
print(f"  Mean ATR (High-Low): ${daily_prices['intraday_atr'].mean():.2f}")
print(f"  Mean Open-Close Range: ${daily_prices['open_close_range'].mean():.2f}")
print(f"  Ratio (ATR/Open-Close): {daily_prices['intraday_atr'].mean() / daily_prices['open_close_range'].mean():.2f}x")

print("\n" + "=" * 60)
print("Analysis complete! Check 'tsla_intraday_atr_analysis.ipynb' for")
print("detailed visualizations and full results.")
print("=" * 60)
