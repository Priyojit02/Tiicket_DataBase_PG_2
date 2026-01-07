# Email API Testing Guide
# Replace YOUR_TOKEN with your actual Azure AD access token

echo "🚀 EMAIL API TESTING WITH CURL"
echo "================================"

# 1. Fetch emails from inbox (received emails)
echo -e "\n1. 📨 FETCH INBOX EMAILS (received emails)"
echo "curl -X POST \"http://localhost:8000/emails/fetch?folder=inbox&days_back=1&max_emails=50\" \\"
echo "  -H \"Authorization: Bearer YOUR_TOKEN\""

# 2. Fetch emails from sent items (sent emails)
echo -e "\n2. 📤 FETCH SENT EMAILS (emails you sent)"
echo "curl -X POST \"http://localhost:8000/emails/fetch?folder=sentitems&days_back=1&max_emails=50\" \\"
echo "  -H \"Authorization: Bearer YOUR_TOKEN\""

# 3. Get email statistics
echo -e "\n3. 📊 GET EMAIL STATISTICS"
echo "curl -X GET \"http://localhost:8000/emails/stats\" \\"
echo "  -H \"Authorization: Bearer YOUR_TOKEN\""

# 4. Get recent emails
echo -e "\n4. 🕐 GET RECENT EMAILS"
echo "curl -X GET \"http://localhost:8000/emails/recent?limit=10\" \\"
echo "  -H \"Authorization: Bearer YOUR_TOKEN\""

# 5. Get unprocessed emails
echo -e "\n5. ⏳ GET UNPROCESSED EMAILS"
echo "curl -X GET \"http://localhost:8000/emails/unprocessed?limit=20\" \\"
echo "  -H \"Authorization: Bearer YOUR_TOKEN\""

# 6. Get emails by SAP category
echo -e "\n6. 📁 GET EMAILS BY SAP MODULE"
echo "curl -X GET \"http://localhost:8000/emails/by-category/MM?limit=10\" \\"
echo "  -H \"Authorization: Bearer YOUR_TOKEN\""

echo -e "\n🎯 QUICK TEST COMMANDS:"
echo "========================"
echo "# Test inbox emails:"
echo "curl -X POST \"http://localhost:8000/emails/fetch?folder=inbox&days_back=7\" -H \"Authorization: Bearer YOUR_TOKEN\""
echo ""
echo "# Test sent emails:"
echo "curl -X POST \"http://localhost:8000/emails/fetch?folder=sentitems&days_back=7\" -H \"Authorization: Bearer YOUR_TOKEN\""
echo ""
echo "# Check what happened:"
echo "curl -X GET \"http://localhost:8000/emails/recent\" -H \"Authorization: Bearer YOUR_TOKEN\""