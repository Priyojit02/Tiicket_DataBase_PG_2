#!/usr/bin/env python
"""
Test script to trigger email fetching and ticket creation
Automatically fetches Azure AD access token from multiple sources
"""

import asyncio
import httpx
import os
import json
from pathlib import Path

# Token sources (in order of preference)
TOKEN_FILE = Path(__file__).parent / "azure_token.json"
ENV_TOKEN_KEY = "AZURE_ACCESS_TOKEN"

async def get_azure_token():
    """Automatically get Azure token from multiple sources"""

    # 1. Try environment variable
    token = os.getenv(ENV_TOKEN_KEY)
    if token and token != "YOUR_AZURE_TOKEN_HERE":
        print("✅ Token found in environment variable")
        return token

    # 2. Try token file
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, 'r') as f:
                data = json.load(f)
                token = data.get('access_token') or data.get('token')
                if token:
                    print("✅ Token found in token file")
                    return token
        except Exception as e:
            print(f"⚠️  Error reading token file: {e}")

    # 3. Try to get from backend session (if user is logged in)
    try:
        print("🔍 Checking for active backend session...")
        async with httpx.AsyncClient() as client:
            # Try to get user info to check if logged in
            response = await client.get(
                "http://localhost:8000/api/v1/auth/me",
                timeout=5.0
            )
            if response.status_code == 200:
                # If we can get user info, try to get a fresh token
                # This assumes there's an endpoint to get the token
                token_response = await client.get(
                    "http://localhost:8000/api/v1/auth/token",
                    timeout=5.0
                )
                if token_response.status_code == 200:
                    token_data = token_response.json()
                    token = token_data.get('access_token')
                    if token:
                        print("✅ Token obtained from backend session")
                        return token
    except Exception as e:
        print(f"⚠️  Could not get token from backend: {e}")

    # 4. Manual fallback
    print("❌ No token found automatically!")
    print("\nPlease get token manually:")
    print("1. Open frontend (http://localhost:3000)")
    print("2. Login with Microsoft")
    print("3. Open browser DevTools (F12)")
    print("4. Go to Console tab")
    print("5. Run: sessionStorage.getItem('msal.token.keys')")
    print("6. Copy the access token")
    print("\nThen either:")
    print("- Set environment variable: set AZURE_ACCESS_TOKEN=your_token_here")
    print("- Or save to file: echo '{\"access_token\":\"your_token_here\"}' > azure_token.json")
    print("- Or paste token below:")

    token = input("\nPaste your Azure access token (or press Enter to skip): ").strip()
    if token:
        # Save to file for future use
        try:
            with open(TOKEN_FILE, 'w') as f:
                json.dump({'access_token': token, 'source': 'manual'}, f, indent=2)
            print(f"💾 Token saved to {TOKEN_FILE} for future use")
        except Exception as e:
            print(f"⚠️  Could not save token: {e}")
        return token

    return None

async def trigger_email_fetch():
    """Trigger email fetching and ticket creation via backend API"""

    # Get token automatically
    azure_token = await get_azure_token()
    if not azure_token:
        print("❌ No Azure token available. Cannot proceed.")
        return

    print("🚀 Triggering email fetch and ticket creation...\n")

    # Backend API endpoint
    backend_url = "http://localhost:8000/api/v1/emails/fetch"
    params = {
        "days_back": 1,  # Fetch last 1 day
        "max_emails": 10,  # Process 10 emails max
        "folder": "inbox"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            backend_url,
            params=params,
            headers={"Authorization": f"Bearer {azure_token}"},
            timeout=60.0  # Longer timeout for processing
        )

        print(f"📡 Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Email fetch triggered successfully!")
            print(f"📊 Processed: {data.get('processed_emails', 0)} emails")
            print(f"🎫 Created: {data.get('created_tickets', 0)} tickets")
            if data.get('errors'):
                print(f"⚠️  Errors: {data['errors']}")
        elif response.status_code == 401:
            print("❌ Authentication failed. Token may be expired.")
            print("💡 Try logging in again in the frontend and re-run this script.")
        elif response.status_code == 403:
            print("❌ Access forbidden. Check your permissions.")
        else:
            print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    asyncio.run(trigger_email_fetch())</content>
<parameter name="filePath">c:\Dash_Board_Project\backend\test_trigger_emails.py