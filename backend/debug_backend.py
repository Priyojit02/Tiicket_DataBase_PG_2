#!/usr/bin/env python
"""
Debug script to check what's causing 500 errors
"""

import asyncio
import sys
import os
import traceback

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

async def debug_backend():
    """Debug backend startup issues"""
    print("🔍 Debugging Backend 500 Error")
    print("=" * 50)

    try:
        # Test 1: Import core modules
        print("📦 Testing imports...")
        from app.core.config import settings
        print("✅ Config imported")

        from app.core.database import init_db, AsyncSessionLocal
        print("✅ Database imported")

        # Test 2: Check configuration
        print("\n⚙️  Checking configuration...")
        print(f"   Database URL: {settings.database_url}")
        print(f"   Debug mode: {settings.debug}")
        print(f"   LLM configured: {settings.is_llm_configured}")

        # Test 3: Initialize database
        print("\n💾 Testing database initialization...")
        await init_db()
        print("✅ Database initialized")

        # Test 4: Check database connection
        print("   Testing database connection...")
        async with AsyncSessionLocal() as db:
            from sqlalchemy import text
            result = await db.execute(text("SELECT 1"))
            print("✅ Database connection working")

            # Check if tables exist
            result = await db.execute(text("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """))
            tables = result.fetchall()
            print(f"✅ Found {len(tables)} tables: {[t[0] for t in tables]}")

        # Test 5: Import routes
        print("\n🛣️  Testing route imports...")
        from app.routes import register_routes
        print("✅ Routes imported")

        # Test 6: Import controllers
        print("   Testing controller imports...")
        from app.controllers import TicketController
        print("✅ Controllers imported")

        # Test 7: Import services
        print("   Testing service imports...")
        from app.services import EmailProcessor
        print("✅ Services imported")

        print("\n" + "=" * 50)
        print("🎉 All imports successful!")
        print("Backend should start without 500 errors.")
        print("=" * 50)

        print("\n💡 If still getting 500 errors:")
        print("1. Check browser console for detailed error messages")
        print("2. Check backend terminal for stack traces")
        print("3. Try restarting the backend: python run.py")
        print("4. Check if all dependencies are installed: pip install -r requirements.txt")

    except Exception as e:
        print(f"\n❌ Error found: {e}")
        print("\n🔍 Full traceback:")
        traceback.print_exc()

        print("\n" + "=" * 50)
        print("🔧 Possible fixes:")
        if "ModuleNotFoundError" in str(e):
            print("• Install missing dependencies: pip install -r requirements.txt")
        elif "database" in str(e).lower():
            print("• Check database configuration in .env")
            print("• Delete ticket.db and restart to recreate tables")
        elif "azure" in str(e).lower():
            print("• Check Azure AD configuration in .env")
        else:
            print("• Check the full error traceback above")
        print("=" * 50)

if __name__ == "__main__":
    asyncio.run(debug_backend())