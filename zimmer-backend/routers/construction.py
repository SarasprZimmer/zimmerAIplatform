from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List
from database import get_db
from models import ConstructionEmail
import json
import os

router = APIRouter()

CONFIG_FILE_PATH = "construction_config.json"

def get_config_file_path():
    """Get the full path to the construction config file"""
    return os.path.join(os.getcwd(), CONFIG_FILE_PATH)

def load_construction_config() -> dict:
    """Load construction configuration from file"""
    config_path = get_config_file_path()
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            default_config = {"isUnderConstruction": False}
            return default_config
    except Exception as e:
        print(f"Error loading construction config: {e}")
        return {"isUnderConstruction": False}

class EmailSubmission(BaseModel):
    email: EmailStr

class ConstructionEmailResponse(BaseModel):
    id: int
    email: str
    submitted_at: datetime
    
    class Config:
        from_attributes = True

class ConstructionConfigResponse(BaseModel):
    isUnderConstruction: bool

@router.get("/config", response_model=ConstructionConfigResponse)
async def get_construction_config():
    """Get current construction configuration (public endpoint)"""
    config = load_construction_config()
    return ConstructionConfigResponse(**config)

@router.post("/submit-email", response_model=dict)
async def submit_construction_email(
    email_data: EmailSubmission,
    db: Session = Depends(get_db)
):
    """Submit email for construction page notifications"""
    try:
        # Check if email already exists
        existing_email = db.query(ConstructionEmail).filter(
            ConstructionEmail.email == email_data.email
        ).first()
        
        if existing_email:
            return {"message": "Email already registered", "status": "exists"}
        
        # Create new email record
        new_email = ConstructionEmail(
            email=email_data.email,
            submitted_at=datetime.utcnow()
        )
        
        db.add(new_email)
        db.commit()
        db.refresh(new_email)
        
        return {"message": "Email registered successfully", "status": "success"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to register email: {str(e)}")

@router.get("/emails", response_model=List[ConstructionEmailResponse])
async def get_construction_emails(
    db: Session = Depends(get_db)
):
    """Get all submitted construction emails (admin only)"""
    try:
        emails = db.query(ConstructionEmail).order_by(
            ConstructionEmail.submitted_at.desc()
        ).all()
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")

@router.delete("/emails/{email_id}")
async def delete_construction_email(
    email_id: int,
    db: Session = Depends(get_db)
):
    """Delete a construction email (admin only)"""
    try:
        email = db.query(ConstructionEmail).filter(
            ConstructionEmail.id == email_id
        ).first()
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        db.delete(email)
        db.commit()
        
        return {"message": "Email deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete email: {str(e)}")
