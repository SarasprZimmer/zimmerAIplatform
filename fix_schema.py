import re

# Read the current schema file
with open('zimmer-backend/schemas/automation_admin.py', 'r') as f:
    content = f.read()

# Fix the AutomationResponse to allow None values for dates
old_schema = '''class AutomationResponse(BaseModel):
    id: int
    name: str
    description: str
    price_per_token: float
    pricing_type: PricingType
    status: bool
    api_base_url: Optional[str]
    api_provision_url: Optional[str]
    api_usage_url: Optional[str]
    api_kb_status_url: Optional[str]
    api_kb_reset_url: Optional[str]
    has_service_token: bool
    service_token_masked: Optional[str]
    health_check_url: Optional[str]
    health_status: str
    last_health_at: Optional[str]
    is_listed: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True'''

new_schema = '''class AutomationResponse(BaseModel):
    id: int
    name: str
    description: str
    price_per_token: float
    pricing_type: PricingType
    status: bool
    api_base_url: Optional[str]
    api_provision_url: Optional[str]
    api_usage_url: Optional[str]
    api_kb_status_url: Optional[str]
    api_kb_reset_url: Optional[str]
    has_service_token: bool
    service_token_masked: Optional[str]
    health_check_url: Optional[str]
    health_status: str
    last_health_at: Optional[str]
    is_listed: bool
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True'''

# Apply the replacement
content = content.replace(old_schema, new_schema)

# Write the updated content back
with open('zimmer-backend/schemas/automation_admin.py', 'w') as f:
    f.write(content)

print("✅ Fixed AutomationResponse schema to allow None values for dates")
