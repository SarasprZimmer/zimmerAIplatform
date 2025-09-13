import re
import html
from typing import Optional
from pydantic import validator

def sanitize_text(text: str) -> str:
    """
    Sanitize text by stripping whitespace and normalizing unicode spaces.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text with normalized whitespace
    """
    if not text:
        return ""
    
    # Convert to string if not already
    text = str(text)
    
    # Normalize unicode spaces and control characters
    # Replace various unicode spaces with regular space
    unicode_spaces = [
        '\u00A0',  # NO-BREAK SPACE
        '\u2000',  # EN QUAD
        '\u2001',  # EM QUAD
        '\u2002',  # EN SPACE
        '\u2003',  # EM SPACE
        '\u2004',  # THREE-PER-EM SPACE
        '\u2005',  # FOUR-PER-EM SPACE
        '\u2006',  # SIX-PER-EM SPACE
        '\u2007',  # FIGURE SPACE
        '\u2008',  # PUNCTUATION SPACE
        '\u2009',  # THIN SPACE
        '\u200A',  # HAIR SPACE
        '\u202F',  # NARROW NO-BREAK SPACE
        '\u205F',  # MEDIUM MATHEMATICAL SPACE
        '\u3000',  # IDEOGRAPHIC SPACE
    ]
    
    for space in unicode_spaces:
        text = text.replace(space, ' ')
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    # Collapse multiple spaces into single space
    text = re.sub(r'\s+', ' ', text)
    
    return text

def forbid_html(text: str) -> str:
    """
    Remove HTML tags and escape HTML entities.
    
    Args:
        text: Input text that may contain HTML
        
    Returns:
        Text with HTML removed and entities escaped
    """
    if not text:
        return ""
    
    text = str(text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Escape HTML entities
    text = html.escape(text)
    
    return text

def escape_html(text: str) -> str:
    """
    Escape HTML entities without removing tags.
    Use this for fields that should preserve formatting but prevent XSS.
    
    Args:
        text: Input text to escape
        
    Returns:
        Text with HTML entities escaped
    """
    if not text:
        return ""
    
    return html.escape(str(text))

def validate_email(email: str) -> str:
    """
    Validate and sanitize email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        Sanitized email address
        
    Raises:
        ValueError: If email is invalid
    """
    if not email:
        raise ValueError("Email cannot be empty")
    
    email = sanitize_text(email).lower()
    
    # Basic email regex validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    
    # Additional checks
    if len(email) > 254:  # RFC 5321 limit
        raise ValueError("Email too long")
    
    if email.count('@') != 1:
        raise ValueError("Invalid email format")
    
    local_part, domain = email.split('@')
    
    if len(local_part) > 64:  # RFC 5321 limit
        raise ValueError("Email local part too long")
    
    if len(domain) > 253:  # RFC 5321 limit
        raise ValueError("Email domain too long")
    
    return email

def validate_phone(phone: str) -> str:
    """
    Validate and sanitize phone number.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Sanitized phone number
        
    Raises:
        ValueError: If phone is invalid
    """
    if not phone:
        return ""
    
    phone = sanitize_text(phone)
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Handle Iranian phone numbers
    if digits_only.startswith('0098'):
        digits_only = digits_only[4:]  # Remove 0098
    elif digits_only.startswith('98'):
        digits_only = digits_only[2:]  # Remove 98
    elif digits_only.startswith('0'):
        digits_only = digits_only[1:]  # Remove leading 0
    
    # Iranian mobile numbers are 10 digits starting with 9
    if len(digits_only) == 10 and digits_only.startswith('9'):
        return f"+98{digits_only}"
    
    # Iranian landline numbers are 10 digits starting with 1-8
    elif len(digits_only) == 10 and re.match(r'^[1-8]', digits_only):
        return f"+98{digits_only}"
    
    # International format
    elif len(digits_only) >= 10 and len(digits_only) <= 15:
        return f"+{digits_only}"
    
    else:
        raise ValueError("Invalid phone number format")

# Pydantic validators for use in schemas
def validate_string_field(value: str, max_length: int = 255, allow_html: bool = False) -> str:
    """
    Generic string field validator for Pydantic schemas.
    
    Args:
        value: String value to validate
        max_length: Maximum allowed length
        allow_html: Whether to allow HTML content
        
    Returns:
        Sanitized string
        
    Raises:
        ValueError: If validation fails
    """
    if not value:
        return ""
    
    # Sanitize text
    value = sanitize_text(value)
    
    # Check length
    if len(value) > max_length:
        raise ValueError(f"Field too long. Maximum {max_length} characters allowed.")
    
    # Handle HTML
    if not allow_html:
        value = forbid_html(value)
    
    return value

def validate_text_field(value: str, max_length: int = 20000, allow_html: bool = False) -> str:
    """
    Generic text field validator for longer content.
    
    Args:
        value: Text value to validate
        max_length: Maximum allowed length
        allow_html: Whether to allow HTML content
        
    Returns:
        Sanitized text
        
    Raises:
        ValueError: If validation fails
    """
    if not value:
        return ""
    
    # Sanitize text
    value = sanitize_text(value)
    
    # Check length
    if len(value) > max_length:
        raise ValueError(f"Text too long. Maximum {max_length} characters allowed.")
    
    # Handle HTML
    if not allow_html:
        value = forbid_html(value)
    
    return value

# Pydantic validator decorators for common field types
def email_validator():
    """Pydantic validator for email fields."""
    return validator('email', pre=True, allow_reuse=True)(validate_email)

def phone_validator():
    """Pydantic validator for phone fields."""
    return validator('phone_number', pre=True, allow_reuse=True)(validate_phone)

def string_validator(max_length: int = 255, allow_html: bool = False):
    """Pydantic validator for string fields."""
    def validator_func(value):
        return validate_string_field(value, max_length, allow_html)
    return validator('*', pre=True, allow_reuse=True)(validator_func)

def text_validator(max_length: int = 20000, allow_html: bool = False):
    """Pydantic validator for text fields."""
    def validator_func(value):
        return validate_text_field(value, max_length, allow_html)
    return validator('*', pre=True, allow_reuse=True)(validator_func)
