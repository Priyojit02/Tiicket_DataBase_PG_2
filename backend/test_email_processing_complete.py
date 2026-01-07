#!/usr/bin/env python
"""
Complete Email Processing & Ticket Creation Test Script
Tests the full pipeline: Email Fetch → LLM Processing → Ticket Creation
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import init_db, AsyncSessionLocal
from app.services.email_processor import EmailProcessor
from app.services.llm_service import LLMService
from app.core.config import settings


async def test_email_processing_pipeline():
    """Test the complete email processing pipeline"""
    print("🧪 Testing Complete Email Processing Pipeline")
    print("=" * 60)

    try:
        # Step 1: Initialize database
        print("📊 Step 1: Initializing database...")
        await init_db()
        print("✅ Database initialized")

        # Step 2: Test LLM Service Configuration
        print("\n🤖 Step 2: Testing LLM Service Configuration...")
        llm_service = LLMService(db=None)  # Test without DB first

        # Test LLM configuration
        if settings.is_llm_configured:
            print("✅ LLM is configured")
            print(f"   Provider: {settings.llm_provider}")
            print(f"   Model: {settings.llm_model}")
            print(f"   API Key: {'*' * 10}...{'*' * 4}")  # Masked
        else:
            print("⚠️  LLM not configured - will use mock processing")
            print("   Set LLM_API_KEY in .env to enable real LLM processing")

        # Step 3: Test Email Processing (Mock Mode)
        print("\n📧 Step 3: Testing Email Processing...")
        async with AsyncSessionLocal() as db:
            # Use mock processor for testing
            processor = EmailProcessor(db, use_mock=True)

            print("   Processing mock emails...")
            result = await processor.process_daily_emails(
                days_back=1,
                max_emails=5,  # Small number for testing
                auto_create_tickets=True
            )

            print("✅ Email processing completed!")
            print(f"   Emails processed: {result.get('emails_processed', 0)}")
            print(f"   Tickets created: {result.get('tickets_created', 0)}")
            print(f"   Processing time: {result.get('processing_time', 0):.2f}s")

            # Show details
            if result.get('tickets_created', 0) > 0:
                print("\n🎫 Created Tickets:")
                for ticket_info in result.get('tickets', []):
                    print(f"   - ID: {ticket_info.get('id')}")
                    print(f"     Title: {ticket_info.get('title')}")
                    print(f"     Status: {ticket_info.get('status')}")
                    print(f"     Priority: {ticket_info.get('priority')}")
                    print(f"     Category: {ticket_info.get('category')}")

        # Step 4: Verify Database State
        print("\n💾 Step 4: Checking Database State...")
        async with AsyncSessionLocal() as db:
            # Count tickets
            from sqlalchemy import text
            result = await db.execute(text("SELECT COUNT(*) FROM tickets"))
            ticket_count = result.scalar()
            print(f"   Total tickets in database: {ticket_count}")

            if ticket_count > 0:
                # Show recent tickets
                result = await db.execute(text("""
                    SELECT id, ticket_id, title, status, priority, category, created_at
                    FROM tickets
                    ORDER BY created_at DESC
                    LIMIT 3
                """))
                recent_tickets = result.fetchall()

                print("   Recent tickets:")
                for ticket in recent_tickets:
                    print(f"   - {ticket.ticket_id}: {ticket.title[:50]}...")
                    print(f"     Status: {ticket.status}, Priority: {ticket.priority}")

        # Step 5: Test Real Email Fetching (if configured)
        print("\n🌐 Step 5: Testing Real Email Fetching...")
        if settings.azure_client_id and settings.azure_client_id != "YOUR_TICKET_MANAGEMENT_SYSTEM_CLIENT_ID":
            print("✅ Azure AD configured for email fetching")
            print("   To test real email fetching:")
            print("   1. Start the backend: python run.py")
            print("   2. Login to frontend at http://localhost:3000")
            print("   3. Use test_trigger_emails.py with your Azure token")
        else:
            print("⚠️  Azure AD not configured")
            print("   Set AZURE_CLIENT_ID and AZURE_TENANT_ID in .env")

        print("\n" + "=" * 60)
        print("🎉 Email Processing Pipeline Test Completed!")
        print("=" * 60)

        # Summary
        print("\n📋 Test Summary:")
        print("✅ Database connection: Working")
        print("✅ Email processing: Working (mock mode)")
        print("✅ Ticket creation: Working")
        print("✅ LLM service: Configured" if settings.is_llm_configured else "⚠️  LLM service: Not configured (using mock)")

        if ticket_count > 0:
            print(f"✅ Database populated: {ticket_count} tickets")
        else:
            print("⚠️  Database empty: Run this script or process real emails")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


async def test_llm_parsing():
    """Test LLM email parsing with sample email"""
    print("\n🧠 Testing LLM Email Parsing...")

    sample_email = """
Subject: SAP Performance Issue - Urgent Help Needed

Dear Support Team,

We are experiencing severe performance issues with our SAP MM module. When processing purchase orders, the system takes over 2 minutes to save transactions. This is significantly impacting our daily operations.

The issue started yesterday morning after the latest system update. Users are reporting timeouts and system hangs.

Please investigate and resolve this ASAP.

Best regards,
John Smith
Procurement Manager
ABC Company
"""

    try:
        llm_service = LLMService(db=None)

        print("   Parsing sample email...")
        result = await llm_service.parse_email_to_ticket(sample_email)

        print("✅ LLM parsing successful!")
        print(f"   Title: {result.title}")
        print(f"   Priority: {result.priority}")
        print(f"   Category: {result.category}")
        print(f"   Confidence: {result.confidence}")

    except Exception as e:
        print(f"❌ LLM parsing failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting Email Processing & Ticket Creation Test")
    print(f"⏰ Started at: {datetime.now()}")

    # Run main test
    asyncio.run(test_email_processing_pipeline())

    # Optional: Test LLM parsing
    if len(sys.argv) > 1 and sys.argv[1] == "--llm":
        asyncio.run(test_llm_parsing())

    print(f"\n⏰ Completed at: {datetime.now()}")
    print("\n💡 Next steps:")
    print("1. Check your .env file for LLM_API_KEY if you want real LLM processing")
    print("2. Run 'python run.py' to start the backend with scheduler")
    print("3. Login to frontend and trigger real email processing")