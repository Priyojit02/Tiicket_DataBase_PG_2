#!/usr/bin/env python
"""
Test script to trigger email fetching and ticket creation
Run this AFTER getting an Azure AD access token from frontend
"""

import asyncio
import httpx

# You need to get this token from the frontend after login
# In browser console after login: copy the access token from sessionStorage
AZURE_ACCESS_TOKEN = "YOUR_AZURE_TOKEN_HERE"

async def trigger_email_fetch():
    """Trigger email fetching and ticket creation via backend API"""

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

    print("Triggering email fetch and ticket creation...\n")

    # Backend API endpoint
    backend_url = "http://localhost:8000/emails/fetch"
    params = {
        "days_back": 1,  # Fetch last 1 day
        "max_emails": 10,  # Process 10 emails max
        "folder": "inbox"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            backend_url,
            params=params,
            headers={"Authorization": f"Bearer {AZURE_ACCESS_TOKEN}"},
            timeout=60.0  # Longer timeout for processing
        )

        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Email fetch triggered successfully!")
            print(f"Response: {data}")
        else:
            print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    asyncio.run(trigger_email_fetch())</content>
<parameter name="filePath">c:\Dash_Board_Project\backend\test_trigger_emails.py