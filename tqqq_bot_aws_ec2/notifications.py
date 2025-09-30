"""
Notification System for TQQQ/SQQQ Trading Bot
Provides desktop notifications, console output, and logging
"""

import os
import logging
from datetime import datetime
import pytz

# Try to import plyer for desktop notifications
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("Warning: plyer not installed. Desktop notifications will be disabled.")

# Try to import colorlog for colored console output
try:
    import colorlog
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False

class NotificationHandler:
    def __init__(self):
        """Initialize the notification handler"""
        self.pdt = pytz.timezone('America/Los_Angeles')
        
        # Set up logging
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Create a separate logger for notifications
        self.logger = logging.getLogger('notifications')
        self.logger.setLevel(logging.INFO)
        
        # File handler for notifications
        fh = logging.FileHandler(
            os.path.join(log_dir, f'notifications_{datetime.now().strftime("%Y%m%d")}.log')
        )
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        # Console handler with colors if available
        if COLORLOG_AVAILABLE:
            console_handler = colorlog.StreamHandler()
            console_handler.setFormatter(
                colorlog.ColoredFormatter(
                    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
                    log_colors={
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red,bg_white',
                    }
                )
            )
            self.logger.addHandler(console_handler)
        else:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def send_notification(self, title, message, urgency='normal'):
        """
        Send a notification through multiple channels
        
        Args:
            title: Notification title
            message: Notification message
            urgency: 'low', 'normal', or 'critical'
        """
        timestamp = datetime.now(self.pdt).strftime('%H:%M:%S PDT')
        full_message = f"[{timestamp}] {message}"
        
        # Console output with formatting
        self._console_notification(title, full_message, urgency)
        
        # Desktop notification
        if PLYER_AVAILABLE:
            self._desktop_notification(title, message)
        
        # Log the notification
        self.logger.info(f"{title}: {message}")
    
    def _console_notification(self, title, message, urgency):
        """Display formatted console notification"""
        # Determine emoji based on title content
        emoji = self._get_emoji(title)
        
        # Create formatted output
        border = "=" * 60
        
        if urgency == 'critical':
            print("\n" + "!" * 60)
            print(f"🚨 CRITICAL: {title}")
            print("!" * 60)
        else:
            print("\n" + border)
            print(f"{emoji} {title}")
            print("-" * 60)
        
        # Print message lines
        for line in message.split('\n'):
            if line.strip():
                print(f"  {line}")
        
        print(border + "\n")
    
    def _desktop_notification(self, title, message):
        """Send desktop notification using plyer"""
        try:
            # Limit message length for desktop notifications
            if len(message) > 200:
                message = message[:197] + "..."
            
            notification.notify(
                title=title,
                message=message,
                app_name='TQQQ/SQQQ Trading Bot',
                timeout=10  # Notification stays for 10 seconds
            )
        except Exception as e:
            self.logger.error(f"Failed to send desktop notification: {e}")
    
    def _get_emoji(self, title):
        """Get appropriate emoji based on notification title"""
        title_lower = title.lower()
        
        emoji_map = {
            'buy': '📈',
            'sell': '📉',
            'error': '❌',
            'warning': '⚠️',
            'started': '🚀',
            'stopped': '🛑',
            'shutdown': '🛑',
            'completed': '✅',
            'summary': '📊',
            'open': '🔔',
            'closed': '🔕',
            'position': '💼',
            'trade': '💹',
            'signal': '📡',
            'tqqq': '📈',
            'sqqq': '📉',
        }
        
        for keyword, emoji in emoji_map.items():
            if keyword in title_lower:
                return emoji
        
        return '📢'  # Default emoji
    
    def send_trade_alert(self, action, symbol, quantity, price, order_id=None):
        """Send a special formatted trade alert"""
        title = f"Trade Alert: {action} {symbol}"
        
        lines = [
            f"{action} {quantity} shares of {symbol}",
            f"Price: ${price:.2f}",
            f"Total Value: ${price * quantity:.2f}",
        ]
        
        if order_id:
            lines.append(f"Order ID: {order_id}")
        
        message = "\n".join(lines)
        
        # Send as critical notification for trades
        self.send_notification(title, message, urgency='normal')
    
    def send_pnl_report(self, symbol, buy_price, sell_price, quantity):
        """Send P&L report notification"""
        pnl = (sell_price - buy_price) * quantity
        pnl_pct = ((sell_price - buy_price) / buy_price) * 100
        
        title = "P&L Report"
        
        if pnl >= 0:
            emoji = "💰"
            status = "PROFIT"
        else:
            emoji = "📉"
            status = "LOSS"
        
        message = f"{emoji} {status}: ${abs(pnl):.2f} ({pnl_pct:+.2f}%)\n"
        message += f"Symbol: {symbol}\n"
        message += f"Buy: ${buy_price:.2f} | Sell: ${sell_price:.2f}"
        
        self.send_notification(title, message)
    
    def test_notifications(self):
        """Test all notification channels"""
        print("\n" + "=" * 60)
        print("TESTING NOTIFICATION SYSTEM")
        print("=" * 60)
        
        # Test different notification types
        test_cases = [
            ("System Test", "Testing notification system...", "normal"),
            ("Trade Alert: BUY TQQQ", "Bought 1 share at $45.67", "normal"),
            ("Trade Alert: SELL SQQQ", "Sold 1 share at $23.45", "normal"),
            ("Error", "Connection lost to Alpaca API", "critical"),
            ("Daily Summary", "Total P&L: +$12.34 (+2.5%)", "normal"),
        ]
        
        for title, message, urgency in test_cases:
            print(f"\nTesting: {title}")
            self.send_notification(title, message, urgency)
            import time
            time.sleep(1)  # Small delay between notifications
        
        # Test trade alert
        print("\nTesting trade alert...")
        self.send_trade_alert("BUY", "TQQQ", 1, 45.67, "test-order-123")
        
        # Test P&L report
        print("\nTesting P&L report...")
        self.send_pnl_report("TQQQ", 45.00, 46.50, 1)
        
        print("\n" + "=" * 60)
        print("NOTIFICATION TEST COMPLETE")
        print("=" * 60)
        
        # Check what's available
        print("\nNotification Channels Available:")
        print(f"  ✓ Console Output: Yes")
        print(f"  {'✓' if PLYER_AVAILABLE else '✗'} Desktop Notifications: {'Yes' if PLYER_AVAILABLE else 'No (install plyer)'}")
        print(f"  {'✓' if COLORLOG_AVAILABLE else '✗'} Colored Output: {'Yes' if COLORLOG_AVAILABLE else 'No (install colorlog)'}")
        print(f"  ✓ Log Files: Yes (check logs/ directory)")
        print()

if __name__ == "__main__":
    # Test the notification system
    handler = NotificationHandler()
    handler.test_notifications()
