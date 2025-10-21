from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
from utils.auth_dependency import get_current_user
import json
import os

router = APIRouter()

class ConstructionConfigUpdate(BaseModel):
    isUnderConstruction: bool

class ConstructionConfigResponse(BaseModel):
    isUnderConstruction: bool

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
            save_construction_config(default_config)
            return default_config
    except Exception as e:
        print(f"Error loading construction config: {e}")
        return {"isUnderConstruction": False}

def save_construction_config(config: dict):
    """Save construction configuration to file"""
    config_path = get_config_file_path()
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving construction config: {e}")
        raise HTTPException(status_code=500, detail="Failed to save configuration")

@router.get("/construction-config", response_model=ConstructionConfigResponse)
async def get_construction_config(
    current_user: User = Depends(get_current_user)
):
    """Get current construction configuration (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    config = load_construction_config()
    return ConstructionConfigResponse(**config)

@router.put("/construction-config", response_model=ConstructionConfigResponse)
async def update_construction_config(
    config_update: ConstructionConfigUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update construction configuration (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        new_config = {"isUnderConstruction": config_update.isUnderConstruction}
        save_construction_config(new_config)
        return ConstructionConfigResponse(**new_config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")
