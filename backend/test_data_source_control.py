# ============================================
# TEST USER DATA SOURCE CONTROL
# ============================================
# This script tests the new user-controlled data source feature

import asyncio
import json
from app.services.email_processor import EmailProcessor
from app.services.ticket_service import TicketService
from app.core.database import AsyncSessionLocal, init_db
from app.repositories.ticket_repository import TicketRepository

async def test_data_source_control():
    """Test the user-controlled data source functionality"""
    print("=" * 60)
    print("🧪 TESTING USER DATA SOURCE CONTROL")
    print("=" * 60)
    print()

    # Step 1: Initialize database
    await init_db()
    print("✅ Database initialized")

    async with AsyncSessionLocal() as db:
        # Step 2: Process some mock emails to create LLM tickets
        print("\n📧 Processing mock emails to create LLM tickets...")
        processor = EmailProcessor(db)
        result = await processor.process_daily_emails(
            days_back=3,
            max_emails=5,
            auto_create_tickets=True
        )

        print(f"   📊 Processing Results: {result}")

        # Step 3: Export to frontend
        print("\n💾 Exporting tickets to frontend...")
        ticket_service = TicketService(db)
        count = await ticket_service.update_frontend_tickets_file()
        print(f"   ✅ Exported {count} tickets to tickets2.ts")

        # Step 4: Verify frontend file
        print("\n🔍 Verifying frontend file content...")
        frontend_path = "frontend-up/src/data/tickets2.ts"

        try:
            with open(frontend_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract JSON part
            start = content.find('export const llmParsedTickets: Ticket[] = ') + len('export const llmParsedTickets: Ticket[] = ')
            end = content.find(';', start)
            if end == -1:
                end = len(content)

            json_content = content[start:end].strip()
            llm_tickets = json.loads(json_content)

            print(f"   📄 tickets2.ts contains {len(llm_tickets)} LLM tickets")

            if llm_tickets:
                print("   🎫 Sample LLM ticket:")
                ticket = llm_tickets[0]
                print(f"      ID: {ticket['id']}, Title: {ticket['title'][:40]}...")
                print(f"      Status: {ticket['status']}, Module: {ticket['module']}")
                print(f"      Tags: {ticket['tags']}")

        except Exception as e:
            print(f"   ❌ Error reading frontend file: {e}")

        # Step 5: Instructions for testing
        print("\n📋 TESTING INSTRUCTIONS:")
        print("1. Start the frontend: cd frontend-up && npm run dev")
        print("2. Go to Settings page (/settings)")
        print("3. Try different data source options:")
        print("   - 'Combined': Should show both dummy + LLM tickets")
        print("   - 'LLM Only': Should show only LLM tickets (if any)")
        print("   - 'Dummy Only': Should show only sample tickets")
        print("4. Check the colored indicator in dashboard/tickets pages")
        print("5. Click the ⚙️ icon to go back to settings")

        print("\n🎯 EXPECTED BEHAVIOR:")
        print("- Page reloads when data source changes")
        print("- Dashboard shows current data source mode")
        print("- Tickets list reflects selected data source")
        print("- Settings persist in localStorage")

        print("\n" + "=" * 60)
        print("🎉 DATA SOURCE CONTROL TEST COMPLETE!")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_data_source_control())