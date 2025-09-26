#!/usr/bin/env python3
"""
Detailed test script for notification system
Tests both send_notification and send_trade_alert methods
"""

import time
from notifications import NotificationHandler

def test_notifications():
    """Run comprehensive notification tests"""
    notifier = NotificationHandler()
    
    print("=" * 60)
    print("NOTIFICATION SYSTEM DETAILED TEST")
    print("=" * 60)
    
    tests = [
        ("Test 1: Basic notification", 
         lambda: notifier.send_notification("Basic Test", "Simple notification test")),
        
        ("Test 2: Notification with emojis", 
         lambda: notifier.send_notification("📊 Emoji Test", "Testing emoji support 🚀")),
        
        ("Test 3: Trade alert (BUY)", 
         lambda: notifier.send_trade_alert("BUY", "TQQQ", 1, 45.67, "ORD123")),
        
        ("Test 4: Trade alert (SELL)", 
         lambda: notifier.send_trade_alert("SELL", "TQQQ", 1, 46.89, "ORD456")),
        
        ("Test 5: Critical notification", 
         lambda: notifier.send_notification("Critical Alert", "This is critical!", urgency='critical')),
        
        ("Test 6: Long message notification", 
         lambda: notifier.send_notification("Long Message", "This is a very long message that contains a lot of text to test how the notification system handles lengthy content. It should be truncated appropriately to fit within system limits while still conveying the important information to the user.")),
        
        ("Test 7: Special characters", 
         lambda: notifier.send_notification("Special Chars", "Price: $123.45 | P&L: +2.5% | Order #ABC-123")),
        
        ("Test 8: P&L Updates", 
         lambda: (notifier.send_pnl_update(125.50, 2.5), 
                  time.sleep(1),
                  notifier.send_pnl_update(-75.25, -1.5))[0]),
        
        ("Test 9: Market status", 
         lambda: notifier.send_market_status("OPEN")),
    ]
    
    for i, (description, test_func) in enumerate(tests, 1):
        print(f"\n{description}...")
        try:
            test_func()
            print(f"  ✅ Success")
            time.sleep(1)  # Small delay between tests
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("All tests completed. Check:")
    print("1. Console output above for colored notifications")
    print("2. Desktop for notification popups")
    print("3. tqqq_bot/logs/ directory for log files")
    print("4. Listen for sound alerts on critical notifications")
    print("\nIf some desktop notifications didn't appear:")
    print("- Check your system notification settings")
    print("- Try installing pync: pip install pync")
    print("- Check if notifications are enabled for Terminal/Python")

if __name__ == "__main__":
    test_notifications()
