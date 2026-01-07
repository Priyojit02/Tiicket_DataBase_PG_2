#!/usr/bin/env python3
"""
Complete Email API Testing Guide
Shows how to test all email endpoints with proper authentication
"""

import requests
import json
from datetime import datetime

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🎯 {title.upper()}")
    print(f"{'='*60}")

def make_request(method, url, headers=None, params=None, data=None):
    """Make HTTP request with error handling"""
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, params=params, json=data)
        else:
            print(f"❌ Unsupported method: {method}")
            return None

        print(f"📡 {method} {url}")
        print(f"   Status: {response.status_code}")

        if response.status_code >= 200 and response.status_code < 300:
            print("   ✅ Success")
            return response.json()
        else:
            print(f"   ❌ Error: {response.text}")
            return None

    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return None

def test_email_apis():
    """Test all email-related API endpoints"""

    BASE_URL = "http://localhost:8000"

    print("🚀 EMAIL API TESTING GUIDE")
    print("=" * 60)
    print("Make sure your backend is running: python run.py")
    print("And you have a valid Azure AD token from the frontend")
    print()

    # You'll need to get this from your frontend application
    ACCESS_TOKEN = "YOUR_AZURE_AD_ACCESS_TOKEN_HERE"

    if ACCESS_TOKEN == "YOUR_AZURE_AD_ACCESS_TOKEN_HERE":
        print("⚠️  IMPORTANT: Replace YOUR_AZURE_AD_ACCESS_TOKEN_HERE with your actual token")
        print("   Get it from your frontend application after logging in")
        print()

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Test 1: Fetch emails from inbox
    print_section("1. FETCH EMAILS FROM INBOX")
    print("POST /emails/fetch?folder=inbox&days_back=1&max_emails=50")
    print("Fetches emails from your inbox (received emails)")

    result = make_request(
        "POST",
        f"{BASE_URL}/emails/fetch",
        headers=headers,
        params={"folder": "inbox", "days_back": 1, "max_emails": 50}
    )

    if result:
        print(f"   📧 Fetched: {result.get('fetched_count', 0)} emails")
        print(f"   📊 Stats: {result.get('stats', {})}")

    # Test 2: Fetch emails from sent items
    print_section("2. FETCH EMAILS FROM SENT ITEMS")
    print("POST /emails/fetch?folder=sentitems&days_back=1&max_emails=50")
    print("Fetches emails you sent (from sent items folder)")

    result = make_request(
        "POST",
        f"{BASE_URL}/emails/fetch",
        headers=headers,
        params={"folder": "sentitems", "days_back": 1, "max_emails": 50}
    )

    if result:
        print(f"   📧 Fetched: {result.get('fetched_count', 0)} emails")
        print(f"   📊 Stats: {result.get('stats', {})}")

    # Test 3: Get email statistics
    print_section("3. GET EMAIL STATISTICS")
    print("GET /emails/stats")
    print("Shows overall email processing statistics")

    result = make_request("GET", f"{BASE_URL}/emails/stats", headers=headers)
    if result:
        print(f"   📊 Total emails: {result.get('total_emails', 0)}")
        print(f"   ✅ Processed: {result.get('processed', 0)}")
        print(f"   🎫 Tickets created: {result.get('tickets_created', 0)}")

    # Test 4: Get recent emails
    print_section("4. GET RECENT EMAILS")
    print("GET /emails/recent?limit=10")
    print("Shows the 10 most recently processed emails")

    result = make_request(
        "GET",
        f"{BASE_URL}/emails/recent",
        headers=headers,
        params={"limit": 10}
    )

    if result and isinstance(result, list):
        print(f"   📧 Recent emails: {len(result)}")
        for i, email in enumerate(result[:3]):  # Show first 3
            print(f"      {i+1}. {email.get('subject', 'No subject')[:50]}...")
            print(f"         From: {email.get('from_address', 'Unknown')}")
            print(f"         SAP: {email.get('is_sap_related', False)}")

    # Test 5: Get unprocessed emails
    print_section("5. GET UNPROCESSED EMAILS")
    print("GET /emails/unprocessed?limit=20")
    print("Shows emails that haven't been analyzed yet")

    result = make_request(
        "GET",
        f"{BASE_URL}/emails/unprocessed",
        headers=headers,
        params={"limit": 20}
    )

    if result and isinstance(result, list):
        print(f"   📧 Unprocessed emails: {len(result)}")
        if result:
            print("   💡 These emails need to be processed or were filtered out")

    # Test 6: Get emails by category
    print_section("6. GET EMAILS BY SAP CATEGORY")
    print("GET /emails/by-category/MM?limit=10")
    print("Shows emails classified as Materials Management (MM)")

    categories = ["MM", "SD", "FICO", "PP", "HCM"]
    for category in categories:
        result = make_request(
            "GET",
            f"{BASE_URL}/emails/by-category/{category}",
            headers=headers,
            params={"limit": 5}
        )
        if result and isinstance(result, list) and result:
            print(f"   📁 {category}: {len(result)} emails")
            break  # Just show one category that has results

    print_section("7. TESTING COMPLETE")
    print("🎯 SUMMARY:")
    print("✅ If you see emails being fetched but no tickets created:")
    print("   - The emails might not be SAP-related")
    print("   - Check LLM confidence scores")
    print("   - Try sending an email with SAP keywords")
    print()
    print("✅ If no emails are fetched:")
    print("   - Check your Azure AD token")
    print("   - Try different time ranges (days_back=7)")
    print("   - Check both inbox and sentitems folders")
    print()
    print("🔄 To re-run: python test_all_email_apis.py")

if __name__ == "__main__":
    test_email_apis()