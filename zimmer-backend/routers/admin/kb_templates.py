from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import SessionLocal
from models.kb_template import KBTemplate
from models.automation import Automation
from models.user import User
from schemas.kb_template import KBTemplateCreate, KBTemplateUpdate, KBTemplateResponse, KBTemplateListResponse
from utils.auth_dependency import get_current_admin_user
from database import get_db

router = APIRouter()

@router.get("/kb-templates", response_model=KBTemplateListResponse)
def list_kb_templates(
    automation_id: Optional[int] = Query(None, description="Filter by automation ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all KB templates with optional filtering"""
    try:
        # Build base query with automation join
        query = db.query(
            KBTemplate,
            Automation.name.label('automation_name')
        ).join(
            Automation, KBTemplate.automation_id == Automation.id
        )
        
        # Apply filters if provided
        if automation_id is not None:
            query = query.filter(KBTemplate.automation_id == automation_id)
        
        if category is not None:
            query = query.filter(KBTemplate.category == category)
        
        # Get total count
        total_count = query.count()
        
        # Get templates ordered by newest first
        template_records = query.order_by(
            KBTemplate.created_at.desc()
        ).all()
        
        # Format response
        formatted_templates = []
        for record, automation_name in template_records:
            formatted_templates.append({
                "id": record.id,
                "automation_id": record.automation_id,
                "category": record.category,
                "question": record.question,
                "answer": record.answer,
                "created_at": record.created_at,
                "updated_at": record.updated_at,
                "automation_name": automation_name
            })
        
        return KBTemplateListResponse(
            total_count=total_count,
            templates=formatted_templates
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve KB templates: {str(e)}"
        )

@router.post("/kb-templates", response_model=KBTemplateResponse, status_code=201)
def create_kb_template(
    template_in: KBTemplateCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Create a new KB template"""
    try:
        # Verify automation exists
        automation = db.query(Automation).filter(Automation.id == template_in.automation_id).first()
        if not automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation not found"
            )
        
        # Create new template
        template = KBTemplate(**template_in.dict())
        db.add(template)
        db.commit()
        db.refresh(template)
        
        # Return with automation name
        return KBTemplateResponse(
            id=template.id,
            automation_id=template.automation_id,
            category=template.category,
            question=template.question,
            answer=template.answer,
            created_at=template.created_at,
            updated_at=template.updated_at,
            automation_name=automation.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create KB template: {str(e)}"
        )

@router.get("/kb-templates/{template_id}", response_model=KBTemplateResponse)
def get_kb_template(
    template_id: int = Path(..., description="Template ID"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get a specific KB template"""
    try:
        template_record = db.query(
            KBTemplate,
            Automation.name.label('automation_name')
        ).join(
            Automation, KBTemplate.automation_id == Automation.id
        ).filter(KBTemplate.id == template_id).first()
        
        if not template_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KB template not found"
            )
        
        template, automation_name = template_record
        
        return KBTemplateResponse(
            id=template.id,
            automation_id=template.automation_id,
            category=template.category,
            question=template.question,
            answer=template.answer,
            created_at=template.created_at,
            updated_at=template.updated_at,
            automation_name=automation_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve KB template: {str(e)}"
        )

@router.put("/kb-templates/{template_id}", response_model=KBTemplateResponse)
def update_kb_template(
    template_id: int = Path(..., description="Template ID"),
    template_in: KBTemplateUpdate = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update a KB template"""
    try:
        template = db.query(KBTemplate).filter(KBTemplate.id == template_id).first()
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KB template not found"
            )
        
        # Update fields if provided
        update_data = template_in.dict(exclude_unset=True)
        if update_data:
            for field, value in update_data.items():
                setattr(template, field, value)
            template.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(template)
        
        # Get automation name for response
        automation = db.query(Automation).filter(Automation.id == template.automation_id).first()
        
        return KBTemplateResponse(
            id=template.id,
            automation_id=template.automation_id,
            category=template.category,
            question=template.question,
            answer=template.answer,
            created_at=template.created_at,
            updated_at=template.updated_at,
            automation_name=automation.name if automation else "Unknown"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update KB template: {str(e)}"
        )

@router.delete("/kb-templates/{template_id}", status_code=204)
def delete_kb_template(
    template_id: int = Path(..., description="Template ID"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Delete a KB template"""
    try:
        template = db.query(KBTemplate).filter(KBTemplate.id == template_id).first()
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KB template not found"
            )
        
        db.delete(template)
        db.commit()
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete KB template: {str(e)}"
        ) 