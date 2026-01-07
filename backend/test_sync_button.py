#!/usr/bin/env python3
"""
Test the Sync Button Functionality
This script tests the email sync endpoint that the frontend button calls
"""

import asyncio
import httpx

# Replace with your actual Azure AD token
AZURE_ACCESS_TOKEN = "YOUR_AZURE_TOKEN_HERE"

async def test_sync_button():
    """Test the sync button functionality"""

    print("🔄 TESTING SYNC BUTTON FUNCTIONALITY")
    print("=" * 50)

    if AZURE_ACCESS_TOKEN == "YOUR_AZURE_TOKEN_HERE":
        print("❌ Please set your Azure AD access token first!")
        print("\nHow to get token:")
        print("1. Open frontend: http://localhost:3000")
        print("2. Login with Microsoft")
        print("3. Open DevTools (F12) → Console")
        print("4. Run: sessionStorage.getItem('msal.token.keys.tenant-id')")
        print("5. Copy the token and paste above")
        return

    print("📡 Testing email sync endpoint...")
    print("POST /emails/fetch?folder=inbox&days_back=1&max_emails=50")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8000/emails/fetch",
                params={
                    "folder": "inbox",
                    "days_back": 1,
                    "max_emails": 50
                },
                headers={"Authorization": f"Bearer {AZURE_ACCESS_TOKEN}"}
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("✅ Sync successful!")
                print(f"📧 Emails fetched: {data.get('fetched_count', 0)}")
                print(f"📊 Processing stats: {data.get('stats', {})}")

                # Show what the frontend button would display
                fetched = data.get('fetched_count', 0)
                tickets = data.get('stats', {}).get('tickets_created', 0)
                print(f"\n🎯 Frontend button result: '{fetched} emails, {tickets} tickets'")

            else:
                print(f"❌ Sync failed: {response.text}")

    except Exception as e:
        print(f"❌ Request failed: {e}")

    print("\n💡 This is exactly what happens when you click 'Sync Emails' in the dashboard!")

if __name__ == "__main__":
    asyncio.run(test_sync_button())