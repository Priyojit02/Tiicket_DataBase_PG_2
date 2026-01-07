# ============================================
# COMPREHENSIVE TICKET CREATION FLOW TEST
# ============================================
# This script demonstrates the complete flow:
# 1. Backend fetches emails from SSO
# 2. LLM parses emails and creates tickets in database
# 3. Tickets are exported to tickets2.ts for frontend
# 4. Frontend automatically switches between dummy/LLM data

import asyncio
import json
import os
from datetime import datetime
from app.services.email_processor import EmailProcessor
from app.services.ticket_service import TicketService
from app.core.database import AsyncSessionLocal, init_db
from app.repositories.ticket_repository import TicketRepository

async def demonstrate_complete_flow():
    """Demonstrate the complete email-to-frontend ticket flow"""
    print("=" * 60)
    print("🎯 COMPREHENSIVE TICKET CREATION FLOW DEMONSTRATION")
    print("=" * 60)
    print()

    # Step 1: Initialize database
    print("1️⃣ INITIALIZING DATABASE...")
    await init_db()
    print("   ✅ Database initialized")
    print()

    async with AsyncSessionLocal() as db:
        # Step 2: Process mock emails (simulating SSO email fetch)
        print("2️⃣ FETCHING & PROCESSING EMAILS FROM SSO...")
        print("   📧 Simulating email fetch from Microsoft Graph API...")

        processor = EmailProcessor(db)  # Always live now
        result = await processor.process_daily_emails(
            days_back=2,
            max_emails=6,
            auto_create_tickets=True
        )

        print("   📊 Processing Results:")
        for key, value in result.items():
            print(f"      {key}: {value}")
        print()

        # Step 3: Show tickets created in database
        print("3️⃣ TICKETS CREATED IN DATABASE...")
        ticket_repo = TicketRepository(db)
        tickets = await ticket_repo.get_recent(10)

        print(f"   📋 Total tickets in database: {len(tickets)}")
        print("   🎫 Sample tickets:")
        for i, ticket in enumerate(tickets[:3], 1):
            print(f"      {i}. {ticket.title[:50]}...")
            print(f"         Status: {ticket.status.value}, Priority: {ticket.priority.value}")
            print(f"         Module: {ticket.category.value if ticket.category else 'OTHER'}")
            print(f"         LLM Confidence: {ticket.llm_confidence:.1%}" if ticket.llm_confidence else "         LLM Confidence: N/A")
            print()
        print()

        # Step 4: Export to frontend format
        print("4️⃣ EXPORTING TICKETS TO FRONTEND FORMAT...")
        ticket_service = TicketService(db)
        frontend_tickets = await ticket_service.export_tickets_to_frontend_format()

        print(f"   📤 Exported {len(frontend_tickets)} LLM-parsed tickets")
        print("   📄 Sample frontend format:")
        for i, ticket in enumerate(frontend_tickets[:2], 1):
            print(f"      {i}. ID: {ticket['id']}, Title: {ticket['title'][:40]}...")
            print(f"         Status: {ticket['status']}, Module: {ticket['module']}")
            print(f"         Tags: {ticket['tags']}")
            print()
        print()

        # Step 5: Update frontend file
        print("5️⃣ UPDATING FRONTEND tickets2.ts FILE...")
        count = await ticket_service.update_frontend_tickets_file()
        print(f"   💾 Updated tickets2.ts with {count} tickets")
        print()

        # Step 6: Verify frontend file
        print("6️⃣ VERIFYING FRONTEND FILE CONTENT...")
        frontend_path = os.path.join(os.path.dirname(__file__), '../frontend-up/src/data/tickets2.ts')

        if os.path.exists(frontend_path):
            with open(frontend_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract the JSON part
            start = content.find('export const llmParsedTickets: Ticket[] = ') + len('export const llmParsedTickets: Ticket[] = ')
            end = content.find(';', start)
            if end == -1:
                end = len(content)

            json_content = content[start:end].strip()
            try:
                parsed_tickets = json.loads(json_content)
                print(f"   ✅ File updated successfully with {len(parsed_tickets)} tickets")
                print("   📊 File contains tickets with IDs:", [t['id'] for t in parsed_tickets[:5]])
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON parsing error: {e}")
        else:
            print("   ❌ Frontend file not found")
        print()

        # Step 7: Explain frontend behavior
        print("7️⃣ FRONTEND DATA SOURCE BEHAVIOR...")
        has_llm_tickets = len(frontend_tickets) > 0
        if has_llm_tickets:
            print("   🤖 Frontend will use LLM data mode (tickets2.ts)")
            print("   📋 Users will see LLM-parsed tickets from email processing")
        else:
            print("   📊 Frontend will use dummy data mode (tickets.ts)")
            print("   📋 Users will see sample tickets for development")
        print()

        # Step 8: Show complete flow summary
        print("8️⃣ COMPLETE FLOW SUMMARY...")
        print("   🔄 Email → LLM Analysis → Database Ticket → Frontend File → UI Display")
        print(f"   📧 Emails processed: {result['analyzed']}")
        print(f"   🎫 SAP-related emails: {result['sap_related']}")
        print(f"   ✅ Tickets created: {result['tickets_created']}")
        print(f"   💾 Frontend file updated: {count} tickets")
        print(f"   🎯 Data source mode: {'LLM' if has_llm_tickets else 'Dummy'}")
        print()

        print("=" * 60)
        print("🎉 FLOW DEMONSTRATION COMPLETE!")
        print("✨ The system automatically switches between dummy and LLM data")
        print("🔧 When LLM API keys are configured, real emails will be processed")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(demonstrate_complete_flow())</content>
<parameter name="filePath">c:\Dash_Board_Project\backend\test_complete_flow.py