# ============================================
# TICKET REPOSITORY - Database Operations for Tickets
# ============================================

from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from app.repositories.base_repository import BaseRepository
from app.models import Ticket, TicketLog, TicketComment, Attachment, TicketStatus, TicketPriority, TicketCategory


class TicketRepository(BaseRepository[Ticket]):
    """Repository for Ticket model operations"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Ticket, db)
    
    async def get_by_ticket_id(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by ticket_id (T-001 format)"""
        result = await self.db.execute(
            select(Ticket)
            .options(
                selectinload(Ticket.created_by_user),
                selectinload(Ticket.assigned_to_user),
            )
            .where(Ticket.ticket_id == ticket_id)
        )
        return result.scalar_one_or_none()
    
    async def get_with_details(self, id: int) -> Optional[Ticket]:
        """Get ticket with all related data (logs, comments, attachments)"""
        result = await self.db.execute(
            select(Ticket)
            .options(
                selectinload(Ticket.created_by_user),
                selectinload(Ticket.assigned_to_user),
                selectinload(Ticket.logs).selectinload(TicketLog.user),
                selectinload(Ticket.comments).selectinload(TicketComment.author),
                selectinload(Ticket.attachments),
            )
            .where(Ticket.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_paginated(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        category: Optional[TicketCategory] = None,
        assigned_to: Optional[int] = None,
        created_by: Optional[int] = None,
        search: Optional[str] = None,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> Tuple[List[Ticket], int]:
        """Get paginated tickets with filters"""
        query = select(Ticket).options(
            selectinload(Ticket.created_by_user),
            selectinload(Ticket.assigned_to_user),
        )
        count_query = select(func.count()).select_from(Ticket)
        
        # Apply filters
        filters = []
        if status:
            filters.append(Ticket.status == status)
        if priority:
            filters.append(Ticket.priority == priority)
        if category:
            filters.append(Ticket.category == category)
        if assigned_to:
            filters.append(Ticket.assigned_to == assigned_to)
        if created_by:
            filters.append(Ticket.created_by == created_by)
        if search:
            search_term = f"%{search.lower()}%"
            filters.append(
                or_(
                    func.lower(Ticket.title).like(search_term),
                    func.lower(Ticket.description).like(search_term),
                    func.lower(Ticket.ticket_id).like(search_term)
                )
            )
        
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()
        
        # Apply ordering
        order_column = getattr(Ticket, order_by, Ticket.created_at)
        if order_desc:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(order_column)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        tickets = list(result.scalars().all())
        
        return tickets, total
    
    async def get_next_ticket_id(self) -> str:
        """Generate the next ticket ID (T-001 format)"""
        result = await self.db.execute(
            select(func.count()).select_from(Ticket)
        )
        count = result.scalar_one()
        return f"T-{str(count + 1).zfill(3)}"
    
    async def get_by_status(self, status: TicketStatus) -> List[Ticket]:
        """Get all tickets by status"""
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.status == status)
            .order_by(desc(Ticket.created_at))
        )
        return list(result.scalars().all())
    
    async def get_user_tickets(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Ticket], int]:
        """Get tickets assigned to or created by a user"""
        query = select(Ticket).options(
            selectinload(Ticket.created_by_user),
            selectinload(Ticket.assigned_to_user),
        ).where(
            or_(
                Ticket.assigned_to == user_id,
                Ticket.created_by == user_id
            )
        ).order_by(desc(Ticket.created_at))
        
        count_query = select(func.count()).select_from(Ticket).where(
            or_(
                Ticket.assigned_to == user_id,
                Ticket.created_by == user_id
            )
        )
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()
        
        result = await self.db.execute(query.offset(skip).limit(limit))
        tickets = list(result.scalars().all())
        
        return tickets, total
    
    async def get_recent_tickets(self, limit: int = 10) -> List[Ticket]:
        """Get most recent tickets"""
        result = await self.db.execute(
            select(Ticket)
            .options(
                selectinload(Ticket.created_by_user),
                selectinload(Ticket.assigned_to_user),
            )
            .order_by(desc(Ticket.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_all_with_details(self) -> List[Ticket]:
        """Get all tickets with user details for frontend export"""
        result = await self.db.execute(
            select(Ticket)
            .options(
                selectinload(Ticket.created_by_user),
                selectinload(Ticket.assigned_to_user),
            )
            .order_by(desc(Ticket.created_at))
        )
        return list(result.scalars().all())
    
    async def update_status(
        self,
        ticket_id: int,
        status: TicketStatus,
        resolved_at: Optional[datetime] = None
    ) -> Optional[Ticket]:
        """Update ticket status"""
        update_data = {"status": status}
        if status == TicketStatus.RESOLVED and resolved_at:
            update_data["resolved_at"] = resolved_at
        return await self.update(ticket_id, update_data)
    
    async def get_status_counts(self) -> dict:
        """Get count of tickets by status"""
        result = await self.db.execute(
            select(Ticket.status, func.count(Ticket.id))
            .group_by(Ticket.status)
        )
        return {status.value: count for status, count in result.all()}
    
    async def get_priority_counts(self) -> dict:
        """Get count of tickets by priority"""
        result = await self.db.execute(
            select(Ticket.priority, func.count(Ticket.id))
            .group_by(Ticket.priority)
        )
        return {priority.value: count for priority, count in result.all()}
    
    async def get_category_counts(self) -> dict:
        """Get count of tickets by category"""
        result = await self.db.execute(
            select(Ticket.category, func.count(Ticket.id))
            .group_by(Ticket.category)
        )
        return {category.value: count for category, count in result.all()}
    
    async def get_daily_ticket_counts(self, days: int = 30) -> List[dict]:
        """Get ticket counts for the last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(
                func.date(Ticket.created_at).label("date"),
                func.count(Ticket.id).label("count")
            )
            .where(Ticket.created_at >= start_date)
            .group_by(func.date(Ticket.created_at))
            .order_by(func.date(Ticket.created_at))
        )
        return [{"date": str(date), "count": count} for date, count in result.all()]
    
    async def get_average_resolution_time(self) -> Optional[float]:
        """Get average resolution time in hours"""
        result = await self.db.execute(
            select(func.avg(Ticket.resolution_time))
            .where(Ticket.resolution_time.isnot(None))
        )
        avg_minutes = result.scalar_one()
        return avg_minutes / 60 if avg_minutes else None


class TicketLogRepository(BaseRepository[TicketLog]):
    """Repository for TicketLog operations"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(TicketLog, db)
    
    async def get_ticket_logs(self, ticket_id: int) -> List[TicketLog]:
        """Get all logs for a ticket"""
        result = await self.db.execute(
            select(TicketLog)
            .options(selectinload(TicketLog.user))
            .where(TicketLog.ticket_id == ticket_id)
            .order_by(desc(TicketLog.created_at))
        )
        return list(result.scalars().all())


class TicketCommentRepository(BaseRepository[TicketComment]):
    """Repository for TicketComment operations"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(TicketComment, db)
    
    async def get_ticket_comments(
        self,
        ticket_id: int,
        include_internal: bool = False
    ) -> List[TicketComment]:
        """Get all comments for a ticket"""
        query = select(TicketComment).options(
            selectinload(TicketComment.author)
        ).where(TicketComment.ticket_id == ticket_id)
        
        if not include_internal:
            query = query.where(TicketComment.is_internal == False)
        
        query = query.order_by(TicketComment.created_at)
        result = await self.db.execute(query)
        return list(result.scalars().all())


class AttachmentRepository(BaseRepository[Attachment]):
    """Repository for Attachment operations"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Attachment, db)
    
    async def get_ticket_attachments(self, ticket_id: int) -> List[Attachment]:
        """Get all attachments for a ticket"""
        result = await self.db.execute(
            select(Attachment)
            .where(Attachment.ticket_id == ticket_id)
            .order_by(Attachment.created_at)
        )
        return list(result.scalars().all())
