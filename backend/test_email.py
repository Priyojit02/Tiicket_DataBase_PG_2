#!/usr/bin/env python
"""
Quick test script to check if email fetching works
Run this AFTER getting an Azure AD access token from frontend
"""

import asyncio
import httpx

# You need to get this token from the frontend after login
# In browser console after login: copy the access token from sessionStorage
AZURE_ACCESS_TOKEN = "YOUR_AZURE_TOKEN_HERE"

async def test_email_fetch():
    """Test fetching emails from Microsoft Graph API directly"""
    
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
    
    print("Testing email fetch from Microsoft Graph API...\n")
    
    # Microsoft Graph API - Get recent emails
    graph_url = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages"
    params = {
        "$top": 5,  # Just fetch 5 emails for test
        "$orderby": "receivedDateTime desc",
        "$select": "subject,from,receivedDateTime,bodyPreview"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            graph_url,
            headers={"Authorization": f"Bearer {AZURE_ACCESS_TOKEN}"},
            params=params,
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            emails = data.get("value", [])
            
            print(f"✅ Successfully fetched {len(emails)} emails!\n")
            print("=" * 60)
            
            for i, email in enumerate(emails, 1):
                subject = email.get("subject", "No Subject")
                from_email = email.get("from", {}).get("emailAddress", {}).get("address", "Unknown")
                received = email.get("receivedDateTime", "Unknown")
                preview = email.get("bodyPreview", "")[:100]
                
                print(f"\n📧 Email {i}:")
                print(f"   Subject: {subject}")
                print(f"   From: {from_email}")
                print(f"   Received: {received}")
                print(f"   Preview: {preview}...")
            
            print("\n" + "=" * 60)
            print("✅ Email fetching works!")
            
        elif response.status_code == 401:
            print("❌ Token expired or invalid!")
            print("   Get a fresh token from frontend after login")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


async def test_user_profile():
    """Test if token works by fetching user profile"""
    
    if AZURE_ACCESS_TOKEN == "YOUR_AZURE_TOKEN_HERE":
        print("❌ Please paste your Azure access token first!")
        return
    
    print("Testing Azure AD token by fetching profile...\n")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {AZURE_ACCESS_TOKEN}"}
        )
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Token is valid!")
            print(f"   Name: {user.get('displayName')}")
            print(f"   Email: {user.get('mail') or user.get('userPrincipalName')}")
        else:
            print(f"❌ Token invalid: {response.status_code}")
            print(response.text)


if __name__ == "__main__":
    print("=" * 60)
    print("EMAIL FETCH TEST")
    print("=" * 60)
    
    # First test if token is valid
    asyncio.run(test_user_profile())
    print()
    
    # Then test email fetch
    asyncio.run(test_email_fetch())
