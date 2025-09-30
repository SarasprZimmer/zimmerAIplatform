import re

# Read the current automation.py file
with open('zimmer-backend/routers/admin/automation.py', 'r') as f:
    content = f.read()

# Fix the AutomationResponse creation - handle None values for dates
old_response = '''        return AutomationResponse(
            id=automation.id,
            name=automation.name,
            description=automation.description,
            price_per_token=automation.price_per_token,
            pricing_type=automation.pricing_type,
            status=automation.status,
            api_base_url=automation.api_base_url,
            api_provision_url=automation.api_provision_url,
            api_usage_url=automation.api_usage_url,
            api_kb_status_url=automation.api_kb_status_url,
            api_kb_reset_url=automation.api_kb_reset_url,
            has_service_token=bool(automation.service_token_hash),
            service_token_masked=(automation.service_token_hash[:8] + "...") if automation.service_token_hash else None,
            health_check_url=automation.health_check_url,
            health_status=automation.health_status,
            last_health_at=automation.last_health_at.isoformat() if automation.last_health_at else None,
            is_listed=automation.is_listed,
            created_at=automation.created_at.isoformat(),
            updated_at=automation.updated_at.isoformat()
        )'''

new_response = '''        return AutomationResponse(
            id=automation.id,
            name=automation.name,
            description=automation.description,
            price_per_token=automation.price_per_token,
            pricing_type=automation.pricing_type,
            status=automation.status,
            api_base_url=automation.api_base_url,
            api_provision_url=automation.api_provision_url,
            api_usage_url=automation.api_usage_url,
            api_kb_status_url=automation.api_kb_status_url,
            api_kb_reset_url=automation.api_kb_reset_url,
            has_service_token=bool(automation.service_token_hash),
            service_token_masked=(automation.service_token_hash[:8] + "...") if automation.service_token_hash else None,
            health_check_url=automation.health_check_url,
            health_status=automation.health_status,
            last_health_at=automation.last_health_at.isoformat() if automation.last_health_at else None,
            is_listed=automation.is_listed,
            created_at=automation.created_at.isoformat() if automation.created_at else None,
            updated_at=automation.updated_at.isoformat() if automation.updated_at else None
        )'''

# Apply the replacement
content = content.replace(old_response, new_response)

# Also fix the update function response
old_update_response = '''        return AutomationResponse(
            id=automation.id,
            name=automation.name,
            description=automation.description,
            price_per_token=automation.price_per_token,
            pricing_type=automation.pricing_type,
            status=automation.status,
            api_base_url=automation.api_base_url,
            api_provision_url=automation.api_provision_url,
            api_usage_url=automation.api_usage_url,
            api_kb_status_url=automation.api_kb_status_url,
            api_kb_reset_url=automation.api_kb_reset_url,
            has_service_token=bool(automation.service_token_hash),
            service_token_masked=(automation.service_token_hash[:8] + "...") if automation.service_token_hash else None,
            health_check_url=automation.health_check_url,
            health_status=automation.health_status,
            last_health_at=automation.last_health_at.isoformat() if automation.last_health_at else None,
            is_listed=automation.is_listed,
            created_at=automation.created_at.isoformat(),
            updated_at=automation.updated_at.isoformat()
        )'''

new_update_response = '''        return AutomationResponse(
            id=automation.id,
            name=automation.name,
            description=automation.description,
            price_per_token=automation.price_per_token,
            pricing_type=automation.pricing_type,
            status=automation.status,
            api_base_url=automation.api_base_url,
            api_provision_url=automation.api_provision_url,
            api_usage_url=automation.api_usage_url,
            api_kb_status_url=automation.api_kb_status_url,
            api_kb_reset_url=automation.api_kb_reset_url,
            has_service_token=bool(automation.service_token_hash),
            service_token_masked=(automation.service_token_hash[:8] + "...") if automation.service_token_hash else None,
            health_check_url=automation.health_check_url,
            health_status=automation.health_status,
            last_health_at=automation.last_health_at.isoformat() if automation.last_health_at else None,
            is_listed=automation.is_listed,
            created_at=automation.created_at.isoformat() if automation.created_at else None,
            updated_at=automation.updated_at.isoformat() if automation.updated_at else None
        )'''

# Apply the replacement for update function
content = content.replace(old_update_response, new_update_response)

# Write the updated content back
with open('zimmer-backend/routers/admin/automation.py', 'w') as f:
    f.write(content)

print("✅ Fixed automation response to handle None date values")
