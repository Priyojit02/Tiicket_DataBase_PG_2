# ============================================
# EXPORT TICKETS FROM SQLITE TO FRONTEND
# ============================================
# This script exports tickets from ticket.db (SQLite) to tickets2.ts for frontend-up

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import init_db, AsyncSessionLocal
from app.services.ticket_service import TicketService


async def export_tickets_to_frontend():
    """Export all tickets from SQLite database to frontend tickets2.ts file"""
    print("🚀 Starting ticket export from SQLite to frontend...")

    try:
        # Initialize database
        print("📊 Initializing SQLite database...")
        await init_db()

        # Create ticket service
        async with AsyncSessionLocal() as db:
            ticket_service = TicketService(db)

            # Export tickets to frontend format
            print("📤 Exporting tickets from database to tickets2.ts...")
            ticket_count = await ticket_service.update_frontend_tickets_file()

            print(f"✅ Successfully exported {ticket_count} tickets to frontend-up/src/data/tickets2.ts")
            print("🎯 Frontend will now use data from SQLite database via tickets2.ts")

    except Exception as e:
        print(f"❌ Error during export: {e}")
        return False

    return True


if __name__ == "__main__":
    # Run the export
    success = asyncio.run(export_tickets_to_frontend())

    if success:
        print("\n🎉 Export completed successfully!")
        print("📋 Next steps:")
        print("   1. Start the backend: python run.py")
        print("   2. Start the frontend: cd frontend-up && npm run dev")
        print("   3. Frontend will load tickets from tickets2.ts (SQLite data)")
    else:
        print("\n💥 Export failed!")
        sys.exit(1)