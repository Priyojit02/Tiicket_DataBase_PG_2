# SAP Ticket Management System - API Flow Documentation

## 📋 System Overview

This is a comprehensive SAP ticket management system that automatically creates support tickets from emails using AI/LLM analysis. The system consists of:

- **Frontend**: Next.js React application with Azure AD authentication
- **Backend**: FastAPI server with async SQLAlchemy ORM
- **Database**: SQLite (development) / PostgreSQL (production)
- **Email Integration**: Microsoft Graph API with SSO
- **AI Processing**: Multi-provider LLM integration (OpenAI, Anthropic, etc.)

---

## 🏗️ Architecture Overview

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   Next.js       │◄──────────────►│    FastAPI       │
│   Frontend      │   APIs         │    Backend       │
│   (React)       │                │   (Python)       │
└─────────────────┘                └─────────────────┘
         │                                 │
         │ Azure AD Token                 │ Microsoft Graph API
         ▼                                 ▼
┌─────────────────┐    WebSocket     ┌─────────────────┐
│   MSAL Browser  │◄───────────────►│   Azure AD       │
│   Library       │                 │   (OAuth 2.0)    │
└─────────────────┘                 └─────────────────┘
                                              │
                                              ▼
                                   ┌─────────────────┐
                                   │   Exchange      │
                                   │   Online       │
                                   └─────────────────┘
```

---

## 🔐 Authentication Flow

### Frontend Authentication (MSAL)

```typescript
// frontend-up/src/lib/auth-service.ts
1. initializeMsal() → Creates PublicClientApplication
2. loginWithPopup() → Azure AD login popup
3. acquireTokenSilent() → Get access token silently
4. getAccessToken() → Returns Bearer token for API calls
```

### Backend Token Validation

```python
# backend/app/middleware/auth_middleware.py
1. get_token() → Extract Bearer token from Authorization header
2. verify_azure_token() → Validate with Microsoft Graph API (/me)
3. get_current_user() → Get/create user in database
4. Return CurrentUser object with id, email, name, is_admin
```

---

## 📡 API Communication Flow

### Frontend → Backend API Calls

#### 1. Ticket Creation (Manual)

```typescript
// User fills form → frontend-up/src/app/(dashboard)/tickets/new/page.tsx
handleSubmit() → createTicket(payload) → ticketsApi.createTicket(data)
    ↓ HTTP POST /api/v1/tickets
    ↓ Authorization: Bearer <azure_token>
    ↓ Body: { title, description, priority, category, assigned_to }
```

#### 2. Email Processing Trigger

```typescript
// User clicks sync → frontend-up/src/lib/api-service.ts
emailService.fetchEmails() → emailsApi.fetch()
    ↓ HTTP POST /api/v1/emails/fetch
    ↓ Authorization: Bearer <azure_token>
    ↓ Body: { days_back: 1, max_emails: 100, folder: "inbox" }
```

#### 3. Ticket Listing

```typescript
// Dashboard loads → frontend-up/src/hooks/useTickets.ts
loadTickets() → ticketsApi.getTickets({ limit: 20 })
    ↓ HTTP GET /api/v1/tickets?limit=20
    ↓ Authorization: Bearer <azure_token>
```

### Backend Route Handling

```python
# backend/app/routes/ticket_routes.py
@router.post("", response_model=TicketResponse)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    controller = TicketController(db)
    return await controller.create_ticket(ticket_data, current_user)
```

---

## 🔄 Backend Internal Method Calls

### Manual Ticket Creation Flow

```
HTTP POST /api/v1/tickets
    ↓
ticket_routes.py: create_ticket()
    ↓
TicketController.create_ticket()
    ↓
TicketService.create_ticket()
    ├─► TicketRepository.get_next_ticket_id() → "T-001"
    ├─► TicketRepository.create({...}) → INSERT INTO tickets
    ├─► TicketService._create_log() → INSERT INTO ticket_logs
    ├─► TicketRepository.get_with_details() → SELECT with JOINs
    └─► TicketService.update_frontend_tickets_file()
        ↓
    Return TicketResponse
```

### Email-Driven Ticket Creation Flow

```
Email Processing Trigger
    ↓
email_routes.py: trigger_email_fetch()
    ↓
EmailController.trigger_email_fetch()
    ↓
EmailProcessor.process_daily_emails()
    ├─► EmailService.fetch_emails_with_token() → Microsoft Graph API
    ├─► EmailService.mark_processed() → UPDATE email_sources
    └─► EmailProcessor._process_single_email()
        ├─► LLMService.analyze_email() → AI analysis
        └─► EmailProcessor._create_ticket_from_analysis()
            ↓
        TicketService.create_ticket_from_email()
            ├─► TicketRepository.get_next_ticket_id() → "T-002"
            ├─► TicketRepository.create({...}) → INSERT INTO tickets
            ├─► TicketService._create_log() → INSERT INTO ticket_logs
            └─► TicketService.update_frontend_tickets_file()
```

---

## 📧 Email Processing Pipeline

### 1. Email Fetching

```python
# backend/app/services/email_service.py
async def fetch_emails_with_token():
    # Microsoft Graph API call
    graph_url = f"https://graph.microsoft.com/v1.0/me/mailFolders/{folder}/messages"
    params = {
        "$top": max_emails,
        "$orderby": "receivedDateTime desc",
        "$filter": f"receivedDateTime ge {since_date}",
        "$select": "id,subject,bodyPreview,body,from,toRecipients,receivedDateTime,hasAttachments,internetMessageId"
    }

    # Deduplication check
    message_id = msg.get("internetMessageId") or msg.get("id")
    if await self.email_repo.message_exists(message_id):
        continue  # Skip duplicate

    # Store email
    email_source = await self.email_repo.create({...})
```

### 2. LLM Analysis

```python
# backend/app/services/email_processor.py
async def _process_single_email():
    # Analyze with LLM
    analysis = await self.llm_service.analyze_email(
        subject=subject,
        body=body,
        from_address=from_address
    )

    # Decision logic
    if analysis.is_sap_related and analysis.confidence >= 0.6:
        ticket = await self._create_ticket_from_analysis(...)
```

### 3. Ticket Generation

```python
# backend/app/services/email_processor.py
async def _create_ticket_from_analysis():
    # Build ticket data
    title = analysis.suggested_title or subject[:200]
    description = f"**Email from:** {from_address}\n\n{body[:2000]}"

    # Create ticket
    ticket = await self.ticket_service.create_ticket_from_email(
        title=title,
        description=description,
        category=analysis.detected_category,
        priority=analysis.suggested_priority,
        source_email_id=email_source.message_id,
        created_by=system_user.id,
        llm_confidence=analysis.confidence
    )
```

---

## 🗄️ Database Operations

### Repository Pattern

```python
# backend/app/repositories/base_repository.py
class BaseRepository(Generic[ModelType]):
    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)  # Create model instance
        self.db.add(db_obj)            # Add to session
        await self.db.flush()          # Execute INSERT
        await self.db.refresh(db_obj)  # Reload from DB
        return db_obj

# backend/app/repositories/ticket_repository.py
class TicketRepository(BaseRepository[Ticket]):
    async def get_next_ticket_id(self) -> str:
        result = await self.db.execute(
            select(func.count()).select_from(Ticket)
        )
        count = result.scalar_one()
        return f"T-{str(count + 1).zfill(3)}"
```

### Transaction Management

```python
# backend/app/core/database.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

---

## 🔄 Data Synchronization

### Frontend-Backend Sync

```python
# backend/app/services/ticket_service.py
async def update_frontend_tickets_file():
    """Export tickets from DB to frontend format"""
    tickets = await self.ticket_repo.get_all_with_details()

    # Convert to frontend format
    frontend_tickets = []
    for ticket in tickets:
        frontend_tickets.append({
            "id": ticket.id,
            "ticketId": ticket.ticket_id,
            "title": ticket.title,
            "description": ticket.description,
            "status": ticket.status.value,
            "priority": ticket.priority.value,
            "category": ticket.category.value,
            "createdOn": ticket.created_at.isoformat(),
            "updatedOn": ticket.updated_at.isoformat(),
            "createdBy": ticket.created_by_user.name if ticket.created_by_user else "Unknown",
            "assignedTo": ticket.assigned_to_user.name if ticket.assigned_to_user else "Unassigned",
        })

    # Write to frontend file
    file_path = Path("../../frontend-up/src/data/tickets2.ts")
    with open(file_path, 'w') as f:
        f.write(f"export const ticketsData = {json.dumps(frontend_tickets, indent=2)};")
```

---

## 📁 File Structure & Dependencies

### Backend Structure
```
backend/
├── app/
│   ├── core/           # Config, database, logging
│   ├── middleware/     # Auth, CORS, error handling
│   ├── models/         # SQLAlchemy models
│   ├── repositories/   # Database operations
│   ├── routes/         # API endpoints
│   ├── schemas/        # Pydantic models
│   ├── services/       # Business logic
│   └── controllers/    # Route handlers
├── database/           # Schema, seeds
└── requirements.txt    # Python dependencies
```

### Frontend Structure
```
frontend-up/
├── src/
│   ├── app/            # Next.js app router
│   ├── components/     # React components
│   ├── hooks/          # Custom React hooks
│   ├── lib/            # Utilities, API clients
│   └── types/          # TypeScript types
├── public/             # Static assets
└── package.json        # Node dependencies
```

### Dependency Injection Chain

```
Routes (FastAPI)
    ↓ Depends(get_db)
Database Session (AsyncSession)
    ↓
Controllers
    ↓ self.service = Service(db)
Services
    ↓ self.repo = Repository(db)
Repositories
    ↓ self.db = db
BaseRepository
    ↓ SQLAlchemy operations
```

---

## 🚀 Startup Sequence

### Backend Startup
```bash
cd backend
python run.py
```
```python
# backend/run.py
1. uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ↓
# backend/app/main.py
2. create_tables() → Alembic migrations
3. app = FastAPI() → Initialize FastAPI
4. include_routers() → Register all routes
5. add_middleware() → CORS, auth, error handling
6. start_server() → Uvicorn server
```

### Frontend Startup
```bash
cd frontend-up
npm run dev
```
```typescript
// frontend-up/src/app/layout.tsx
1. <Providers> → AuthProvider, context setup
   ↓
// frontend-up/src/hooks/useAuth.tsx
2. initializeMsal() → Azure AD setup
3. check authentication state
4. Load dashboard or redirect to login
```

---

## 🔍 Key Integration Points

### 1. Authentication Bridge
- **Frontend**: MSAL Browser → Azure AD → Access Token
- **Backend**: Token validation → Microsoft Graph API → User info
- **Database**: User lookup/create → Return CurrentUser

### 2. Email Processing Bridge
- **Frontend**: Button click → API call with token
- **Backend**: Token → Microsoft Graph API → Email fetch
- **AI**: Email analysis → Ticket creation decision
- **Database**: Email storage → Ticket creation → Log creation

### 3. Data Synchronization
- **Backend**: Database changes → Export to frontend format
- **Frontend**: Import tickets2.ts → Display in UI
- **Real-time**: Auto-sync every 30 seconds

---

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**: Check Azure AD credentials in `.env`
2. **API calls fail**: Verify Azure token is valid (expires every 1 hour)
3. **Email processing fails**: Check LLM API keys and Microsoft Graph permissions
4. **Database errors**: Ensure SQLite file permissions or PostgreSQL connection

### Debug Commands

```bash
# Test backend API
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/tickets

# Check email processing
python backend/test_trigger_emails.py

# View database
sqlite3 backend/ticket.db "SELECT * FROM tickets LIMIT 5;"

# Check logs
tail -f backend/logs/app.log
```

---

## 📚 API Reference

### Authentication Endpoints
- `POST /auth/login` - Login with Azure token
- `GET /auth/me` - Get current user profile
- `GET /auth/verify` - Verify token validity

### Ticket Endpoints
- `GET /tickets` - List tickets with filtering
- `POST /tickets` - Create new ticket
- `GET /tickets/{id}` - Get ticket details
- `PUT /tickets/{id}` - Update ticket
- `DELETE /tickets/{id}` - Delete ticket

### Email Endpoints
- `POST /emails/fetch` - Trigger email processing
- `GET /emails/stats` - Get processing statistics
- `GET /emails/recent` - Get recent emails

### Admin Endpoints
- `GET /admin/users` - List all users
- `POST /admin/admins/add` - Add admin privileges
- `GET /analytics/dashboard` - Get dashboard analytics

---

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Azure AD
AZURE_CLIENT_ID=your_client_id
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_SECRET=your_client_secret

# LLM APIs
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Database
DATABASE_URL=sqlite+aiosqlite:///./ticket.db
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_AZURE_CLIENT_ID=your_client_id
NEXT_PUBLIC_AZURE_TENANT_ID=your_tenant_id
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_DATA_SOURCE=combined
NEXT_PUBLIC_AUTO_SYNC_ENABLED=true
```

---

## 🎯 Development Workflow

1. **Setup**: Clone repo, install dependencies, configure Azure AD app
2. **Backend**: `cd backend && python run.py`
3. **Frontend**: `cd frontend-up && npm run dev`
4. **Login**: Use Microsoft account to authenticate
5. **Test**: Create manual tickets or trigger email processing
6. **Monitor**: Check logs and database for debugging

This documentation provides a complete understanding of how APIs are called throughout the SAP Ticket Management System, from frontend user interactions to backend database operations.</content>
<parameter name="filePath">c:\Dash_Board_Project\API_FLOW_README.md