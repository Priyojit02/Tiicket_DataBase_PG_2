# ============================================
# EMAIL PROCESSOR - Orchestrates Email to Ticket Pipeline
# ============================================

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.services.email_service import EmailService, MockEmailService
from app.services.llm_service import LLMService, MockLLMService
from app.services.ticket_service import TicketService
from app.repositories import UserRepository, EmailRepository
from app.models import TicketCategory, TicketPriority
from app.core.config import settings


class EmailProcessor:
    """
    Orchestrates the email-to-ticket pipeline:
    1. Fetch emails from IMAP
    2. Parse with LLM
    3. Create tickets for SAP-related emails
    """
    
    def __init__(self, db: AsyncSession, use_mock: bool = False):
        self.db = db
        self.use_mock = use_mock
        
        # Initialize services based on mode
        if use_mock:
            self.email_service = MockEmailService(db)
            self.llm_service = MockLLMService(db)
        else:
            self.email_service = EmailService(db)
            self.llm_service = LLMService(db)
        
        self.ticket_service = TicketService(db)
        self.user_repo = UserRepository(db)
        self.email_repo = EmailRepository(db)
    
    async def process_daily_emails(
        self,
        days_back: int = 1,
        max_emails: int = 100,
        auto_create_tickets: bool = True
    ) -> dict:
        """
        Main method: Fetch, analyze, and process emails
        Returns processing statistics
        """
        stats = {
            "fetched": 0,
            "analyzed": 0,
            "sap_related": 0,
            "tickets_created": 0,
            "errors": 0,
            "skipped": 0
        }
        
        try:
            # Step 1: Fetch new emails
            print(f"Fetching emails from last {days_back} day(s)...")
            new_emails = await self.email_service.fetch_emails(
                days_back=days_back,
                max_emails=max_emails
            )
            stats["fetched"] = len(new_emails)
            print(f"Fetched {len(new_emails)} new emails")
            
            # Step 2: Get all unprocessed emails
            unprocessed = await self.email_service.get_unprocessed_emails(limit=max_emails)
            print(f"Processing {len(unprocessed)} unprocessed emails")
            
            # Step 3: Analyze and process each email
            for email in unprocessed:
                try:
                    result = await self._process_single_email(
                        email_id=email.id,
                        subject=email.subject,
                        body=email.body_text or "",
                        from_address=email.from_address,
                        auto_create_ticket=auto_create_tickets
                    )
                    
                    stats["analyzed"] += 1
                    
                    if result.get("is_sap_related"):
                        stats["sap_related"] += 1
                        if result.get("ticket_created"):
                            stats["tickets_created"] += 1
                    else:
                        stats["skipped"] += 1
                        
                except Exception as e:
                    print(f"Error processing email {email.id}: {e}")
                    stats["errors"] += 1
                    
                    # Mark as processed with error
                    await self.email_service.mark_processed(
                        email_id=email.id,
                        is_sap_related=False,
                        error_message=str(e)
                    )
            
            return stats
            
        except Exception as e:
            print(f"Email processing error: {e}")
            raise
        
        finally:
            # Always update frontend tickets file after processing
            try:
                await self.ticket_service.update_frontend_tickets_file()
            except Exception as e:
                print(f"Warning: Failed to update frontend tickets file: {e}")
    
    async def process_emails(
        self,
        emails: List,
        auto_create_tickets: bool = True,
        created_by_user_id: int = None
    ) -> dict:
        """
        Process a list of already fetched emails
        Used by the controller when emails are fetched via API
        """
        stats = {
            "analyzed": 0,
            "sap_related": 0,
            "tickets_created": 0,
            "errors": 0,
            "skipped": 0
        }
        
        for email in emails:
            try:
                # Email is already stored, just process it
                result = await self._process_single_email(
                    email_id=email.id,
                    subject=email.subject,
                    body=email.body_text or "",
                    from_address=email.from_address,
                    auto_create_ticket=auto_create_tickets
                )
                
                stats["analyzed"] += 1
                
                if result.get("is_sap_related"):
                    stats["sap_related"] += 1
                    if result.get("ticket_created"):
                        stats["tickets_created"] += 1
                else:
                    stats["skipped"] += 1
                    
            except Exception as e:
                print(f"Error processing email {email.id}: {e}")
                stats["errors"] += 1
        
        # Update frontend tickets file after processing
        try:
            await self.ticket_service.update_frontend_tickets_file()
        except Exception as e:
            print(f"Warning: Failed to update frontend tickets file: {e}")
        
        return stats
    
    async def _process_single_email(
        self,
        email_id: int,
        subject: str,
        body: str,
        from_address: str,
        auto_create_ticket: bool = True
    ) -> dict:
        """Process a single email through the LLM pipeline"""
        result = {
            "email_id": email_id,
            "is_sap_related": False,
            "category": None,
            "ticket_created": False,
            "ticket_id": None
        }
        
        # Analyze with LLM
        try:
            analysis = await self.llm_service.analyze_email(
                subject=subject,
                body=body,
                from_address=from_address
            )
        except Exception as e:
            print(f"LLM analysis failed for email {email_id}: {e}")
            # Fall back to keyword-based analysis if LLM fails
            if not self.use_mock:
                from app.services.llm_service import MockLLMService
                mock_llm = MockLLMService(self.db)
                analysis = await mock_llm.analyze_email(
                    subject=subject,
                    body=body,
                    from_address=from_address
                )
                print(f"Using fallback keyword analysis for email {email_id}")
            else:
                raise  # Re-raise if already using mock services
        
        result["is_sap_related"] = analysis.is_sap_related
        result["category"] = analysis.detected_category.value if analysis.detected_category else None
        result["confidence"] = analysis.confidence
        
        ticket_id = None
        
        # Create ticket if SAP-related and auto-create is enabled
        if analysis.is_sap_related and auto_create_ticket and analysis.confidence >= 0.6:
            ticket = await self._create_ticket_from_analysis(
                email_id=email_id,
                subject=subject,
                body=body,
                from_address=from_address,
                analysis=analysis
            )
            
            if ticket:
                result["ticket_created"] = True
                result["ticket_id"] = ticket.id
                ticket_id = ticket.id
        
        # Mark email as processed
        await self.email_service.mark_processed(
            email_id=email_id,
            is_sap_related=analysis.is_sap_related,
            detected_category=result["category"],
            llm_analysis=analysis.raw_response,
            ticket_created_id=ticket_id
        )
        
        return result
    
    async def _create_ticket_from_analysis(
        self,
        email_id: int,
        subject: str,
        body: str,
        from_address: str,
        analysis
    ):
        """Create a ticket from LLM analysis"""
        # Get system user for auto-created tickets
        system_user = await self._get_or_create_system_user()
        
        # Prepare ticket data
        title = analysis.suggested_title or subject[:200]
        
        # Build description with key points
        description = f"**Email from:** {from_address}\n\n"
        description += f"**Original Subject:** {subject}\n\n"
        description += f"**Content:**\n{body[:2000]}\n\n"
        
        if analysis.key_points:
            description += "**Key Points:**\n"
            for point in analysis.key_points:
                description += f"- {point}\n"
        
        description += f"\n---\n*Auto-generated ticket (Confidence: {analysis.confidence:.2%})*"
        
        # Map category
        category = analysis.detected_category or TicketCategory.OTHER
        
        # Map priority
        priority = analysis.suggested_priority or TicketPriority.MEDIUM
        
        # Get email source for message_id
        email_source = await self.email_repo.get_by_id(email_id)
        
        # Create ticket
        ticket = await self.ticket_service.create_ticket_from_email(
            title=title,
            description=description,
            category=category,
            priority=priority,
            source_email_id=email_source.message_id if email_source else str(email_id),
            source_email_from=from_address,
            source_email_subject=subject,
            created_by=system_user.id,
            llm_confidence=analysis.confidence,
            llm_raw_response=analysis.raw_response
        )
        
        return ticket
    
    async def _get_or_create_system_user(self):
        """Get or create a system user for auto-created tickets"""
        system_email = "system@sap-ticket-bot.local"
        
        user = await self.user_repo.get_by_email(system_email)
        if user:
            return user
        
        # Create system user
        user = await self.user_repo.create({
            "azure_id": "system-bot-001",
            "email": system_email,
            "name": "SAP Ticket Bot",
            "department": "IT Support",
            "is_active": True,
            "is_admin": False
        })
        
        return user
    
    async def reprocess_email(self, email_id: int) -> dict:
        """Reprocess a specific email"""
        email = await self.email_repo.get_by_id(email_id)
        if not email:
            raise ValueError(f"Email {email_id} not found")
        
        return await self._process_single_email(
            email_id=email.id,
            subject=email.subject,
            body=email.body_text or "",
            from_address=email.from_address,
            auto_create_ticket=True
        )
    
    async def get_processing_stats(self) -> dict:
        """Get email processing statistics"""
        return await self.email_service.get_email_stats()
