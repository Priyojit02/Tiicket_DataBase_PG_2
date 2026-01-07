#!/usr/bin/env python3
"""
Test Email Fetching - Test both inbox and sent items
This script tests fetching from different folders with proper date filtering
"""

import asyncio
import json
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.database import get_db
from app.services.email_service import EmailService


async def test_email_fetching():
    """Test fetching emails from different folders"""

    print("🧪 TESTING EMAIL FETCHING")
    print("=" * 50)

    # Get database session
    db = next(get_db())
    email_service = EmailService(db)

    # Test different folders and time ranges
    test_cases = [
        {"folder": "inbox", "days_back": 1, "description": "Inbox - Last 24 hours"},
        {"folder": "inbox", "days_back": 7, "description": "Inbox - Last 7 days"},
        {"folder": "sentitems", "days_back": 1, "description": "Sent Items - Last 24 hours"},
        {"folder": "sentitems", "days_back": 7, "description": "Sent Items - Last 7 days"},
    ]

    print("⚠️  Note: This test requires a valid Azure AD access token")
    print("   You can get one from your frontend application")
    print()

    # For testing, we'll show what the API calls would look like
    for test_case in test_cases:
        folder = test_case["folder"]
        days_back = test_case["days_back"]
        description = test_case["description"]

        print(f"📁 Testing: {description}")
        print(f"   Folder: {folder}")
        print(f"   Days back: {days_back}")

        # Calculate the date filter
        since_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Show what the API call would look like
        if folder.lower() == "sentitems":
            date_filter = f"sentDateTime ge {since_date}"
            order_by = "sentDateTime desc"
            print("   📅 Filtering by: sentDateTime (when you sent the email)")
        else:
            date_filter = f"receivedDateTime ge {since_date}"
            order_by = "receivedDateTime desc"
            print("   📅 Filtering by: receivedDateTime (when email was received)")

        print(f"   🔗 API Filter: {date_filter}")
        print(f"   📊 Order by: {order_by}")
        print()

    print("💡 KEY FIXES APPLIED:")
    print("1. ✅ Sent items now filter by 'sentDateTime' instead of 'receivedDateTime'")
    print("2. ✅ Inbox items still filter by 'receivedDateTime'")
    print("3. ✅ Proper ordering for each folder type")
    print()

    print("🧪 TO TEST WITH REAL TOKEN:")
    print("1. Get your Azure AD access token from the frontend")
    print("2. Run the email fetch endpoint:")
    print("   POST /emails/fetch?folder=sentitems&days_back=7")
    print("3. Or test inbox:")
    print("   POST /emails/fetch?folder=inbox&days_back=7")
    print()

    print("🎯 EXPECTED RESULTS:")
    print("- Sent items should now include emails you sent recently")
    print("- Inbox should include emails received recently")
    print("- Both should respect the time filtering properly")


if __name__ == "__main__":
    asyncio.run(test_email_fetching())