# ============================================
# SAP TICKET MANAGEMENT SYSTEM - Complete Setup Guide
# ============================================

## 🚀 System Overview

This system automatically processes SAP-related emails, uses LLM to analyze them, creates tickets in a local database, and dynamically updates the frontend based on configuration.

## 📋 Architecture

```
Email Source → LLM Analysis → Database → JSON Export → Frontend Display
     ↓            ↓            ↓          ↓            ↓
Microsoft Graph  GPT/OpenAI   SQLite   tickets2.ts   Dynamic Mode
```

## ⚙️ Configuration

### Backend Configuration (.env)
```bash
# LLM Setup
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-actual-api-key-here  # Replace with real key

# Data Export Mode
DATA_SOURCE_MODE=combined  # llm | combined | dummy

# Scheduler (runs every 1 minute)
SCHEDULER_ENABLED=true
```

### Frontend Configuration (frontend-up/.env.local)
```bash
# Data Display Mode
USE_DB=combined  # llm | normal | combined
```

## 🎯 How It Works

### Backend Flow:
1. **Scheduler runs every 1 minute**
2. **Fetches emails from last 24 hours** (mock or real)
3. **LLM analyzes for SAP relevance**
4. **Creates tickets in database** if SAP-related
5. **Exports to tickets2.ts** based on DATA_SOURCE_MODE

### Frontend Flow:
1. **Reads USE_DB from .env.local**
2. **Loads appropriate data**:
   - `llm` → only tickets2.ts
   - `normal` → only tickets.ts
   - `combined` → both files

## 🚦 Data Source Modes

### Backend DATA_SOURCE_MODE (controls tickets2.ts content):
- **`llm`**: Only LLM-parsed tickets
- **`combined`**: Dummy tickets + LLM tickets
- **`dummy`**: Only dummy tickets

### Frontend USE_DB (controls display):
- **`llm`**: Show only LLM data
- **`normal`**: Show only dummy data
- **`combined`**: Show both data sources

## 🛠️ Setup Instructions

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
# Edit .env with your LLM API key
# Run: python run.py
```

### 2. Frontend Setup
```bash
cd frontend-up
npm install
# Edit .env.local USE_DB setting
# Run: npm run dev
```

### 3. Test the System
```bash
cd backend
python test_complete_system.py
```

## 📊 Usage Examples

### Development Mode:
```
Backend .env: DATA_SOURCE_MODE=dummy
Frontend .env: USE_DB=normal
Result: Shows only sample tickets
```

### Production Mode:
```
Backend .env: DATA_SOURCE_MODE=llm + LLM_API_KEY=sk-...
Frontend .env: USE_DB=llm
Result: Shows only real LLM-processed tickets
```

### Mixed Mode:
```
Backend .env: DATA_SOURCE_MODE=combined + LLM_API_KEY=sk-...
Frontend .env: USE_DB=combined
Result: Shows sample + real tickets
```

## 🔧 API Endpoints

- `GET /tickets` - Get tickets
- `POST /tickets/sync-frontend` - Manual frontend sync
- `GET /analytics/dashboard` - Dashboard stats

## 📁 File Structure

```
backend/
├── .env                    # Backend config
├── ticket.db              # SQLite database
└── app/
    ├── core/config.py     # Configuration
    ├── services/          # Business logic
    └── routes/            # API endpoints

frontend-up/
├── .env.local            # Frontend config
└── src/
    ├── data/
    │   ├── tickets.ts    # Dummy data
    │   └── tickets2.ts   # LLM data (auto-generated)
    └── lib/
        └── ticket-service.ts  # Data loading logic
```

## 🎛️ Changing Data Sources

### To Change Backend Export:
1. Edit `backend/.env`
2. Change `DATA_SOURCE_MODE=llm|combined|dummy`
3. Restart backend

### To Change Frontend Display:
1. Edit `frontend-up/.env.local`
2. Change `USE_DB=llm|normal|combined`
3. Restart frontend

## 🔍 Monitoring

- **Backend logs**: Check console for processing status
- **Database**: Check `ticket.db` for stored tickets
- **Frontend**: Check browser console for data source info
- **Scheduler**: Runs every 1 minute, check logs

## 🚨 Troubleshooting

### No tickets appearing:
- Check LLM API key in backend .env
- Verify scheduler is running
- Check database for tickets

### Wrong data showing:
- Verify USE_DB in frontend .env.local
- Check DATA_SOURCE_MODE in backend .env
- Restart both services

### LLM not working:
- Replace `sk-your-api-key-here` with real API key
- Check API key validity
- Verify LLM_PROVIDER setting

## 🎉 Success Indicators

✅ **Backend**: "LLM configured" in startup logs
✅ **Scheduler**: "Started with email processing every 1 minute"
✅ **Database**: Tickets created with `source_email_id`
✅ **Frontend**: Correct data source indicator in UI
✅ **Integration**: tickets2.ts updates automatically

---

**The system is now fully automated and configurable!** 🎯</content>
<parameter name="filePath">c:\Dash_Board_Project\SYSTEM_README.md