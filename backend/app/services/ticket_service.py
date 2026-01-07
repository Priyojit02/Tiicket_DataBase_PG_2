# ============================================
# TICKET SERVICE - Ticket Management Operations
# ============================================

from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.repositories import (
    TicketRepository,
    TicketLogRepository,
    TicketCommentRepository,
    AttachmentRepository,
    UserRepository
)
from app.models import (
    Ticket,
    TicketLog,
    TicketComment,
    TicketStatus,
    TicketPriority,
    TicketCategory,
    LogType
)
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
    CurrentUser
)


class TicketService:
    """Service for ticket management operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ticket_repo = TicketRepository(db)
        self.log_repo = TicketLogRepository(db)
        self.comment_repo = TicketCommentRepository(db)
        self.attachment_repo = AttachmentRepository(db)
        self.user_repo = UserRepository(db)
    
    async def create_ticket(
        self,
        ticket_data: TicketCreate,
        current_user: CurrentUser
    ) -> TicketResponse:
        """Create a new ticket"""
        try:
            # Generate ticket ID
            ticket_id = await self.ticket_repo.get_next_ticket_id()

            # Create ticket
            ticket = await self.ticket_repo.create({
                "ticket_id": ticket_id,
                "title": ticket_data.title,
                "description": ticket_data.description,
                "status": TicketStatus.OPEN,
                "priority": ticket_data.priority,
                "category": ticket_data.category,
                "created_by": current_user.id,
                "assigned_to": ticket_data.assigned_to
            })

            # Create log entry
            await self._create_log(
                ticket_id=ticket.id,
                user_id=current_user.id,
                log_type=LogType.CREATED,
                action=f"Ticket {ticket_id} created"
            )

            # Reload with relationships
            ticket = await self.ticket_repo.get_with_details(ticket.id)
            
            # Update frontend tickets file after creation
            await self.update_frontend_tickets_file()
            
            return TicketResponse.model_validate(ticket)

        except Exception as e:
            # Database not reachable - fallback to file storage
            print(f"Database error: {e}. Falling back to file storage.")
            return await self._create_ticket_in_file(ticket_data, current_user)
    
    async def create_ticket_from_email(
        self,
        title: str,
        description: str,
        category: TicketCategory,
        priority: TicketPriority,
        source_email_id: str,
        source_email_from: str,
        source_email_subject: str,
        created_by: int,
        llm_confidence: float = None,
        llm_raw_response: dict = None
    ) -> Optional[Ticket]:
        """Create a ticket from email processing (auto-generated)"""
        try:
            # Generate ticket ID
            ticket_id = await self.ticket_repo.get_next_ticket_id()

            # Create ticket with email metadata
            ticket = await self.ticket_repo.create({
                "ticket_id": ticket_id,
                "title": title,
                "description": description,
                "status": TicketStatus.OPEN,
                "priority": priority,
                "category": category,
                "created_by": created_by,
                "source_email_id": source_email_id,
                "source_email_from": source_email_from,
                "source_email_subject": source_email_subject,
                "llm_confidence": llm_confidence,
                "llm_raw_response": llm_raw_response
            })

            # Create log entry
            await self._create_log(
                ticket_id=ticket.id,
                user_id=created_by,
                log_type=LogType.EMAIL_RECEIVED,
                action=f"Ticket {ticket_id} auto-created from email processing"
            )

            # Update frontend tickets file after email ticket creation
            await self.update_frontend_tickets_file()

            return ticket

        except Exception as e:
            print(f"Error creating ticket from email: {e}")
            return None
    
    async def export_tickets_to_frontend_format(self) -> list:
        """Export tickets from database to frontend format for tickets2.ts"""
        try:
            # Get all tickets with relationships
            tickets = await self.ticket_repo.get_all_with_details()
            
            frontend_tickets = []
            for ticket in tickets:
                frontend_ticket = {
                    'id': ticket.id,
                    'title': ticket.title,
                    'description': ticket.description,
                    'status': ticket.status.value,
                    'priority': ticket.priority.value,
                    'assignedTo': ticket.assigned_to_user.name if ticket.assigned_to_user else 'Unassigned',
                    'raisedBy': ticket.created_by_user.name if ticket.created_by_user else 'System',
                    'completionBy': None,
                    'createdOn': ticket.created_at.strftime('%Y-%m-%d'),
                    'closedOn': ticket.resolved_at.strftime('%Y-%m-%d') if ticket.resolved_at else None,
                    'module': ticket.category.value if ticket.category else 'OTHER',
                    'tags': ['email-parsed', 'llm-generated'] if ticket.source_email_id else ['manual'],
                    'source_email_id': ticket.source_email_id,  # Include for filtering
                    'created_by': ticket.created_by,  # Include for filtering manual tickets
                    'logs': [{
                        'id': 1,
                        'action': 'ticket_created',
                        'performedBy': 'LLM Parser' if ticket.source_email_id else 'Manual',
                        'timestamp': ticket.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
                        'details': f'Auto-created from email (Confidence: {ticket.llm_confidence:.1%})' if ticket.llm_confidence else 'Manually created'
                    }],
                    'comments': []
                }
                frontend_tickets.append(frontend_ticket)
            
            return frontend_tickets
            
        except Exception as e:
            print(f"Error exporting tickets to frontend format: {e}")
            return []
    
    async def  update_frontend_tickets_file(self):
        """Update the tickets2.ts file with current database tickets ba sed on DATA_SOURCE_MODE"""
        try:
            import json
            import os
            from app.core.config import settings
            
            # Get all tickets with details
            all_tickets = await self.export_tickets_to_frontend_format()
            
            # Filter tickets based on DATA_SOURCE_MODE
            if settings.data_source_mode == "llm":
                # LLM-parsed tickets (those with source_email_id) OR manually created tickets (have created_by)
                filtered_tickets = [t for t in all_tickets if t.get('source_email_id') or t.get('created_by')]
            elif settings.data_source_mode == "combined":
                # All tickets (both dummy and LLM)
                filtered_tickets = all_tickets
            elif settings.data_source_mode == "dummy":
                # Only manually created tickets (those without source_email_id)
                filtered_tickets = [t for t in all_tickets if not t.get('source_email_id')]
            else:
                # Default to combined
                filtered_tickets = all_tickets
            
            # Create the TypeScript content
            mode_description = {
                "llm": "LLM-parsed tickets + manual user tickets",
                "combined": "Combined dummy + LLM tickets", 
                "dummy": "Manual user tickets only"
            }.get(settings.data_source_mode, "Combined mode")
            
            ts_content = f"""// ============================================
// TICKETS DATA - {mode_description.upper()}
// ============================================
// Mode: {settings.data_source_mode}
// Auto-generated from database on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
// Total tickets: {len(filtered_tickets)}
// Data source mode controlled by .env DATA_SOURCE_MODE

import {{ Ticket }} from '@/types';

export const ticketsData: Ticket[] = {json.dumps(filtered_tickets, indent=2)};
"""
            
            # Write to frontend file
            frontend_path = os.path.join(os.path.dirname(__file__), '../../../frontend-up/src/data/tickets2.ts')
            os.makedirs(os.path.dirname(frontend_path), exist_ok=True)
            
            with open(frontend_path, 'w', encoding='utf-8') as f:
                f.write(ts_content)
            
            print(f"Updated tickets2.ts with {len(filtered_tickets)} tickets (mode: {settings.data_source_mode})")
            return len(filtered_tickets)
            
        except Exception as e:
            print(f"Error updating frontend tickets file: {e}")
            return 0
    
    async def get_ticket(self, ticket_id: int) -> Optional[TicketDetailResponse]:
        """Get ticket with all details"""
        ticket = await self.ticket_repo.get_with_details(ticket_id)
        if not ticket:
            return None
        return TicketDetailResponse.model_validate(ticket)
    
    async def get_ticket_by_ticket_id(self, ticket_id: str) -> Optional[TicketDetailResponse]:
        """Get ticket by ticket_id (T-001 format)"""
        ticket = await self.ticket_repo.get_by_ticket_id(ticket_id)
        if not ticket:
            return None
        ticket = await self.ticket_repo.get_with_details(ticket.id)
        return TicketDetailResponse.model_validate(ticket)
    
    async def get_tickets(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        assigned_to: Optional[int] = None,
        created_by: Optional[int] = None,
        search: Optional[str] = None,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> TicketListResponse:
        """Get paginated list of tickets"""
        # Convert string filters to enums
        status_enum = TicketStatus(status) if status else None
        priority_enum = TicketPriority(priority) if priority else None
        category_enum = TicketCategory(category) if category else None
        
        tickets, total = await self.ticket_repo.get_paginated(
            skip=skip,
            limit=limit,
            status=status_enum,
            priority=priority_enum,
            category=category_enum,
            assigned_to=assigned_to,
            created_by=created_by,
            search=search,
            order_by=order_by,
            order_desc=order_desc
        )
        
        pages = (total + limit - 1) // limit
        
        return TicketListResponse(
            items=[TicketResponse.model_validate(t) for t in tickets],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=pages
        )
    
    async def update_ticket(
        self,
        ticket_id: int,
        update_data: TicketUpdate,
        current_user: CurrentUser
    ) -> Optional[TicketResponse]:
        """Update a ticket"""
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Track changes for logging
        for field, new_value in update_dict.items():
            old_value = getattr(ticket, field)
            
            if field == "status" and old_value != new_value:
                await self._create_log(
                    ticket_id=ticket_id,
                    user_id=current_user.id,
                    log_type=LogType.STATUS_CHANGE,
                    action=f"Status changed from {old_value.value if old_value else 'None'} to {new_value.value if hasattr(new_value, 'value') else new_value}",
                    old_value=old_value.value if old_value else None,
                    new_value=new_value.value if hasattr(new_value, 'value') else str(new_value)
                )
                
                # Set resolved_at if status is Resolved
                if new_value == TicketStatus.RESOLVED:
                    update_dict["resolved_at"] = datetime.utcnow()
                    # Calculate resolution time
                    if ticket.created_at:
                        resolution_minutes = int((datetime.utcnow() - ticket.created_at).total_seconds() / 60)
                        update_dict["resolution_time"] = resolution_minutes
            
            elif field == "priority" and old_value != new_value:
                await self._create_log(
                    ticket_id=ticket_id,
                    user_id=current_user.id,
                    log_type=LogType.PRIORITY_CHANGE,
                    action=f"Priority changed from {old_value.value if old_value else 'None'} to {new_value.value if hasattr(new_value, 'value') else new_value}",
                    old_value=old_value.value if old_value else None,
                    new_value=new_value.value if hasattr(new_value, 'value') else str(new_value)
                )
            
            elif field == "assigned_to" and old_value != new_value:
                old_user = await self.user_repo.get_by_id(old_value) if old_value else None
                new_user = await self.user_repo.get_by_id(new_value) if new_value else None
                await self._create_log(
                    ticket_id=ticket_id,
                    user_id=current_user.id,
                    log_type=LogType.ASSIGNMENT,
                    action=f"Assigned to {new_user.name if new_user else 'Unassigned'}",
                    old_value=old_user.name if old_user else None,
                    new_value=new_user.name if new_user else None
                )
        
        # Update the ticket
        updated_ticket = await self.ticket_repo.update(ticket_id, update_dict)
        if not updated_ticket:
            return None
        
        # Reload with relationships
        updated_ticket = await self.ticket_repo.get_with_details(ticket_id)
        
        # Update frontend tickets file after update
        await self.update_frontend_tickets_file()
        
        return TicketResponse.model_validate(updated_ticket)
    
    async def delete_ticket(self, ticket_id: int) -> bool:
        """Delete a ticket"""
        result = await self.ticket_repo.delete(ticket_id)
        if result:
            # Update frontend tickets file after deletion
            await self.update_frontend_tickets_file()
        return result
    
    async def add_comment(
        self,
        ticket_id: int,
        comment_data: TicketCommentCreate,
        current_user: CurrentUser
    ) -> Optional[TicketCommentResponse]:
        """Add a comment to a ticket"""
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None
        
        comment = await self.comment_repo.create({
            "ticket_id": ticket_id,
            "author_id": current_user.id,
            "content": comment_data.content,
            "is_internal": comment_data.is_internal
        })
        
        # Create log entry
        await self._create_log(
            ticket_id=ticket_id,
            user_id=current_user.id,
            log_type=LogType.COMMENT,
            action=f"Comment added by {current_user.name}"
        )
        
        return TicketCommentResponse.model_validate(comment)
    
    async def update_comment(
        self,
        comment_id: int,
        update_data: TicketCommentUpdate,
        current_user: CurrentUser
    ) -> Optional[TicketCommentResponse]:
        """Update a comment"""
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment or comment.author_id != current_user.id:
            return None
        
        updated_comment = await self.comment_repo.update(comment_id, {
            "content": update_data.content,
            "is_edited": True,
            "edited_at": datetime.utcnow()
        })
        
        return TicketCommentResponse.model_validate(updated_comment)
    
    async def delete_comment(
        self,
        comment_id: int,
        current_user: CurrentUser
    ) -> bool:
        """Delete a comment"""
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            return False
        
        # Only author or admin can delete
        if comment.author_id != current_user.id and not current_user.is_admin:
            return False
        
        return await self.comment_repo.delete(comment_id)
    
    async def get_ticket_logs(self, ticket_id: int) -> List[TicketLogResponse]:
        """Get all logs for a ticket"""
        logs = await self.log_repo.get_ticket_logs(ticket_id)
        return [TicketLogResponse.model_validate(log) for log in logs]
    
    async def get_user_tickets(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> TicketListResponse:
        """Get tickets for a specific user"""
        tickets, total = await self.ticket_repo.get_user_tickets(
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        
        pages = (total + limit - 1) // limit
        
        return TicketListResponse(
            items=[TicketResponse.model_validate(t) for t in tickets],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=pages
        )
    
    async def get_recent_tickets(self, limit: int = 10) -> List[TicketResponse]:
        """Get most recent tickets"""
        tickets = await self.ticket_repo.get_recent_tickets(limit)
        return [TicketResponse.model_validate(t) for t in tickets]
    
    async def _create_log(
        self,
        ticket_id: int,
        user_id: int,
        log_type: LogType,
        action: str,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        log_metadata: Optional[dict] = None
    ) -> TicketLog:
        """Create a ticket log entry"""
        return await self.log_repo.create({
            "ticket_id": ticket_id,
            "user_id": user_id,
            "log_type": log_type,
            "action": action,
            "old_value": old_value,
            "new_value": new_value,
            "log_metadata": log_metadata
        })
    
    async def create_ticket_from_email(
        self,
        title: str,
        description: str,
        category: TicketCategory,
        priority: TicketPriority,
        source_email_id: str,
        source_email_from: str,
        source_email_subject: str,
        created_by: int,
        llm_confidence: Optional[float] = None,
        llm_raw_response: Optional[dict] = None
    ) -> Ticket:
        """Create a ticket from parsed email"""
        ticket_id = await self.ticket_repo.get_next_ticket_id()
        
        ticket = await self.ticket_repo.create({
            "ticket_id": ticket_id,
            "title": title,
            "description": description,
            "status": TicketStatus.OPEN,
            "priority": priority,
            "category": category,
            "created_by": created_by,
            "source_email_id": source_email_id,
            "source_email_from": source_email_from,
            "source_email_subject": source_email_subject,
            "llm_confidence": llm_confidence,
            "llm_raw_response": llm_raw_response
        })
        
        # Create log entry
        await self._create_log(
            ticket_id=ticket.id,
            user_id=created_by,
            log_type=LogType.EMAIL_RECEIVED,
            action=f"Ticket auto-created from email: {source_email_subject}",
            log_metadata={"source_email": source_email_from, "llm_confidence": llm_confidence}
        )
        
        return ticket

    async def _create_ticket_in_file(
        self,
        ticket_data: TicketCreate,
        current_user: CurrentUser
    ) -> TicketResponse:
        """Create ticket in frontend file when database is not reachable"""
        import json
        import os
        from datetime import datetime

        # Generate a unique ID (start from 1000 to avoid conflicts with mock data)
        ticket_id_num = int(datetime.now().timestamp() * 1000) % 1000000 + 1000
        ticket_id_str = f"T-{ticket_id_num:03d}"

        # Create ticket data in frontend format
        ticket_dict = {
            "id": ticket_id_num,
            "title": ticket_data.title,
            "description": ticket_data.description or "",
            "status": "Open",
            "priority": ticket_data.priority.value if hasattr(ticket_data.priority, 'value') else str(ticket_data.priority),
            "assignedTo": "Auto-assigned",  # Default assignment
            "raisedBy": current_user.name if hasattr(current_user, 'name') else str(current_user.id),
            "completionBy": ticket_data.completion_by.isoformat() if ticket_data.completion_by else datetime.now().date().isoformat(),
            "createdOn": datetime.now().date().isoformat(),
            "closedOn": None,
            "module": ticket_data.category.value if hasattr(ticket_data.category, 'value') else str(ticket_data.category),
            "tags": ["db-fallback"],
            "logs": [{
                "id": 1,
                "action": "ticket_created",
                "performedBy": "System (DB Fallback)",
                "timestamp": datetime.now().isoformat(),
                "details": "Ticket created when database was not reachable"
            }],
            "comments": []
        }

        # Path to frontend data2.ts file
        frontend_data_file = os.path.join(
            os.path.dirname(__file__),  # backend/app/services/
            "..", "..", "..",          # go up to project root
            "frontend-up", "src", "data", "tickets2.ts"
        )

        try:
            # Read existing file
            if os.path.exists(frontend_data_file):
                with open(frontend_data_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                # Create new file with initial structure
                content = """// ============================================
// LLM-PARSED TICKETS DATA - Auto-generated from email parsing
// ============================================

import { Ticket } from '@/types';

export const llmParsedTickets: Ticket[] = [
    // LLM will add parsed tickets here
];
"""

            # Parse existing tickets
            if 'export const llmParsedTickets: Ticket[] = [' in content:
                # Find the array content
                start_idx = content.find('[')
                end_idx = content.rfind(']')

                if start_idx != -1 and end_idx != -1:
                    existing_array_content = content[start_idx+1:end_idx].strip()
                    if existing_array_content and existing_array_content != '// LLM will add parsed tickets here':
                        # Parse existing JSON-like content and add new ticket
                        existing_tickets = []
                        if existing_array_content.strip():
                            # This is a simplified parser - in production you'd want proper JSON parsing
                            pass

                        # Add new ticket to the array
                        new_array_content = existing_array_content
                        if new_array_content and not new_array_content.endswith(','):
                            new_array_content += ','
                        new_array_content += f"""
    {json.dumps(ticket_dict, indent=4)}"""

                        content = content[:start_idx+1] + new_array_content + content[end_idx:]
                    else:
                        # Empty array, add first ticket
                        content = content.replace('// LLM will add parsed tickets here', f"""
    {json.dumps(ticket_dict, indent=4)}""")

            # Write back to file
            with open(frontend_data_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"Ticket {ticket_id_num} saved to frontend file: {frontend_data_file}")

            # Return response in expected format
            from app.schemas import TicketResponse
            return TicketResponse(
                id=ticket_id_num,
                ticket_id=ticket_id_str,
                title=ticket_data.title,
                description=ticket_data.description,
                status="Open",
                priority=ticket_data.priority,
                category=ticket_data.category,
                created_by=current_user.id,
                assigned_to=ticket_data.assigned_to,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

        except Exception as file_error:
            print(f"Error writing to frontend file: {file_error}")
            # Return a basic response even if file write fails
            from app.schemas import TicketResponse
            return TicketResponse(
                id=ticket_id_num,
                ticket_id=ticket_id_str,
                title=ticket_data.title,
                description=ticket_data.description,
                status="Open",
                priority=ticket_data.priority,
                category=ticket_data.category,
                created_by=current_user.id,
                assigned_to=ticket_data.assigned_to,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
