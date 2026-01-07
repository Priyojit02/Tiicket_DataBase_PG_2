#!/usr/bin/env python
"""
Quick Status Check Script
Checks if email processing and ticket creation systems are ready
"""

import asyncio
import os
import sys
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings


async def check_system_status():
    """Check the status of all email processing components"""
    print("🔍 Email Processing System Status Check")
    print("=" * 50)

    # Check 1: Environment Configuration
    print("📋 1. Configuration Status:")
    checks = [
        ("LLM API Key", settings.is_llm_configured, f"Provider: {settings.llm_provider}"),
        ("Azure Client ID", bool(settings.azure_client_id and settings.azure_client_id != "YOUR_TICKET_MANAGEMENT_SYSTEM_CLIENT_ID"), "Azure AD configured"),
        ("Database", True, "SQLite (always ready)"),
        ("Scheduler", settings.scheduler_enabled, "Auto-processing enabled"),
    ]

    for check_name, status, details in checks:
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {check_name}: {details}")

    # Check 2: Required Files
    print("\n📁 2. Required Files:")
    required_files = [
        ("Backend .env", ".env", "contains API keys and settings"),
        ("Frontend .env.local", "../frontend-up/.env.local", "contains frontend config"),
        ("Database file", "ticket.db", "SQLite database"),
    ]

    for file_name, file_path, description in required_files:
        exists = os.path.exists(file_path)
        status_icon = "✅" if exists else "❌"
        print(f"   {status_icon} {file_name}: {description}")

    # Check 3: Data Source Mode
    print("\n🎯 3. Data Source Configuration:")
    frontend_env = os.path.join("..", "frontend-up", ".env.local")
    if os.path.exists(frontend_env):
        with open(frontend_env, 'r') as f:
            content = f.read()
            if 'NEXT_PUBLIC_USE_MOCK_DATA=true' in content:
                print("   ✅ Frontend: Using MOCK data (tickets.ts)")
            elif 'NEXT_PUBLIC_USE_MOCK_DATA=false' in content:
                print("   ✅ Frontend: Using REAL backend API")
            else:
                print("   ⚠️  Frontend: USE_MOCK_DATA not set")

            if 'NEXT_PUBLIC_DATA_SOURCE=normal' in content:
                print("   ✅ Data Mode: NORMAL (sample tickets only)")
            elif 'NEXT_PUBLIC_DATA_SOURCE=llm' in content:
                print("   ✅ Data Mode: LLM (processed emails only)")
            elif 'NEXT_PUBLIC_DATA_SOURCE=combined' in content:
                print("   ✅ Data Mode: COMBINED (sample + processed)")
    else:
        print("   ❌ Frontend config not found")

    # Check 4: Database Status
    print("\n💾 4. Database Status:")
    try:
        from app.core.database import init_db, AsyncSessionLocal
        await init_db()

        async with AsyncSessionLocal() as db:
            from sqlalchemy import text

            # Count tickets
            result = await db.execute(text("SELECT COUNT(*) FROM tickets"))
            ticket_count = result.scalar()
            print(f"   ✅ Database connected: {ticket_count} tickets")

            # Count users
            result = await db.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"   ✅ Users: {user_count} registered")

    except Exception as e:
        print(f"   ❌ Database error: {e}")

    # Check 5: Test Files Available
    print("\n🧪 5. Test Scripts Available:")
    test_files = [
        ("test_email_processing_complete.py", "Full pipeline test"),
        ("test_system_logic.py", "System logic test"),
        ("test_trigger_emails.py", "Email triggering test"),
        ("test_email.py", "Basic email fetch test"),
    ]

    for filename, description in test_files:
        exists = os.path.exists(filename)
        status_icon = "✅" if exists else "❌"
        print(f"   {status_icon} {filename}: {description}")

    print("\n" + "=" * 50)
    print("🎯 Quick Actions:")
    print("=" * 50)

    if not settings.is_llm_configured:
        print("⚠️  LLM not configured - add LLM_API_KEY to .env for real processing")

    if not settings.scheduler_enabled:
        print("⚠️  Scheduler disabled - set SCHEDULER_ENABLED=true for auto-processing")

    print("✅ Run: python test_email_processing_complete.py (full test)")
    print("✅ Run: python run.py (start backend)")
    print("✅ Visit: http://localhost:3000 (frontend)")

    print(f"\n⏰ Status check completed at: {datetime.now()}")


if __name__ == "__main__":
    asyncio.run(check_system_status())