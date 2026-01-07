#!/usr/bin/env python
"""
Debug script to test Microsoft Graph API email fetching
"""

import asyncio
import httpx
from datetime import datetime, timedelta

# You need to get this token from the frontend after login
AZURE_ACCESS_TOKEN = "YOUR_AZURE_TOKEN_HERE"

async def test_graph_api_emails():
    """Test Microsoft Graph API email fetching with different parameters"""

    if AZURE_ACCESS_TOKEN == "YOUR_AZURE_TOKEN_HERE":
        print("❌ Please paste your Azure access token first!")
        print("\nHow to get token:")
        print("1. Open frontend (http://localhost:3000)")
        print("2. Login with Microsoft")
        print("3. Open browser DevTools (F12)")
        print("4. Go to Console tab")
        print("5. Type: sessionStorage.getItem('msal.token.keys')")
        print("6. Copy the access token and paste in this file")
        return

    print("🔍 Testing Microsoft Graph API Email Fetching")
    print("=" * 60)

    # Test different time ranges
    test_cases = [
        {"days_back": 1, "name": "Last 24 hours"},
        {"days_back": 7, "name": "Last 7 days"},
        {"days_back": 30, "name": "Last 30 days"},
    ]

    for test_case in test_cases:
        days_back = test_case["days_back"]
        name = test_case["name"]

        print(f"\n📧 Testing: {name} (days_back={days_back})")
        print("-" * 40)

        try:
            # Calculate date filter
            since_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
            print(f"Looking for emails since: {since_date}")

            # Microsoft Graph API URL
            graph_url = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages"

            params = {
                "$top": 50,  # Get up to 50 emails
                "$orderby": "receivedDateTime desc",
                "$filter": f"receivedDateTime ge {since_date}",
                "$select": "subject,from,receivedDateTime,bodyPreview"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    graph_url,
                    headers={"Authorization": f"Bearer {AZURE_ACCESS_TOKEN}"},
                    params=params,
                    timeout=30.0
                )

                print(f"Status Code: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    messages = data.get("value", [])

                    print(f"✅ Found {len(messages)} emails")

                    if len(messages) > 0:
                        print("\n📨 Recent emails:")
                        for i, msg in enumerate(messages[:5]):  # Show first 5
                            subject = msg.get("subject", "No subject")[:50]
                            from_addr = msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown")
                            received = msg.get("receivedDateTime", "Unknown")
                            print(f"  {i+1}. {subject}...")
                            print(f"     From: {from_addr}")
                            print(f"     Date: {received}")
                            print()

                    else:
                        print("❌ No emails found in this time range")

                else:
                    error_data = response.json() if response.text else {}
                    print(f"❌ Graph API Error: {response.status_code}")
                    print(f"Error details: {error_data}")

        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n" + "=" * 60)
    print("🎯 Troubleshooting Tips:")
    print("=" * 60)

    print("1. Check if you have emails in your inbox from the specified time range")
    print("2. Verify the Azure token is still valid (tokens expire)")
    print("3. Check if you're accessing the correct mailbox/folder")
    print("4. Try different time ranges (7 days, 30 days)")
    print("5. Check if your mailbox has any emails at all")

    print("\n🔧 To test with your backend:")
    print("1. Update test_trigger_emails.py with your token")
    print("2. Change days_back parameter to 7 or 30")
    print("3. Run: python test_trigger_emails.py")

if __name__ == "__main__":
    asyncio.run(test_graph_api_emails())