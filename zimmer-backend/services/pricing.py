"""
Pricing service for computing payment amounts
"""
from models.automation import Automation, PricingType
from typing import Union


def compute_amount_rial(automation: Automation, tokens: int) -> int:
    """
    Compute payment amount in Rial based on automation pricing and tokens
    
    Args:
        automation: Automation model instance
        tokens: Number of tokens to purchase
        
    Returns:
        Amount in Rial as integer
    """
    if not automation or not automation.price_per_token:
        raise ValueError("Invalid automation or pricing")
    
    if tokens <= 0:
        raise ValueError("Tokens must be positive")
    
    if automation.pricing_type == PricingType.token_per_session:
        # Per session pricing: tokens * price_per_token
        amount = tokens * automation.price_per_token
    elif automation.pricing_type == PricingType.token_per_step:
        # Per step pricing: tokens * price_per_token
        amount = tokens * automation.price_per_token
    elif automation.pricing_type == PricingType.flat_fee:
        # Flat fee: ignore tokens, enforce tokens=1
        if tokens != 1:
            raise ValueError("Flat fee pricing requires exactly 1 token")
        amount = automation.price_per_token
    else:
        raise ValueError(f"Unsupported pricing type: {automation.pricing_type}")
    
    # Ensure amount is positive and convert to integer
    if amount <= 0:
        raise ValueError("Computed amount must be positive")
    
    return int(amount)


def validate_token_range(tokens: int, min_tokens: int = 1, max_tokens: int = 100000) -> bool:
    """
    Validate token amount is within acceptable range
    
    Args:
        tokens: Number of tokens
        min_tokens: Minimum allowed tokens
        max_tokens: Maximum allowed tokens
        
    Returns:
        True if valid, False otherwise
    """
    return min_tokens <= tokens <= max_tokens
