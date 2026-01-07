# ============================================
# TICKET ROUTES - Ticket Endpoints
# ============================================

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.controllers import TicketController
from app.middleware import get_current_user, get_token
from app.schemas import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketDetailResponse,
    TicketListResponse,
    TicketLogResponse,
    TicketCommentCreate,
    TicketCommentUpdate,
    TicketCommentResponse,
    CurrentUser,
    MessageResponse
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new ticket.
    """
    controller = TicketController(db)
    return await controller.create_ticket(ticket_data, current_user)


@router.get("", response_model=TicketListResponse)
async def get_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assigned_to: Optional[int] = None,
    created_by: Optional[int] = None,
    search: Optional[str] = None,
    order_by: str = "created_at",
    order_desc: bool = True,
    fetch_emails: bool = Query(False, description="Trigger email fetching before getting tickets"),
    current_user: CurrentUser = Depends(get_current_user),
    token: str = Depends(get_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of tickets with filters.
    Optionally trigger email fetching first.
    """
    controller = TicketController(db)
    
    # Trigger email fetching if requested
    if fetch_emails:
        from app.controllers import EmailController
        email_controller = EmailController(db)
        await email_controller.trigger_email_fetch(
            access_token=token,
            current_user=current_user,
            days_back=1,
            max_emails=50,
            folder="inbox"
        )
    
    return await controller.get_tickets(
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        category=category,
        assigned_to=assigned_to,
        created_by=created_by,
        search=search,
        order_by=order_by,
        order_desc=order_desc
    )


@router.get("/recent", response_model=List[TicketResponse])
async def get_recent_tickets(
    limit: int = Query(10, ge=1, le=50),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get most recent tickets.
    """
    controller = TicketController(db)
    return await controller.get_recent_tickets(limit)


@router.get("/my", response_model=TicketListResponse)
async def get_my_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get tickets assigned to or created by current user.
    """
    controller = TicketController(db)
    return await controller.get_my_tickets(current_user, skip, limit)


@router.get("/by-ticket-id/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket_by_ticket_id(
    ticket_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get ticket by ticket_id (e.g., T-001).
    """
    controller = TicketController(db)
    return await controller.get_ticket_by_ticket_id(ticket_id)


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(
    ticket_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get ticket by ID with full details.
    """
    controller = TicketController(db)
    return await controller.get_ticket(ticket_id)


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    update_data: TicketUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a ticket.
    """
    controller = TicketController(db)
    return await controller.update_ticket(ticket_id, update_data, current_user)


@router.delete("/{ticket_id}", response_model=MessageResponse)
async def delete_ticket(
    ticket_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a ticket (admin only).
    """
    controller = TicketController(db)
    return await controller.delete_ticket(ticket_id, current_user)


# ============================================
# Ticket Logs
# ============================================

@router.get("/{ticket_id}/logs", response_model=List[TicketLogResponse])
async def get_ticket_logs(
    ticket_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get logs for a ticket.
    """
    controller = TicketController(db)
    return await controller.get_ticket_logs(ticket_id)


# ============================================
# Ticket Comments
# ============================================

@router.post("/{ticket_id}/comments", response_model=TicketCommentResponse)
async def add_comment(
    ticket_id: int,
    comment_data: TicketCommentCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a comment to a ticket.
    """
    controller = TicketController(db)
    return await controller.add_comment(ticket_id, comment_data, current_user)


@router.patch("/comments/{comment_id}", response_model=TicketCommentResponse)
async def update_comment(
    comment_id: int,
    update_data: TicketCommentUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a comment.
    """
    controller = TicketController(db)
    return await controller.update_comment(comment_id, update_data, current_user)


@router.delete("/comments/{comment_id}", response_model=MessageResponse)
async def delete_comment(
    comment_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a comment.
    """
    controller = TicketController(db)
    return await controller.delete_comment(comment_id, current_user)


@router.post("/sync-frontend", response_model=MessageResponse)
async def sync_frontend_tickets(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync tickets from database to frontend tickets2.ts file.
    This endpoint updates the LLM-parsed tickets file used by the frontend.
    """
    from app.services.ticket_service import TicketService
    
    ticket_service = TicketService(db)
    count = await ticket_service.update_frontend_tickets_file()
    
    return {
        "message": f"Successfully synced {count} tickets to frontend file",
        "data": {"tickets_synced": count}
    }
