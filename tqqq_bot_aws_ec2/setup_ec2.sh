#!/bin/bash

# TQQQ/SQQQ Trading Bot - AWS EC2 Setup Script
# This script sets up the trading bot on an Amazon Linux 2023 EC2 instance

set -e  # Exit on error

echo "============================================"
echo "TQQQ/SQQQ Trading Bot - EC2 Setup"
echo "For Amazon Linux 2023"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Detect Amazon Linux version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$NAME" == "Amazon Linux" ]]; then
        print_status "Detected Amazon Linux $VERSION"
    else
        print_warning "This script is optimized for Amazon Linux. Detected: $NAME $VERSION"
    fi
fi

# Update system
print_status "Updating system packages..."
sudo dnf update -y
sudo dnf upgrade -y

# Install Python 3.9+ if not present
print_status "Installing Python and development tools..."
sudo dnf install -y python3 python3-pip python3-devel

# Install system dependencies
print_status "Installing system dependencies..."
sudo dnf install -y \
    git \
    curl \
    wget \
    gcc \
    gcc-c++ \
    make \
    openssl-devel \
    libffi-devel \
    chrony  # For time synchronization

# Configure timezone to PDT/PST
print_status "Setting timezone to America/Los_Angeles (PDT/PST)..."
sudo timedatectl set-timezone America/Los_Angeles
echo "Current time: $(date)"

# Ensure time synchronization
print_status "Configuring time synchronization..."
sudo systemctl enable chronyd
sudo systemctl start chronyd
sudo chronyc sources

# Create bot directory if it doesn't exist
BOT_DIR="/home/ec2-user/tqqq_bot_aws_ec2"
if [ ! -d "$BOT_DIR" ]; then
    print_status "Creating bot directory..."
    mkdir -p "$BOT_DIR"
fi

# Navigate to bot directory
cd "$BOT_DIR"

# Create Python virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python requirements
if [ -f "requirements.txt" ]; then
    print_status "Installing Python requirements..."
    pip install -r requirements.txt
else
    print_warning "requirements.txt not found. Installing basic packages..."
    pip install \
        alpaca-py \
        pandas \
        numpy \
        pytz \
        python-dotenv \
        colorlog \
        boto3 \
        schedule \
        psutil
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file template..."
    cat > .env << 'EOL'
# Alpaca API Credentials
ALPACA_API_KEY=your_api_key_here
ALPACA_API_SECRET=your_api_secret_here

# AWS Configuration (optional)
AWS_REGION=us-west-2
SNS_TOPIC_ARN=

# Email Configuration (optional)
EMAIL_SENDER=
EMAIL_PASSWORD=
EMAIL_RECIPIENT=
EOL
    print_warning "Please edit .env file with your Alpaca API credentials"
fi

# Create systemd service file
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/tqqq-bot.service > /dev/null << 'EOL'
[Unit]
Description=TQQQ/SQQQ Trading Bot
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/tqqq_bot_aws_ec2
Environment="PATH=/home/ec2-user/tqqq_bot_aws_ec2/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/ec2-user/tqqq_bot_aws_ec2/venv/bin/python /home/ec2-user/tqqq_bot_aws_ec2/run_bot.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

# Logging
SyslogIdentifier=tqqq-bot

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOL

# Create systemd timer for daily execution (optional)
print_status "Creating systemd timer for daily execution..."
sudo tee /etc/systemd/system/tqqq-bot.timer > /dev/null << 'EOL'
[Unit]
Description=Run TQQQ/SQQQ Trading Bot daily at 6:25 AM PDT
Requires=tqqq-bot.service

[Timer]
# Run Monday-Friday at 6:25 AM PDT (13:25 UTC during PDT, 14:25 UTC during PST)
OnCalendar=Mon-Fri *-*-* 13:25:00
Persistent=true

[Install]
WantedBy=timers.target
EOL

# Reload systemd
print_status "Reloading systemd..."
sudo systemctl daemon-reload

# Create log rotation configuration
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/tqqq-bot > /dev/null << EOL
$BOT_DIR/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 ec2-user ec2-user
}
EOL

# Create cron job for market days only (alternative to systemd timer)
print_status "Creating cron job (alternative to systemd timer)..."
(crontab -l 2>/dev/null || true; echo "25 6 * * 1-5 cd $BOT_DIR && ./venv/bin/python run_bot.py >> logs/cron.log 2>&1") | crontab -

# Set up CloudWatch agent (optional)
print_status "Checking for CloudWatch agent..."
if command -v amazon-cloudwatch-agent-ctl &> /dev/null; then
    print_status "CloudWatch agent found. Configuring..."
    # Add CloudWatch configuration here if needed
else
    print_warning "CloudWatch agent not installed. Install it for metrics monitoring."
fi

# Create helper scripts
print_status "Creating helper scripts..."

# Start script
cat > start_bot.sh << 'EOL'
#!/bin/bash
cd /home/ec2-user/tqqq_bot_aws_ec2
source venv/bin/activate
python run_bot.py
EOL
chmod +x start_bot.sh

# Status script
cat > check_status.sh << 'EOL'
#!/bin/bash
echo "Bot Service Status:"
sudo systemctl status tqqq-bot.service --no-pager
echo ""
echo "Recent Logs:"
sudo journalctl -u tqqq-bot.service -n 20 --no-pager
echo ""
echo "Timer Status:"
sudo systemctl status tqqq-bot.timer --no-pager
EOL
chmod +x check_status.sh

# Test script
cat > test_bot.sh << 'EOL'
#!/bin/bash
cd /home/ec2-user/tqqq_bot_aws_ec2
source venv/bin/activate
python run_bot.py --validate-only
EOL
chmod +x test_bot.sh

# Make run_bot.py executable
chmod +x run_bot.py

print_status "Setup complete!"

echo ""
echo "============================================"
echo "NEXT STEPS:"
echo "============================================"
echo "1. Edit the .env file with your Alpaca API credentials:"
echo "   nano $BOT_DIR/.env"
echo ""
echo "2. Test the configuration:"
echo "   ./test_bot.sh"
echo ""
echo "3. Test notifications:"
echo "   ./venv/bin/python run_bot.py --test-notifications"
echo ""
echo "4. Enable and start the service:"
echo "   sudo systemctl enable tqqq-bot.service"
echo "   sudo systemctl start tqqq-bot.service"
echo ""
echo "5. Enable the timer for daily runs (optional):"
echo "   sudo systemctl enable tqqq-bot.timer"
echo "   sudo systemctl start tqqq-bot.timer"
echo ""
echo "6. Check service status:"
echo "   ./check_status.sh"
echo ""
echo "7. View logs:"
echo "   sudo journalctl -u tqqq-bot.service -f"
echo ""
echo "============================================"
echo "IMPORTANT NOTES:"
echo "============================================"
echo "- The bot runs in PAPER TRADING mode by default"
echo "- Trading times are in PDT (6:30 AM, 7:00 AM, 12:59 PM)"
echo "- Logs are stored in: $BOT_DIR/logs/"
echo "- Service name: tqqq-bot"
echo "- Running on: Amazon Linux 2023"
echo "============================================"
