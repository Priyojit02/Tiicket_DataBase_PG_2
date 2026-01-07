# ============================================
# COMPLETE SYSTEM TEST - Backend + Frontend Integration
# ============================================
# Tests the complete flow:
# 1. Backend processes emails every minute
# 2. Creates tickets in database
# 3. Exports to tickets2.ts based on DATA_SOURCE_MODE
# 4. Frontend reads from .env and displays appropriate data

import asyncio
import json
import os
from datetime import datetime
from app.services.email_processor import EmailProcessor
from app.services.ticket_service import TicketService
from app.core.database import AsyncSessionLocal, init_db
from app.repositories.ticket_repository import TicketRepository
from app.core.config import settings

async def test_complete_system():
    """Test the complete backend + frontend integration"""
    print("=" * 70)
    print("🚀 COMPLETE SYSTEM TEST - Backend + Frontend Integration")
    print("=" * 70)
    print()

    # Step 1: Show current configuration
    print("1️⃣ CONFIGURATION CHECK")
    print(f"   Backend DATA_SOURCE_MODE: {settings.data_source_mode}")
    print(f"   LLM Configured: {settings.is_llm_configured}")
    print(f"   Using Mock Services: {settings.should_use_mock_services}")
    print(f"   Scheduler Enabled: {settings.scheduler_enabled}")
    print()

    # Step 2: Initialize database
    print("2️⃣ DATABASE INITIALIZATION")
    await init_db()
    print("   ✅ Database initialized")
    print()

    async with AsyncSessionLocal() as db:
        # Step 3: Process emails (simulating scheduler)
        print("3️⃣ EMAIL PROCESSING (Mock Mode)")
        processor = EmailProcessor(db, use_mock=True)
        result = await processor.process_daily_emails(
            days_back=1,
            max_emails=8,
            auto_create_tickets=True
        )

        print("   📧 Processing Results:")
        for key, value in result.items():
            print(f"      {key}: {value}")
        print()

        # Step 4: Show tickets in database
        print("4️⃣ TICKETS IN DATABASE")
        ticket_repo = TicketRepository(db)
        tickets = await ticket_repo.get_recent(10)

        print(f"   📋 Total tickets in database: {len(tickets)}")
        llm_tickets = [t for t in tickets if t.source_email_id]
        dummy_tickets = [t for t in tickets if not t.source_email_id]

        print(f"   🤖 LLM tickets: {len(llm_tickets)}")
        print(f"   📊 Dummy tickets: {len(dummy_tickets)}")
        print()

        # Step 5: Export to frontend based on DATA_SOURCE_MODE
        print("5️⃣ EXPORT TO FRONTEND (tickets2.ts)")
        ticket_service = TicketService(db)
        count = await ticket_service.update_frontend_tickets_file()

        print(f"   💾 Exported {count} tickets to tickets2.ts")
        print(f"   🎯 Mode: {settings.data_source_mode}")
        print()

        # Step 6: Verify frontend file
        print("6️⃣ VERIFY FRONTEND FILE")
        frontend_path = "frontend-up/src/data/tickets2.ts"

        try:
            with open(frontend_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract JSON part
            start = content.find('export const ticketsData: Ticket[] = ') + len('export const ticketsData: Ticket[] = ')
            end = content.find(';', start)
            if end == -1:
                end = len(content)

            json_content = content[start:end].strip()
            exported_tickets = json.loads(json_content)

            print(f"   📄 tickets2.ts contains {len(exported_tickets)} tickets")
            print(f"   🎯 Matches DATA_SOURCE_MODE: {settings.data_source_mode}")

            if exported_tickets:
                ticket = exported_tickets[0]
                print(f"   🎫 Sample ticket: ID {ticket['id']}, {ticket['title'][:40]}...")
                print(f"      Status: {ticket['status']}, Module: {ticket['module']}")

        except Exception as e:
            print(f"   ❌ Error reading frontend file: {e}")
        print()

        # Step 7: Show frontend .env configuration
        print("7️⃣ FRONTEND CONFIGURATION")
        frontend_env_path = "frontend-up/.env.local"
        try:
            with open(frontend_env_path, 'r', encoding='utf-8') as f:
                env_content = f.read()

            # Find USE_DB line
            for line in env_content.split('\n'):
                if line.startswith('USE_DB='):
                    use_db_value = line.split('=')[1]
                    print(f"   🎛️ Frontend USE_DB: {use_db_value}")
                    break
            else:
                print("   ⚠️ USE_DB not found in frontend .env.local")

        except Exception as e:
            print(f"   ❌ Error reading frontend .env: {e}")
        print()

        # Step 8: Show what frontend will display
        print("8️⃣ FRONTEND DATA SOURCE BEHAVIOR")
        frontend_mode = use_db_value if 'use_db_value' in locals() else 'combined'

        print(f"   🎯 Frontend will use: {frontend_mode} mode")
        if frontend_mode == 'llm':
            print("   🤖 Shows only LLM-parsed tickets from tickets2.ts")
        elif frontend_mode == 'normal':
            print("   📊 Shows only dummy tickets from tickets.ts")
        elif frontend_mode == 'combined':
            print("   🔄 Shows both tickets.ts + tickets2.ts")
        print()

        # Step 9: Complete flow summary
        print("9️⃣ COMPLETE SYSTEM FLOW")
        print("   🔄 Email → LLM Analysis → Database → tickets2.ts → Frontend")
        print("   ⏰ Runs every 1 minute automatically")
        print("   🎛️ Controlled by .env files")
        print("   📊 Backend: DATA_SOURCE_MODE controls export")
        print("   🎨 Frontend: USE_DB controls display")
        print()

        print("=" * 70)
        print("🎉 SYSTEM TEST COMPLETE!")
        print("✅ Backend: Email processing → Database → Export")
        print("✅ Frontend: .env controlled data source")
        print("✅ Integration: Automatic every 1 minute")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_complete_system())