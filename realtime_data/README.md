# TSLA Real-time Stock Price Tracker

This folder contains implementations for fetching real-time TSLA stock prices using the Alpaca API.

## Features

- **Real-time price updates** for TSLA stock
- **Two modes of operation**:
  - **Polling Mode**: Fetches prices at regular intervals
  - **Streaming Mode**: WebSocket connection for true real-time updates
- **Colored console output** for better visualization
- **Price change tracking** with percentage calculations
- **CSV export** option for data analysis
- **Summary statistics** at the end of session

## Files

1. **`tsla_realtime.py`** - Full-featured real-time tracker with both polling and streaming modes
2. **`simple_tsla_price.py`** - Simplified version for quick price checks
3. **`requirements.txt`** - Required Python packages

## Prerequisites

1. **Alpaca API Account**: You need an Alpaca account (paper trading is fine)
2. **API Credentials**: Already configured in the parent directory's `.env` file:
   ```
   ALPACA_API_KEY=your_api_key
   ALPACA_API_SECRET=your_api_secret
   ```

## Installation

Install the required packages:

```bash
pip install -r realtime_data/requirements.txt
```

## Usage

### Simple Price Check

Get a single TSLA price update:

```bash
python realtime_data/simple_tsla_price.py
```

Run continuous updates (updates every second):

```bash
python realtime_data/simple_tsla_price.py --continuous
```

Specify custom interval (e.g., every 2 seconds):

```bash
python realtime_data/simple_tsla_price.py --continuous 2
```

### Advanced Real-time Tracker

#### Polling Mode (Default)

Basic usage with 1-second updates:

```bash
python realtime_data/tsla_realtime.py
```

Custom interval (e.g., 0.5 seconds):

```bash
python realtime_data/tsla_realtime.py --interval 0.5
```

Run for specific duration (e.g., 60 seconds):

```bash
python realtime_data/tsla_realtime.py --duration 60
```

Save data to CSV:

```bash
python realtime_data/tsla_realtime.py --save-csv
```

#### Streaming Mode (WebSocket)

For true real-time updates via WebSocket:

```bash
python realtime_data/tsla_realtime.py --mode streaming
```

With CSV logging:

```bash
python realtime_data/tsla_realtime.py --mode streaming --save-csv
```

## Command Line Options

### `tsla_realtime.py` Options

- `--mode {polling,streaming}`: Choose data fetching mode (default: polling)
- `--interval FLOAT`: Update interval in seconds for polling mode (default: 1.0)
- `--duration INT`: Duration in seconds to run (default: infinite)
- `--save-csv`: Save price data to CSV file
- `--paper`: Use paper trading (default: True)

### `simple_tsla_price.py` Options

- `--continuous [INTERVAL]`: Run continuous updates with optional interval

## Output Format

### Console Display

The tracker displays real-time updates with:
- Timestamp
- Current price with direction indicator (▲ ▼ =)
- Price change (absolute and percentage)
- Bid/Ask prices
- Spread

Example:
```
[10:30:45] TSLA: $245.67 ▲ (+1.23, +0.50%) Bid: $245.65 Ask: $245.69 Spread: $0.04
```

### CSV Export

When `--save-csv` is used, data is saved with columns:
- timestamp
- last_price
- bid
- ask
- spread
- bid_size
- ask_size
- trade_size

## Features Explained

### Polling Mode
- Fetches latest quote and trade data at specified intervals
- Good for most use cases
- Lower resource usage
- Configurable update frequency

### Streaming Mode
- Establishes WebSocket connection to Alpaca
- Receives push notifications on price changes
- True real-time updates
- Best for high-frequency monitoring

### Price Tracking
- Tracks price changes between updates
- Calculates percentage changes
- Color-coded output (green for up, red for down)
- Maintains session statistics

### Data Export
- Optional CSV logging for further analysis
- Timestamped filenames
- All price points recorded
- Can be imported into Excel or analysis tools

## Market Hours

The tracker works during:
- **Regular Market Hours**: 9:30 AM - 4:00 PM ET (6:30 AM - 1:00 PM PT)
- **Pre-market**: 4:00 AM - 9:30 AM ET (1:00 AM - 6:30 AM PT)
- **After-hours**: 4:00 PM - 8:00 PM ET (1:00 PM - 5:00 PM PT)

Note: Data availability depends on your Alpaca subscription level.

## Troubleshooting

1. **No data received**: 
   - Check if market is open
   - Verify API credentials in `.env` file
   - Ensure you have market data subscription

2. **Connection errors**:
   - Check internet connection
   - Verify Alpaca API status
   - Try paper trading endpoint

3. **Import errors**:
   - Install requirements: `pip install -r realtime_data/requirements.txt`
   - Check Python version (3.7+ required)

## Examples

### Monitor TSLA for 5 minutes with CSV export

```bash
python realtime_data/tsla_realtime.py --duration 300 --save-csv
```

### High-frequency monitoring (0.5 second updates)

```bash
python realtime_data/tsla_realtime.py --interval 0.5
```

### Stream mode with data logging

```bash
python realtime_data/tsla_realtime.py --mode streaming --save-csv
```

## Notes

- The tracker uses paper trading endpoints by default
- Bid/Ask prices may be 0 outside regular market hours
- Streaming mode requires stable internet connection
- CSV files are saved in the `realtime_data` folder
- Press `Ctrl+C` to stop the tracker gracefully

## API Rate Limits

Alpaca has rate limits:
- **Historical Data**: 200 requests per minute
- **Streaming**: No specific limit for subscriptions

The polling mode respects these limits with default settings.

## Future Enhancements

Potential improvements:
- Multiple symbol support
- Technical indicators (moving averages, RSI)
- Alert system for price thresholds
- Database storage option
- Web dashboard interface
- Historical comparison charts
