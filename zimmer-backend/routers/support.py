"""
Support endpoints for Zimmer AI Platform
Handles support tickets and customer service
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from database import get_db
from models.user import User
from models.ticket import Ticket
from models.ticket_message import TicketMessage
from utils.auth import get_current_user

router = APIRouter(prefix="/api/support", tags=["support"])

class CreateTicketRequest(BaseModel):
    subject: str
    message: str
    importance: str = "medium"
    category: Optional[str] = None

class TicketMessageRequest(BaseModel):
    message: str
    attachment_path: Optional[str] = None

@router.get("/tickets")
async def get_support_tickets(
    status: Optional[str] = Query(None, description="Filter by ticket status"),
    importance: Optional[str] = Query(None, description="Filter by importance"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's support tickets"""
    try:
        query = db.query(Ticket).filter(Ticket.user_id == current_user.id)
        
        # Apply filters
        if status:
            query = query.filter(Ticket.status == status)
        if importance:
            query = query.filter(Ticket.importance == importance)
        
        # Get total count
        total_count = query.count()
        
        # Get tickets with pagination
        tickets = query.order_by(Ticket.created_at.desc()).offset(offset).limit(limit).all()
        
        ticket_list = []
        for ticket in tickets:
            # Get latest message
            latest_message = db.query(TicketMessage).filter(
                TicketMessage.ticket_id == ticket.id
            ).order_by(TicketMessage.created_at.desc()).first()
            
            ticket_list.append({
                "id": ticket.id,
                "subject": ticket.subject,
                "status": ticket.status,
                "importance": ticket.importance,
                "category": ticket.category,
                "assigned_to": ticket.assigned_to,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
                "latest_message": {
                    "message": latest_message.message if latest_message else None,
                    "created_at": latest_message.created_at.isoformat() if latest_message else None,
                    "is_admin": latest_message.is_internal if latest_message else None
                } if latest_message else None
            })
        
        return {
            "tickets": ticket_list,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve support tickets: {str(e)}"
        )

@router.post("/tickets")
async def create_support_ticket(
    request: CreateTicketRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new support ticket"""
    try:
        # Validate importance level
        valid_importance = ["low", "medium", "high", "urgent"]
        if request.importance not in valid_importance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Importance must be one of: {valid_importance}"
            )
        
        # Create ticket
        ticket = Ticket(
            user_id=current_user.id,
            subject=request.subject,
            message=request.message,
            status="open",
            importance=request.importance,
            category=request.category,
            created_at=datetime.utcnow()
        )
        
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        # Create initial message
        ticket_message = TicketMessage(
            ticket_id=ticket.id,
            user_id=current_user.id,
            message=request.message,
            is_internal=False,
            created_at=datetime.utcnow()
        )
        
        db.add(ticket_message)
        db.commit()
        
        return {
            "ticket_id": ticket.id,
            "subject": ticket.subject,
            "status": ticket.status,
            "importance": ticket.importance,
            "created_at": ticket.created_at.isoformat(),
            "message": "Support ticket created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create support ticket: {str(e)}"
        )

@router.get("/tickets/{ticket_id}")
async def get_ticket_details(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific ticket"""
    try:
        ticket = db.query(Ticket).filter(
            Ticket.id == ticket_id,
            Ticket.user_id == current_user.id
        ).first()
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Get all messages for this ticket
        messages = db.query(TicketMessage).filter(
            TicketMessage.ticket_id == ticket_id
        ).order_by(TicketMessage.created_at.asc()).all()
        
        message_list = []
        for message in messages:
            message_list.append({
                "id": message.id,
                "message": message.message,
                "is_admin": message.is_internal,
                "created_at": message.created_at.isoformat(),
                "attachment_path": message.attachment_path
            })
        
        return {
            "id": ticket.id,
            "subject": ticket.subject,
            "status": ticket.status,
            "importance": ticket.importance,
            "category": ticket.category,
            "assigned_to": ticket.assigned_to,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
            "messages": message_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve ticket details: {str(e)}"
        )

@router.post("/tickets/{ticket_id}/messages")
async def add_ticket_message(
    ticket_id: int,
    request: TicketMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a message to an existing ticket"""
    try:
        # Verify ticket exists and belongs to user
        ticket = db.query(Ticket).filter(
            Ticket.id == ticket_id,
            Ticket.user_id == current_user.id
        ).first()
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Check if ticket is closed
        if ticket.status == "closed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot add message to closed ticket"
            )
        
        # Create new message
        ticket_message = TicketMessage(
            ticket_id=ticket_id,
            user_id=current_user.id,
            message=request.message,
            is_internal=False,
            attachment_path=request.attachment_path,
            created_at=datetime.utcnow()
        )
        
        db.add(ticket_message)
        
        # Update ticket's updated_at timestamp
        ticket.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "message_id": ticket_message.id,
            "ticket_id": ticket_id,
            "message": "Message added to ticket successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add message to ticket: {str(e)}"
        )

@router.put("/tickets/{ticket_id}/close")
async def close_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Close a support ticket"""
    try:
        ticket = db.query(Ticket).filter(
            Ticket.id == ticket_id,
            Ticket.user_id == current_user.id
        ).first()
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        if ticket.status == "closed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ticket is already closed"
            )
        
        ticket.status = "closed"
        ticket.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "ticket_id": ticket_id,
            "status": "closed",
            "message": "Ticket closed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to close ticket: {str(e)}"
        )

@router.get("/categories")
async def get_support_categories():
    """Get available support ticket categories"""
    return {
        "categories": [
            {"id": "technical", "name": "Technical Support", "description": "Technical issues and bugs"},
            {"id": "billing", "name": "Billing & Payments", "description": "Payment and billing questions"},
            {"id": "feature", "name": "Feature Request", "description": "Request new features"},
            {"id": "account", "name": "Account Issues", "description": "Account-related problems"},
            {"id": "general", "name": "General Inquiry", "description": "General questions and inquiries"}
        ]
    }

@router.get("/stats")
async def get_support_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get support statistics for current user"""
    try:
        total_tickets = db.query(Ticket).filter(Ticket.user_id == current_user.id).count()
        
        open_tickets = db.query(Ticket).filter(
            Ticket.user_id == current_user.id,
            Ticket.status == "open"
        ).count()
        
        closed_tickets = db.query(Ticket).filter(
            Ticket.user_id == current_user.id,
            Ticket.status == "closed"
        ).count()
        
        # Get tickets by importance
        tickets_by_importance = db.query(
            Ticket.importance,
            db.func.count(Ticket.id).label('count')
        ).filter(
            Ticket.user_id == current_user.id
        ).group_by(Ticket.importance).all()
        
        importance_stats = {item.importance: item.count for item in tickets_by_importance}
        
        return {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "closed_tickets": closed_tickets,
            "tickets_by_importance": importance_stats,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get support stats: {str(e)}"
        )
