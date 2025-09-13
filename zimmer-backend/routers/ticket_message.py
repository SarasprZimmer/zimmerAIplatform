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
from models.ticket import Ticket
from models.ticket_message import TicketMessage
from schemas.ticket_message import TicketMessageCreate, TicketMessageUpdate, TicketMessageOut, TicketMessageListResponse
from utils.auth import get_current_user, require_admin

router = APIRouter()

# File upload configuration (same as tickets)
UPLOAD_DIR = "uploads/ticket_messages"
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
    
    # Generate unique filename
    import uuid
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path

@router.post("/tickets/{ticket_id}/messages", response_model=TicketMessageOut)
async def create_ticket_message(
    ticket_id: int = Path(..., description="Ticket ID"),
    message: str = Form(...),
    file: Optional[UploadFile] = File(None),
    is_internal: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a message to a ticket
    """
    try:
        # Verify ticket exists
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Permission check: users can only add messages to their own tickets, admins can add to any
        if not current_user.is_admin and ticket.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only add messages to your own tickets"
            )
        
        # Only admins can create internal messages
        if is_internal and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can create internal messages"
            )
        
        # Handle file upload
        attachment_path = None
        if file:
            attachment_path = save_uploaded_file(file)
        
        # Create new message
        new_message = TicketMessage(
            ticket_id=ticket_id,
            user_id=current_user.id,
            message=message,
            attachment_path=attachment_path,
            is_internal=is_internal
        )
        
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        # Return with user info
        return TicketMessageOut(
            id=new_message.id,
            ticket_id=new_message.ticket_id,
            user_id=new_message.user_id,
            message=new_message.message,
            attachment_path=new_message.attachment_path,
            is_internal=new_message.is_internal,
            created_at=new_message.created_at,
            user_name=current_user.name,
            user_email=current_user.email
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
            detail=f"Failed to create message: {str(e)}"
        )

@router.get("/tickets/{ticket_id}/messages", response_model=TicketMessageListResponse)
async def get_ticket_messages(
    ticket_id: int = Path(..., description="Ticket ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all messages for a ticket
    """
    try:
        # Verify ticket exists
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Permission check: users can only see messages for their own tickets, admins can see all
        if not current_user.is_admin and ticket.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view messages for your own tickets"
            )
        
        # Get messages ordered by creation time
        messages = db.query(TicketMessage).filter(
            TicketMessage.ticket_id == ticket_id
        ).order_by(TicketMessage.created_at.asc()).all()
        
        # Filter internal messages for non-admin users
        if not current_user.is_admin:
            messages = [msg for msg in messages if not msg.is_internal]
        
        # Format response with user names
        formatted_messages = []
        for msg in messages:
            user = db.query(User).filter(User.id == msg.user_id).first()
            formatted_messages.append(TicketMessageOut(
                id=msg.id,
                ticket_id=msg.ticket_id,
                user_id=msg.user_id,
                message=msg.message,
                attachment_path=msg.attachment_path,
                is_internal=msg.is_internal,
                created_at=msg.created_at,
                user_name=user.name if user else None,
                user_email=user.email if user else None
            ))
        
        return TicketMessageListResponse(
            total_count=len(formatted_messages),
            messages=formatted_messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve messages: {str(e)}"
        )

@router.get("/tickets/{ticket_id}/messages/{message_id}/attachment")
async def get_message_attachment(
    ticket_id: int = Path(..., description="Ticket ID"),
    message_id: int = Path(..., description="Message ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get message attachment file
    """
    try:
        # Verify ticket exists
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Permission check: users can only see attachments for their own tickets, admins can see all
        if not current_user.is_admin and ticket.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view attachments for your own tickets"
            )
        
        # Verify message exists
        message = db.query(TicketMessage).filter(
            TicketMessage.id == message_id,
            TicketMessage.ticket_id == ticket_id
        ).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Filter internal messages for non-admin users
        if not current_user.is_admin and message.is_internal:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access internal message attachments"
            )
        
        if not message.attachment_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No attachment found for this message"
            )
        
        # Security check: ensure the file path is within the upload directory
        file_path = PathLib(message.attachment_path)
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

def include_ticket_message_router(app):
    """Include ticket message router in the main app"""
    app.include_router(router, prefix="/api", tags=["ticket-messages"]) 