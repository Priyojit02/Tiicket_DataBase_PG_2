# ============================================
# EMAIL CONTROLLER - Email Processing Business Logic
# ============================================
# Uses Microsoft Graph API with SSO token

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.services import EmailProcessor, EmailService
from app.schemas import (
    EmailSourceResponse,
    CurrentUser,
    MessageResponse
)
from app.core.config import settings


class EmailController:
    """Controller for email processing operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        # Always use real services
        self.email_processor = EmailProcessor(db)
        self.email_service = EmailService(db)
    
    async def trigger_email_fetch(
        self,
        access_token: str,
        current_user: CurrentUser,
        days_back: int = 1,
        max_emails: int = 100,
        folder: str = "inbox"
    ) -> dict:
        """
        Fetch emails using user's SSO token and process them
        """
        if days_back < 1 or days_back > 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="days_back must be between 1 and 30"
            )
        
        if max_emails < 1 or max_emails > 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="max_emails must be between 1 and 500"
            )
        
        # Fetch emails using Microsoft Graph API
        fetched_emails = await self.email_service.fetch_emails_with_token(
            access_token=access_token,
            days_back=days_back,
            max_emails=max_emails,
            folder=folder
        )
        
        # Process fetched emails with LLM and create tickets
        result = await self.email_processor.process_emails(
            emails=fetched_emails,
            auto_create_tickets=True,
            created_by_user_id=current_user.id
        )
        
        # Sync tickets to frontend after processing
        try:
            from app.services.ticket_service import TicketService
            ticket_service = TicketService(self.db)
            synced_count = await ticket_service.update_frontend_tickets_file()
            print(f"✅ Synced {synced_count} tickets to frontend after email processing")
        except Exception as e:
            print(f"⚠️  Failed to sync tickets to frontend: {e}")
        
        return {
            "message": "Email processing completed",
            "fetched_count": len(fetched_emails),
            "stats": result
        }
    
    async def get_email_stats(
        self,
        current_user: CurrentUser
    ) -> dict:
        """Get email processing statistics"""
        return await self.email_service.get_email_stats()
    
    async def get_recent_emails(
        self,
        current_user: CurrentUser,
        limit: int = 10
    ) -> list:
        """Get most recent emails"""
        return await self.email_service.get_recent_emails(limit)
    
    async def get_unprocessed_emails(
        self,
        current_user: CurrentUser,
        limit: int = 50
    ) -> list:
        """Get unprocessed emails"""
        return await self.email_service.get_unprocessed_emails(limit)
    
    async def reprocess_email(
        self,
        current_user: CurrentUser,
        email_id: int
    ) -> dict:
        """Reprocess a specific email"""
        
        try:
            result = await self.email_processor.reprocess_email(email_id)
            return {
                "message": "Email reprocessed successfully",
                "result": result
            }
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
    
    async def get_emails_by_category(
        self,
        current_user: CurrentUser,
        category: str,
        skip: int = 0,
        limit: int = 50
    ) -> list:
        """Get emails by detected category"""
        self._check_admin(current_user)
        return await self.email_service.get_emails_by_category(
            category=category,
            skip=skip,
            limit=limit
        )
