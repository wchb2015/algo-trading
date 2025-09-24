"""
Notification Handler for Trading Bot
Provides desktop notifications, console alerts, and logging
"""

import os
import sys
import logging
from datetime import datetime
import platform

# Try to import notification libraries
try:
    from plyer import notification as desktop_notification
    DESKTOP_NOTIFICATIONS_AVAILABLE = True
except ImportError:
    DESKTOP_NOTIFICATIONS_AVAILABLE = False
    print("Desktop notifications not available. Install 'plyer' for desktop notifications.")

# For macOS, we can also use osascript for notifications
IS_MACOS = platform.system() == 'Darwin'

logger = logging.getLogger(__name__)

class NotificationHandler:
    def __init__(self, enable_desktop=True, enable_console=True, enable_sound=True):
        """
        Initialize notification handler
        
        Args:
            enable_desktop: Enable desktop notifications
            enable_console: Enable console output with colors
            enable_sound: Enable sound alerts
        """
        self.enable_desktop = enable_desktop and (DESKTOP_NOTIFICATIONS_AVAILABLE or IS_MACOS)
        self.enable_console = enable_console
        self.enable_sound = enable_sound
        
        # ANSI color codes for console output
        self.COLORS = {
            'HEADER': '\033[95m',
            'BLUE': '\033[94m',
            'CYAN': '\033[96m',
            'GREEN': '\033[92m',
            'WARNING': '\033[93m',
            'FAIL': '\033[91m',
            'ENDC': '\033[0m',
            'BOLD': '\033[1m',
            'UNDERLINE': '\033[4m'
        }
        
        # Create notifications log file
        self.log_file = f"notifications_{datetime.now().strftime('%Y%m%d')}.log"
        
    def send_notification(self, title, message, urgency='normal'):
        """
        Send notification through multiple channels
        
        Args:
            title: Notification title
            message: Notification message
            urgency: 'low', 'normal', or 'critical'
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Log to file
        self._log_to_file(timestamp, title, message)
        
        # Console notification
        if self.enable_console:
            self._console_notification(title, message, urgency)
        
        # Desktop notification
        if self.enable_desktop:
            self._desktop_notification(title, message)
        
        # Sound alert for critical notifications
        if self.enable_sound and urgency == 'critical':
            self._play_sound()
    
    def _log_to_file(self, timestamp, title, message):
        """Log notification to file"""
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {title}\n")
            f.write(f"{message}\n")
            f.write("-" * 50 + "\n")
    
    def _console_notification(self, title, message, urgency):
        """Display colored console notification"""
        # Choose color based on urgency and title content
        if urgency == 'critical' or 'Error' in title or 'Failed' in title:
            color = self.COLORS['FAIL']
        elif 'BUY' in title:
            color = self.COLORS['GREEN']
        elif 'SELL' in title:
            color = self.COLORS['WARNING']
        elif 'Summary' in title:
            color = self.COLORS['CYAN']
        else:
            color = self.COLORS['BLUE']
        
        # Print formatted notification
        print("\n" + "=" * 60)
        print(f"{color}{self.COLORS['BOLD']}📢 {title}{self.COLORS['ENDC']}")
        print("-" * 60)
        print(f"{message}")
        print("=" * 60 + "\n")
    
    def _desktop_notification(self, title, message):
        """Send desktop notification"""
        try:
            if IS_MACOS:
                # Use macOS native notification via osascript
                self._macos_notification(title, message)
            elif DESKTOP_NOTIFICATIONS_AVAILABLE:
                # Use plyer for cross-platform notifications
                desktop_notification.notify(
                    title=title,
                    message=message[:256],  # Limit message length
                    app_name='TQQQ Trading Bot',
                    timeout=10  # Notification stays for 10 seconds
                )
        except Exception as e:
            logger.warning(f"Could not send desktop notification: {e}")
    
    def _macos_notification(self, title, message):
        """Send macOS native notification using osascript"""
        try:
            # Escape quotes in title and message
            title = title.replace('"', '\\"')
            message = message.replace('"', '\\"')
            
            # Create AppleScript command
            script = f'''
            display notification "{message}" with title "{title}" sound name "Glass"
            '''
            
            # Execute AppleScript
            os.system(f"osascript -e '{script}'")
        except Exception as e:
            logger.warning(f"Could not send macOS notification: {e}")
    
    def _play_sound(self):
        """Play alert sound"""
        try:
            if IS_MACOS:
                # Play system sound on macOS
                os.system('afplay /System/Library/Sounds/Glass.aiff')
            elif platform.system() == 'Linux':
                # Use paplay or beep on Linux
                os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || echo -e "\\a"')
            elif platform.system() == 'Windows':
                # Use winsound on Windows
                import winsound
                winsound.Beep(1000, 500)
            else:
                # Fallback to terminal bell
                print('\a')
        except Exception as e:
            logger.warning(f"Could not play sound: {e}")
    
    def send_trade_alert(self, action, symbol, quantity, price, order_id=None):
        """
        Send a formatted trade alert
        
        Args:
            action: 'BUY' or 'SELL'
            symbol: Stock symbol
            quantity: Number of shares
            price: Execution price
            order_id: Order ID (optional)
        """
        title = f"🔔 Trade Alert: {action} {symbol}"
        
        message = f"{action} {quantity} shares of {symbol}\n"
        message += f"Price: ${price:.2f}\n"
        message += f"Total Value: ${quantity * price:.2f}"
        
        if order_id:
            message += f"\nOrder ID: {order_id}"
        
        # Trade alerts are critical
        self.send_notification(title, message, urgency='critical')
    
    def send_pnl_update(self, pnl, pnl_percentage):
        """
        Send P&L update notification
        
        Args:
            pnl: Profit/loss amount
            pnl_percentage: Profit/loss percentage
        """
        if pnl >= 0:
            title = "📈 Profit Update"
            emoji = "🟢"
            urgency = 'normal'
        else:
            title = "📉 Loss Update"
            emoji = "🔴"
            urgency = 'critical'
        
        message = f"{emoji} P&L: ${pnl:.2f} ({pnl_percentage:.2f}%)"
        
        self.send_notification(title, message, urgency=urgency)
    
    def send_market_status(self, status, details=""):
        """
        Send market status notification
        
        Args:
            status: 'OPEN', 'CLOSED', 'OPENING_SOON', etc.
            details: Additional details
        """
        status_messages = {
            'OPEN': ('🟢 Market Open', 'Trading session has started'),
            'CLOSED': ('🔴 Market Closed', 'Trading session has ended'),
            'OPENING_SOON': ('🟡 Market Opening Soon', 'Prepare for trading'),
            'CLOSING_SOON': ('🟡 Market Closing Soon', 'Positions will be closed soon')
        }
        
        title, default_message = status_messages.get(status, ('Market Update', ''))
        message = details if details else default_message
        
        self.send_notification(title, message)


# Test notifications if run directly
if __name__ == "__main__":
    notifier = NotificationHandler()
    
    print("Testing notification system...")
    
    # Test different notification types
    notifier.send_notification("Test Alert", "This is a test notification")
    
    notifier.send_trade_alert("BUY", "TQQQ", 1, 45.67, "ORD123456")
    
    notifier.send_pnl_update(125.50, 2.5)
    notifier.send_pnl_update(-75.25, -1.5)
    
    notifier.send_market_status("OPEN")
    
    print("Notification tests completed. Check your desktop for notifications.")
