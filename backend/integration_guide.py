#!/usr/bin/env python3
"""
Backend-Frontend Integration Guide
Complete setup for connecting React frontend to FastAPI backend
"""

def show_integration_steps():
    print("🔗 BACKEND-FRONTEND INTEGRATION GUIDE")
    print("=" * 60)

    print("✅ COMPLETED INTEGRATION STEPS:")
    print("1. ✅ Created API service (frontend/src/services/apiService.js)")
    print("2. ✅ Updated Tickets component to use backend API")
    print("3. ✅ Integrated Azure AD token authentication")
    print("4. ✅ CORS configured for localhost:3000")
    print()

    print("🚀 TO COMPLETE THE INTEGRATION:")
    print()

    print("STEP 1: START BACKEND")
    print("cd backend")
    print("python run.py")
    print("✅ Backend will run on http://localhost:8000")
    print()

    print("STEP 2: START FRONTEND")
    print("cd frontend")
    print("npm install  # if not done already")
    print("npm start")
    print("✅ Frontend will run on http://localhost:3000")
    print()

    print("STEP 3: TEST THE CONNECTION")
    print("1. Open browser to http://localhost:3000")
    print("2. Login with Azure AD")
    print("3. Dashboard should load tickets from backend")
    print("4. Check browser DevTools → Network tab")
    print()

    print("🔍 WHAT HAPPENS WHEN DASHBOARD LOADS:")
    print("1. User logs in → Gets Azure AD token")
    print("2. Dashboard loads → Calls GET /tickets")
    print("3. Backend validates token → Returns ticket data")
    print("4. Frontend displays real tickets from database")
    print()

    print("📡 API CALLS THE DASHBOARD MAKES:")
    print("• GET /tickets?limit=100 - Main ticket list")
    print("• GET /users/me - User profile info")
    print("• GET /analytics/summary - Analytics data (when tab clicked)")
    print()

    print("🔧 TROUBLESHOOTING:")
    print("• 'CORS error' → Check backend CORS settings")
    print("• '401 Unauthorized' → Check Azure AD token")
    print("• 'Failed to load tickets' → Check backend is running")
    print("• 'No tickets shown' → Check database has data")
    print()

    print("🧪 TEST INDIVIDUAL ENDPOINTS:")
    print("# Get tickets (replace YOUR_TOKEN):")
    print('curl -X GET "http://localhost:8000/tickets?limit=5" \\')
    print('  -H "Authorization: Bearer YOUR_TOKEN"')
    print()
    print("# Test CORS:")
    print('curl -X OPTIONS "http://localhost:8000/tickets" \\')
    print('  -H "Origin: http://localhost:3000" \\')
    print('  -H "Access-Control-Request-Method: GET"')
    print()

    print("🎯 CURRENT STATUS:")
    print("✅ API Service: Created and configured")
    print("✅ Authentication: Azure AD token integrated")
    print("✅ CORS: Configured for frontend origin")
    print("✅ Tickets Component: Updated to use API")
    print("⏳ Ready to test: Start both servers and login")

if __name__ == "__main__":
    show_integration_steps()