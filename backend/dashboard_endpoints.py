#!/usr/bin/env python3
"""
Dashboard API Endpoints - Shows what the frontend calls
"""

def show_dashboard_endpoints():
    print("🎯 DASHBOARD API ENDPOINTS")
    print("=" * 50)
    print("When your dashboard opens, it will call these endpoints:")
    print()

    print("1. 📨 TICKETS LIST (Main dashboard view)")
    print("   GET /tickets?limit=100&skip=0")
    print("   - Loads all tickets for the tickets tab")
    print("   - Called when dashboard first loads")
    print("   - Returns: Array of ticket objects")
    print()

    print("2. 📊 ANALYTICS DATA (Analytics tab)")
    print("   GET /analytics/summary")
    print("   - Loads ticket statistics and charts")
    print("   - Called when switching to Analytics tab")
    print("   - Returns: Analytics data for charts")
    print()

    print("3. 📋 REPORTS DATA (Reports tab)")
    print("   GET /analytics/tickets")
    print("   - Loads detailed report data")
    print("   - Called when switching to Reports tab")
    print("   - Returns: Report data for export")
    print()

    print("4. 👤 USER INFO (Profile dropdown)")
    print("   GET /users/me")
    print("   - Loads current user information")
    print("   - Called on login/profile access")
    print("   - Returns: User profile data")
    print()

    print("🔧 ADDITIONAL ENDPOINTS (Available but not auto-called):")
    print()
    print("• POST /emails/fetch - Fetch new emails")
    print("• GET /emails/stats - Email processing stats")
    print("• GET /tickets/{id} - Single ticket details")
    print("• PUT /tickets/{id} - Update ticket")
    print("• POST /tickets - Create new ticket")
    print()

    print("💡 TO SEE THESE CALLS IN ACTION:")
    print("1. Start your backend: python run.py")
    print("2. Open browser dev tools (F12)")
    print("3. Go to Network tab")
    print("4. Load the dashboard")
    print("5. Watch the API calls appear")
    print()

    print("🔍 CURRENT STATUS:")
    print("✅ Backend endpoints are ready")
    print("✅ Frontend API service created")
    print("✅ Tickets component updated to use API")
    print("⏳ Need to add Azure AD token to frontend")
    print()

    print("🚀 NEXT STEPS:")
    print("1. Add your Azure AD token to frontend")
    print("2. Start backend: cd backend && python run.py")
    print("3. Start frontend: cd frontend && npm start")
    print("4. Open dashboard and check Network tab")

if __name__ == "__main__":
    show_dashboard_endpoints()