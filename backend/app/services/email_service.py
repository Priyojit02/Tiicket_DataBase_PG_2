# ============================================
# EMAIL SERVICE - Microsoft Graph API (SSO)
# ============================================
# Fetches emails using Azure AD SSO token via Microsoft Graph API
# No IMAP/password needed!

import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.core.config import settings
from app.repositories import EmailRepository
from app.schemas import EmailSourceCreate, EmailSourceResponse


class EmailService:
    """Service for fetching emails via Microsoft Graph API using SSO token"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.email_repo = EmailRepository(db)
    
    async def fetch_emails_with_token(
        self,
        access_token: str,
        days_back: int = 1,
        max_emails: int = 100,
        folder: str = "inbox"
    ) -> List[EmailSourceResponse]:
        """
        Fetch emails from Microsoft Graph API using user's SSO token
        
        Args:
            access_token: Azure AD access token from frontend
            days_back: How many days back to fetch
            max_emails: Maximum emails to fetch
            folder: Email folder (inbox, sentitems, etc.)
        """
        fetched_emails = []
        
        try:
            # Calculate date filter
            since_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Build Microsoft Graph API URL
            graph_url = f"https://graph.microsoft.com/v1.0/me/mailFolders/{folder}/messages"
            
            # Use appropriate date field based on folder
            if folder.lower() == "sentitems":
                # For sent items, filter by sent date
                date_filter = f"sentDateTime ge {since_date}"
                order_by = "sentDateTime desc"
                select_fields = "id,subject,bodyPreview,body,from,toRecipients,sentDateTime,hasAttachments,internetMessageId"
            else:
                # For inbox and other folders, filter by received date
                date_filter = f"receivedDateTime ge {since_date}"
                order_by = "receivedDateTime desc"
                select_fields = "id,subject,bodyPreview,body,from,toRecipients,receivedDateTime,hasAttachments,internetMessageId"
            
            params = {
                "$top": max_emails,
                "$orderby": order_by,
                "$filter": date_filter,
                "$select": select_fields
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    graph_url,
                    headers={"Authorization": f"Bearer {access_token}"},
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_detail = response.json() if response.text else "No response"
                    raise Exception(f"Microsoft Graph API error: {response.status_code} - {error_detail}")
                
                data = response.json()
                messages = data.get("value", [])
                
                for msg in messages:
                    message_id = msg.get("internetMessageId") or msg.get("id")
                    
                    # Check if email already exists
                    if await self.email_repo.message_exists(message_id):
                        continue
                    
                    # Extract sender
                    from_data = msg.get("from", {}).get("emailAddress", {})
                    from_address = from_data.get("address", "unknown")
                    
                    # Extract recipients
                    to_recipients = msg.get("toRecipients", [])
                    to_addresses = ", ".join([
                        r.get("emailAddress", {}).get("address", "") 
                        for r in to_recipients
                    ])
                    
                    # Get body content
                    body_data = msg.get("body", {})
                    body_content = body_data.get("content", "")
                    body_type = body_data.get("contentType", "text")
                    
                    # Parse date (sent or received based on folder)
                    if folder.lower() == "sentitems":
                        date_str = msg.get("sentDateTime")
                        date_field = "sent_at"
                    else:
                        date_str = msg.get("receivedDateTime")
                        date_field = "received_at"
                    
                    email_date = datetime.fromisoformat(date_str.replace("Z", "+00:00")) if date_str else datetime.utcnow()
                    
                    # Store email in database
                    email_source = await self.email_repo.create({
                        "message_id": message_id,
                        "from_address": from_address,
                        "to_address": to_addresses,
                        "subject": msg.get("subject", "(No Subject)"),
                        "body_text": body_content if body_type == "text" else msg.get("bodyPreview", ""),
                        "body_html": body_content if body_type == "html" else None,
                        "received_at": email_date,  # Store in received_at field regardless
                        "has_attachments": msg.get("hasAttachments", False),
                        "raw_headers": None
                    })
                    
                    fetched_emails.append(EmailSourceResponse.model_validate(email_source))
                
            return fetched_emails
            
        except Exception as e:
            print(f"Error fetching emails from Microsoft Graph: {e}")
            raise
    
    async def get_email_by_id(
        self,
        access_token: str,
        message_id: str
    ) -> Optional[dict]:
        """Get a specific email by ID from Microsoft Graph"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://graph.microsoft.com/v1.0/me/messages/{message_id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                return None
                
        except Exception as e:
            print(f"Error fetching email {message_id}: {e}")
            return None
    
    async def get_unprocessed_emails(
        self,
        limit: int = 50
    ) -> List[EmailSourceResponse]:
        """Get emails that haven't been processed yet"""
        emails = await self.email_repo.get_unprocessed(limit)
        return [EmailSourceResponse.model_validate(e) for e in emails]
    
    async def mark_processed(
        self,
        email_id: int,
        is_sap_related: bool,
        detected_category: Optional[str] = None,
        llm_analysis: Optional[dict] = None,
        ticket_created_id: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> Optional[EmailSourceResponse]:
        """Mark an email as processed"""
        email = await self.email_repo.mark_processed(
            email_id=email_id,
            is_sap_related=is_sap_related,
            detected_category=detected_category,
            llm_analysis=llm_analysis,
            ticket_created_id=ticket_created_id,
            error_message=error_message
        )
        if not email:
            return None
        return EmailSourceResponse.model_validate(email)
    
    async def get_email_stats(self) -> dict:
        """Get email processing statistics"""
        return await self.email_repo.get_stats()
    
    async def get_recent_emails(
        self,
        limit: int = 10
    ) -> List[EmailSourceResponse]:
        """Get most recent emails"""
        emails = await self.email_repo.get_recent(limit)
        return [EmailSourceResponse.model_validate(e) for e in emails]
    
    async def get_emails_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[EmailSourceResponse]:
        """Get emails by detected category"""
        emails = await self.email_repo.get_by_category(category, skip, limit)
        return [EmailSourceResponse.model_validate(e) for e in emails]


class MockEmailService(EmailService):
    """
    Mock email service for development/testing
    Returns simulated email data without actual IMAP connection
    """
    
    async def fetch_emails(
        self,
        days_back: int = 1,
        max_emails: int = 100
    ) -> List[EmailSourceResponse]:
        """Return mock emails for testing"""
        mock_emails = [
            {
                "message_id": f"mock_{datetime.utcnow().timestamp()}_{i}",
                "from_address": f"user{i}@example.com",
                "to_address": settings.email_address,
                "subject": f"SAP MM Issue - Purchase Order {1000 + i}",
                "body_text": f"We are experiencing issues with purchase order {1000 + i}. The goods receipt is not posting correctly in MM module.",
                "body_html": None,
                "received_at": datetime.utcnow() - timedelta(hours=i)
            }
            for i in range(min(5, max_emails))
        ]
        
        fetched = []
        for email_data in mock_emails:
            if await self.email_repo.message_exists(email_data["message_id"]):
                continue
            
            email_source = await self.email_repo.create({
                "message_id": email_data["message_id"],
                "from_address": email_data["from_address"],
                "to_address": email_data["to_address"],
                "subject": email_data["subject"],
                "body_text": email_data["body_text"],
                "body_html": email_data["body_html"],
                "received_at": email_data["received_at"]
            })
            
            fetched.append(EmailSourceResponse.model_validate(email_source))
        
        return fetched
