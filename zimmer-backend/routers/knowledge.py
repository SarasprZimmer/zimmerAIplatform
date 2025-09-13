from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import SessionLocal
from models.user import User
from models.knowledge import KnowledgeEntry
from schemas.knowledge import KnowledgeCreate, KnowledgeOut, KnowledgeListResponse
from utils.auth import require_admin

router = APIRouter()

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/admin/knowledge", response_model=KnowledgeOut)
async def create_knowledge_entry(
    knowledge_data: KnowledgeCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new knowledge base entry (admin only)
    """
    try:
        # Validate and sanitize input
        if not knowledge_data.category or len(knowledge_data.category.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category cannot be empty"
            )
        
        if not knowledge_data.answer or len(knowledge_data.answer.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Answer cannot be empty"
            )
        
        # Sanitize inputs
        category = knowledge_data.category.strip()[:100]  # Limit length
        answer = knowledge_data.answer.strip()[:5000]     # Limit length
        
        # Verify client exists
        client = db.query(User).filter(User.id == knowledge_data.client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Create new knowledge entry
        new_entry = KnowledgeEntry(
            client_id=knowledge_data.client_id,
            category=category,
            answer=answer
        )
        
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        
        # Return with client name
        return KnowledgeOut(
            id=new_entry.id,
            category=new_entry.category,
            answer=new_entry.answer,
            created_at=new_entry.created_at,
            client_name=client.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create knowledge entry: {str(e)}"
        )

@router.get("/admin/knowledge", response_model=KnowledgeListResponse)
async def get_knowledge_entries(
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get knowledge base entries with optional filtering (admin only)
    """
    try:
        # Build base query with user join
        query = db.query(
            KnowledgeEntry,
            User.name.label('client_name')
        ).join(
            User, KnowledgeEntry.client_id == User.id
        )
        
        # Apply filters if provided
        if client_id is not None:
            query = query.filter(KnowledgeEntry.client_id == client_id)
        
        if category is not None:
            query = query.filter(KnowledgeEntry.category == category)
        
        # Get total count
        total_count = query.count()
        
        # Get entries ordered by newest first
        knowledge_records = query.order_by(
            KnowledgeEntry.created_at.desc()
        ).all()
        
        # Format response
        formatted_entries = []
        for record, client_name in knowledge_records:
            formatted_entries.append({
                "id": record.id,
                "category": record.category,
                "answer": record.answer,
                "created_at": record.created_at,
                "client_name": client_name
            })
        
        return KnowledgeListResponse(
            total_count=total_count,
            knowledge_entries=formatted_entries
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve knowledge entries: {str(e)}"
        )

@router.get("/knowledge", response_model=KnowledgeListResponse)
async def get_public_knowledge_entries(
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """
    Get public knowledge base entries (no authentication required)
    """
    try:
        # Build base query with user join
        query = db.query(
            KnowledgeEntry,
            User.name.label('client_name')
        ).join(
            User, KnowledgeEntry.client_id == User.id
        )
        
        # Apply category filter if provided
        if category is not None:
            query = query.filter(KnowledgeEntry.category == category)
        
        # Get total count
        total_count = query.count()
        
        # Get entries ordered by newest first
        knowledge_records = query.order_by(
            KnowledgeEntry.created_at.desc()
        ).all()
        
        # Format response
        formatted_entries = []
        for record, client_name in knowledge_records:
            formatted_entries.append({
                "id": record.id,
                "category": record.category,
                "answer": record.answer,
                "created_at": record.created_at,
                "client_name": client_name
            })
        
        return KnowledgeListResponse(
            total_count=total_count,
            knowledge_entries=formatted_entries
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve knowledge entries: {str(e)}"
        ) 