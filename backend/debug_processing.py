#!/usr/bin/env python3
"""
Debug Email Processing Pipeline
Shows exactly what happens to each email during processing
"""

import asyncio
from app.core.database import get_db
from app.services.email_service import EmailService
from app.services.llm_service import LLMService


async def debug_email_processing():
    """Debug what happens to emails during processing"""

    print("🔍 DEBUGGING EMAIL PROCESSING PIPELINE")
    print("=" * 50)

    db = next(get_db())
    email_service = EmailService(db)
    llm_service = LLMService(db)

    # Get recent emails from database
    recent_emails = await email_service.get_recent_emails(limit=10)

    print(f"📧 Found {len(recent_emails)} recent emails in database")
    print()

    for i, email in enumerate(recent_emails):
        print(f"📧 EMAIL {i+1}: {email.subject[:50]}...")
        print(f"   From: {email.from_address}")
        print(f"   Received: {email.received_at}")
        print(f"   Body preview: {email.body_text[:100] if email.body_text else 'No body'}...")

        # Analyze with LLM
        try:
            analysis = await llm_service.analyze_email(
                subject=email.subject,
                body=email.body_text or "",
                from_address=email.from_address
            )

            print("   🤖 LLM Analysis:")
            print(f"      SAP Related: {analysis.is_sap_related}")
            print(".2f")
            print(f"      Category: {analysis.detected_category.value if analysis.detected_category else 'None'}")
            print(f"      Title: {analysis.suggested_title}")

            # Check if it would create a ticket
            would_create_ticket = analysis.is_sap_related and analysis.confidence >= 0.6
            print(f"   🎫 Would create ticket: {would_create_ticket}")

            if not would_create_ticket:
                if not analysis.is_sap_related:
                    print("   ❌ REASON: Not detected as SAP-related")
                elif analysis.confidence < 0.6:
                    print(f"   ❌ REASON: Low confidence ({analysis.confidence:.2f} < 0.6)")
                else:
                    print("   ❌ REASON: Unknown filtering issue")

        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")

        print("-" * 40)

    print("\n🎯 SUMMARY:")
    print("✅ Emails that create tickets: SAP-related + confidence ≥0.6")
    print("❌ Emails that don't create tickets:")
    print("   - Not SAP-related content")
    print("   - Low LLM confidence (<0.6)")
    print("   - Analysis failures")

    print("\n💡 TO SEE MORE EMAILS:")
    print("1. Fetch more emails: POST /emails/fetch?days_back=7")
    print("2. Check different folder: POST /emails/fetch?folder=sentitems")
    print("3. View all unprocessed: GET /emails/unprocessed")


if __name__ == "__main__":
    asyncio.run(debug_email_processing())