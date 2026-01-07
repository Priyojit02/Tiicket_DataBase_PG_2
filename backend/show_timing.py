#!/usr/bin/env python3
"""
Show Email Time Filtering Logic
"""

from datetime import datetime, timedelta

def show_time_logic():
    print("⏰ EMAIL TIME FILTERING LOGIC")
    print("=" * 40)

    now = datetime.now()
    yesterday = now - timedelta(days=1)
    one_hour_ago = now - timedelta(hours=1)

    print(f"🕐 Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Yesterday: {yesterday.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🕑 1 hour ago: {one_hour_ago.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    print("🎯 DEFAULT BEHAVIOR (days_back=1):")
    print(f"   - Fetches emails from: {yesterday.strftime('%Y-%m-%d %H:%M:%S')} onwards")
    print("   - Your email sent 'just now' would be included ✅")
    print()

    print("❌ WHY SENT EMAILS MIGHT NOT APPEAR:")
    print("   1. ⏳ Email not yet synced to Outlook/Microsoft Graph")
    print("   2. 📁 Wrong folder (inbox vs sentitems)")
    print("   3. 🕐 Time zone differences")
    print("   4. 🔄 Email still being processed by email server")
    print()

    print("💡 SOLUTIONS:")
    print("   - Wait 1-2 minutes after sending")
    print("   - Check both 'inbox' and 'sentitems' folders")
    print("   - Use longer time range: days_back=7")
    print("   - Check Microsoft Graph API directly")

if __name__ == "__main__":
    show_time_logic()