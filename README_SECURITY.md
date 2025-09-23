# API Security Configuration

## Overview
This project uses Alpaca Markets API for trading data. API credentials are now securely stored in environment variables instead of being hardcoded in the source files.

## Setup Instructions

### 1. Environment Variables
The API credentials are stored in a `.env` file which is excluded from version control.

Create a `.env` file in the project root with the following structure:
```
ALPACA_API_KEY=your_api_key_here
ALPACA_API_SECRET=your_api_secret_here
```

### 2. Security Features Implemented
- ✅ API credentials moved to `.env` file
- ✅ `.env` file added to `.gitignore` (won't be committed to Git)
- ✅ All scripts updated to use environment variables
- ✅ Error handling added for missing credentials

### 3. Updated Files
The following files have been updated to use environment variables:
- `fetch_tsla_minute_data.py` - Fetches TSLA minute-level historical data
- `live.py` - Live data streaming
- `explore_alpaca_data.py` - Data exploration and visualization

### 4. Required Package
Make sure you have `python-dotenv` installed:
```bash
pip install python-dotenv
```

### 5. Important Security Notes
- **NEVER** commit the `.env` file to version control
- **NEVER** share your API credentials publicly
- Consider rotating your API keys periodically
- Use different API keys for development and production

### 6. Git Ignore Configuration
The `.gitignore` file has been updated to exclude:
- `.env` - Main environment file
- `*.env` - Any file ending with .env
- `.env.*` - Any environment-specific files (e.g., .env.local, .env.production)

### 7. If You've Already Exposed Your Keys
Since your API keys were previously exposed in the Git history:
1. **Immediately** regenerate your API keys in your Alpaca account
2. Update the new keys in your `.env` file
3. Consider using `git filter-branch` or BFG Repo-Cleaner to remove sensitive data from Git history

## Usage
All scripts will automatically load the environment variables from the `.env` file when run:
```bash
python fetch_tsla_minute_data.py
python live.py
python explore_alpaca_data.py
```

## Verification
To verify your environment variables are loaded correctly:
```python
from dotenv import load_dotenv
import os

load_dotenv()
print("API Key loaded:", "Yes" if os.getenv('ALPACA_API_KEY') else "No")
print("API Secret loaded:", "Yes" if os.getenv('ALPACA_API_SECRET') else "No")
