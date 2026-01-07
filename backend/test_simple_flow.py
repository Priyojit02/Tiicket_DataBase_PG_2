import asyncio
import json
import os
from app.services.email_processor import EmailProcessor
from app.services.ticket_service import TicketService
from app.core.database import AsyncSessionLocal, init_db
from app.repositories.ticket_repository import TicketRepository

async def test_flow():
    print("Testing complete flow...")

    # Initialize database
    await init_db()

    async with AsyncSessionLocal() as db:
        # Process emails
        processor = EmailProcessor(db, use_mock=True)
        result = await processor.process_daily_emails(
            days_back=2,
            max_emails=4,
            auto_create_tickets=True
        )

        print(f"Processing results: {result}")

        # Update frontend file
        ticket_service = TicketService(db)
        count = await ticket_service.update_frontend_tickets_file()
        print(f"Updated frontend with {count} tickets")

        # Check file
        frontend_path = os.path.join(os.path.dirname(__file__), '../frontend-up/src/data/tickets2.ts')
        if os.path.exists(frontend_path):
            with open(frontend_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print("Frontend file updated successfully")
            print(f"File contains: {len(content)} characters")
        else:
            print("Frontend file not found")

if __name__ == "__main__":
    asyncio.run(test_flow())</content>
<parameter name="filePath">c:\Dash_Board_Project\backend\test_simple_flow.py