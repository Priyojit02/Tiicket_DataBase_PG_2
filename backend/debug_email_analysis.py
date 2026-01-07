#!/usr/bin/env python3
"""
Debug Email Analysis - Test LLM analysis on actual emails
This script fetches emails and shows what the LLM analysis returns
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any

from app.core.config import settings
from app.core.database import get_db
from app.services.email_service import EmailService
from app.services.llm_service import LLMService


async def debug_email_analysis():
    """Fetch emails and analyze them with LLM to see what gets detected"""

    print("🔍 DEBUG EMAIL ANALYSIS")
    print("=" * 50)

    # Get database session
    db = next(get_db())

    # Initialize services
    email_service = EmailService(db)
    llm_service = LLMService(db)

    # Test different time ranges
    time_ranges = [
        ("Last 24 hours", 1),
        ("Last 7 days", 7),
        ("Last 30 days", 30),
        ("Last 90 days", 90)
    ]

    for range_name, days in time_ranges:
        print(f"\n📅 Testing {range_name}...")
        print("-" * 30)

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        try:
            # Fetch emails
            emails = await email_service.fetch_emails(
                start_date=start_date,
                end_date=end_date,
                limit=50  # Test with more emails
            )

            print(f"📧 Found {len(emails)} emails in {range_name}")

            if not emails:
                print("   No emails found in this time range")
                continue

            # Analyze each email
            sap_related_count = 0
            analysis_results = []

            for i, email in enumerate(emails[:10]):  # Analyze first 10 emails
                print(f"\n   🔍 Analyzing email {i+1}/{min(10, len(emails))}:")
                print(f"      From: {email.get('from', {}).get('emailAddress', {}).get('address', 'Unknown')}")
                print(f"      Subject: {email.get('subject', 'No subject')[:80]}...")

                # Get email content
                subject = email.get('subject', '')
                body = email.get('body', {}).get('content', '')
                from_address = email.get('from', {}).get('emailAddress', {}).get('address', '')

                try:
                    # Analyze with LLM
                    analysis = await llm_service.analyze_email(
                        subject=subject,
                        body=body,
                        from_address=from_address
                    )

                    # Store result
                    result = {
                        'email_id': email.get('id'),
                        'subject': subject[:50],
                        'from': from_address,
                        'is_sap_related': analysis.is_sap_related,
                        'confidence': analysis.confidence,
                        'category': analysis.detected_category.value if analysis.detected_category else None,
                        'priority': analysis.suggested_priority.value if analysis.suggested_priority else None,
                        'title': analysis.suggested_title,
                        'raw_response': analysis.raw_response
                    }
                    analysis_results.append(result)

                    # Print result
                    status = "✅ SAP" if analysis.is_sap_related else "❌ Not SAP"
                    confidence = f"{analysis.confidence:.2f}"
                    category = analysis.detected_category.value if analysis.detected_category else "None"

                    print(f"      Result: {status} | Confidence: {confidence} | Category: {category}")
                    print(f"      Title: {analysis.suggested_title}")

                    if analysis.is_sap_related:
                        sap_related_count += 1

                except Exception as e:
                    print(f"      ❌ Analysis failed: {e}")
                    continue

            # Summary for this time range
            print(f"\n   📊 Summary for {range_name}:")
            print(f"      Total analyzed: {len(analysis_results)}")
            print(f"      SAP-related: {sap_related_count}")
            print(".1f")

            # Show sample of non-SAP emails to understand why
            non_sap_emails = [r for r in analysis_results if not r['is_sap_related']]
            if non_sap_emails:
                print(f"\n   📝 Sample non-SAP emails:")
                for email in non_sap_emails[:3]:  # Show first 3
                    print(f"      Subject: '{email['subject']}' | From: {email['from']}")

        except Exception as e:
            print(f"❌ Error testing {range_name}: {e}")
            continue

    print("\n" + "=" * 50)
    print("🎯 RECOMMENDATIONS:")
    print("1. If no SAP emails found, check if your inbox has SAP-related emails")
    print("2. Try longer time ranges if recent emails aren't SAP-related")
    print("3. Check email content - system looks for SAP keywords and context")
    print("4. Consider adjusting confidence threshold if needed")


if __name__ == "__main__":
    asyncio.run(debug_email_analysis())