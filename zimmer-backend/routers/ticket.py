from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
import os
import shutil
from pathlib import Path as PathLib

from database import SessionLocal
from models.user import User
from models.ticket import Ticket, TicketStatus
from schemas.ticket import TicketCreate, TicketUpdate, TicketOut, TicketListResponse
from utils.auth import get_current_user, require_admin

router = APIRouter()

# File upload configuration
UPLOAD_DIR = "uploads/tickets"
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".jpg", ".jpeg", ".png", ".gif"}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_uploaded_file(file: UploadFile) -> Optional[str]:
    """Save uploaded file and return the file path"""
    if not file:
        return None
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Validate file extension
    file_extension = PathLib(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate filename for path traversal attempts
    filename = file.filename
    if not filename or '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename detected"
        )
    
    # Generate unique filename with secure random UUID
    import uuid
    import secrets
    unique_filename = f"{secrets.token_urlsafe(16)}_{uuid.uuid4()}{file_extension}"
    
    # Ensure upload directory exists and is secure
    upload_path = PathLib(UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    
    # Create absolute file path and validate it's within upload directory
    file_path = upload_path / unique_filename
    try:
        file_path = file_path.resolve()
        upload_path_resolved = upload_path.resolve()
        if not str(file_path).startswith(str(upload_path_resolved)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path"
            )
    except (RuntimeError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path"
        )
    
    # Save file with secure handling
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except (OSError, IOError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    return str(file_path)

@router.post("/tickets", response_model=TicketOut)
async def create_ticket(
    user_id: int = Form(..., gt=0, description="User ID for ticket creation"),
    subject: str = Form(..., min_length=1, max_length=200, description="Ticket subject"),
    message: str = Form(..., min_length=1, max_length=5000, description="Ticket message"),
    importance: str = Form("medium", description="Ticket importance level"),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new support ticket with optional file attachment
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions: users can only create tickets for themselves, admins can create for anyone
        if not current_user.is_admin and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create tickets for yourself"
            )
        
        # Handle file upload
        attachment_path = None
        if file:
            attachment_path = save_uploaded_file(file)
        
        # Create new ticket
        new_ticket = Ticket(
            user_id=user_id,
            subject=subject,
            message=message,
            importance=importance,
            attachment_path=attachment_path
        )
        
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        
        # Return with user names
        return TicketOut(
            id=new_ticket.id,
            user_id=new_ticket.user_id,
            subject=new_ticket.subject,
            message=new_ticket.message,
            status=new_ticket.status,
            importance=new_ticket.importance,
            attachment_path=new_ticket.attachment_path,
            assigned_to=new_ticket.assigned_to,
            created_at=new_ticket.created_at,
            updated_at=new_ticket.updated_at,
            user_name=user.name,
            assigned_admin_name=None
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database constraint violation"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ticket: {str(e)}"
        )

@router.get("/tickets", response_model=TicketListResponse)
async def get_tickets(
    ticket_status: Optional[TicketStatus] = Query(None, description="Filter by status"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all tickets (admin only) or user's own tickets
    """
    try:
        # Build base query
        query = db.query(Ticket)
        
        # Apply filters
        if ticket_status is not None:
            query = query.filter(Ticket.status == ticket_status)
        
        if user_id is not None:
            query = query.filter(Ticket.user_id == user_id)
        
        # Permission check: non-admins can only see their own tickets
        if not current_user.is_admin:
            query = query.filter(Ticket.user_id == current_user.id)
        
        # Get total count
        total_count = query.count()
        
        # Get tickets ordered by newest first
        tickets = query.order_by(Ticket.created_at.desc()).all()
        
        # Format response with user names
        formatted_tickets = []
        for ticket in tickets:
            user = db.query(User).filter(User.id == ticket.user_id).first()
            assigned_admin = None
            if ticket.assigned_to:
                assigned_admin = db.query(User).filter(User.id == ticket.assigned_to).first()
            
            formatted_tickets.append(TicketOut(
                id=ticket.id,
                user_id=ticket.user_id,
                subject=ticket.subject,
                message=ticket.message,
                status=ticket.status,
                importance=ticket.importance,
                attachment_path=ticket.attachment_path,
                assigned_to=ticket.assigned_to,
                created_at=ticket.created_at,
                updated_at=ticket.updated_at,
                user_name=user.name if user else None,
                assigned_admin_name=assigned_admin.name if assigned_admin else None
            ))
        
        return TicketListResponse(
            total_count=total_count,
            tickets=formatted_tickets
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tickets: {str(e)}"
        )

@router.get("/tickets/{ticket_id}", response_model=TicketOut)
async def get_ticket(
    ticket_id: int = Path(..., description="Ticket ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific ticket by ID
    """
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Permission check: users can only see their own tickets, admins can see all
        if not current_user.is_admin and ticket.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own tickets"
            )
        
        # Get user names
        user = db.query(User).filter(User.id == ticket.user_id).first()
        assigned_admin = None
        if ticket.assigned_to:
            assigned_admin = db.query(User).filter(User.id == ticket.assigned_to).first()
        
        return TicketOut(
            id=ticket.id,
            user_id=ticket.user_id,
            subject=ticket.subject,
            message=ticket.message,
            status=ticket.status,
            importance=ticket.importance,
            attachment_path=ticket.attachment_path,
            assigned_to=ticket.assigned_to,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            user_name=user.name if user else None,
            assigned_admin_name=assigned_admin.name if assigned_admin else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve ticket: {str(e)}"
        )

@router.put("/tickets/{ticket_id}", response_model=TicketOut)
async def update_ticket(
    ticket_update: TicketUpdate,
    ticket_id: int = Path(..., description="Ticket ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a ticket (status, assignment, or add reply)
    """
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Permission check: users can only update their own tickets, admins can update all
        if not current_user.is_admin and ticket.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own tickets"
            )
        
        # Update fields
        if ticket_update.status is not None:
            # Only admins can change status
            if not current_user.is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admins can change ticket status"
                )
            ticket.status = ticket_update.status
        
        if ticket_update.assigned_to is not None:
            # Only admins can assign tickets
            if not current_user.is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admins can assign tickets"
                )
            # Verify assigned user exists and is admin
            assigned_user = db.query(User).filter(User.id == ticket_update.assigned_to).first()
            if not assigned_user or not assigned_user.is_admin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assigned user must be an admin"
                )
            ticket.assigned_to = ticket_update.assigned_to
        
        if ticket_update.message is not None:
            # Users can add replies to their own tickets
            if not current_user.is_admin and ticket.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only add replies to your own tickets"
                )
            # Append the new message to existing message
            ticket.message += f"\n\n--- Reply from {current_user.name} ---\n{ticket_update.message}"
        
        db.commit()
        db.refresh(ticket)
        
        # Get user names for response
        user = db.query(User).filter(User.id == ticket.user_id).first()
        assigned_admin = None
        if ticket.assigned_to:
            assigned_admin = db.query(User).filter(User.id == ticket.assigned_to).first()
        
        return TicketOut(
            id=ticket.id,
            user_id=ticket.user_id,
            subject=ticket.subject,
            message=ticket.message,
            status=ticket.status,
            importance=ticket.importance,
            attachment_path=ticket.attachment_path,
            assigned_to=ticket.assigned_to,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            user_name=user.name if user else None,
            assigned_admin_name=assigned_admin.name if assigned_admin else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update ticket: {str(e)}"
        )

@router.delete("/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: int = Path(..., description="Ticket ID"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a ticket (admin only)
    """
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        db.delete(ticket)
        db.commit()
        
        return {"message": "Ticket deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete ticket: {str(e)}"
        ) 

@router.get("/tickets/{ticket_id}/attachment")
async def get_ticket_attachment(
    ticket_id: int = Path(..., description="Ticket ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get ticket attachment file
    """
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Permission check: users can only see their own ticket attachments, admins can see all
        if not current_user.is_admin and ticket.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view attachments for your own tickets"
            )
        
        if not ticket.attachment_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No attachment found for this ticket"
            )
        
        # Security check: ensure the file path is within the upload directory
        file_path = PathLib(ticket.attachment_path)
        upload_path = PathLib(UPLOAD_DIR).resolve()
        if not file_path.resolve().is_relative_to(upload_path):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid file path"
            )
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment file not found"
            )
        
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve attachment: {str(e)}"
        )

def include_ticket_router(app):
    """
    Include the ticket router in the FastAPI app
    
    Args:
        app: FastAPI app instance
    """
    from routers import ticket
    app.include_router(ticket.router, prefix="/api", tags=["tickets"]) 