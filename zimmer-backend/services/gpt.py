"""
GPT Service for Zimmer Dashboard
Handles AI response generation with multi-key management and fallback logic
"""

import openai
from typing import Optional
import os
from dotenv import load_dotenv
from models.knowledge import KnowledgeEntry
from services.openai_key_manager import OpenAIKeyManager
from utils.crypto import decrypt_secret
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Configure OpenAI (using dummy key for development)
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-dummy-key-for-development")

def search_knowledge_base(db, client_id: int, category: str) -> Optional[str]:
    """
    Search the knowledge base for a given client and category.
    Returns the answer if found, else None.
    """
    entry = db.query(KnowledgeEntry).filter(
        KnowledgeEntry.client_id == client_id,
        KnowledgeEntry.category == category
    ).first()
    if entry:
        return entry.answer
    return None

def generate_gpt_response(db, message: str, client_id: int = None, category: str = None, automation_id: int = None, user_id: int = None) -> Optional[str]:
    """
    Generate GPT response for user message with multi-key management and fallback logic
    """
    # 1. Try knowledge base if db, client_id, and category are provided
    if db and client_id and category:
        kb_answer = search_knowledge_base(db, client_id, category)
        if kb_answer:
            return kb_answer
    
    # Fallback rules - check for complex keywords
    complex_keywords = ["complex", "technical", "specific", "detailed", "custom"]
    message_lower = message.lower()
    has_complex_keywords = any(keyword in message_lower for keyword in complex_keywords)
    word_count = len(message.split())
    is_too_long = word_count > 20
    if has_complex_keywords or is_too_long:
        return None
    
    # Multi-key GPT call
    if automation_id and db:
        return generate_gpt_response_with_keys(db, message, automation_id, user_id)
    else:
        # Fallback to single key (legacy behavior)
        return generate_gpt_response_single_key(message)

def generate_gpt_response_with_keys(db, message: str, automation_id: int, user_id: int = None) -> Optional[str]:
    """
    Generate GPT response using multi-key management
    """
    key_manager = OpenAIKeyManager(db)
    max_retries = 3  # Try up to 3 different keys
    
    for attempt in range(max_retries):
        # Select the best available key
        key = key_manager.select_key(automation_id)
        if not key:
            logger.error(f"No available OpenAI keys for automation {automation_id}")
            return "در حال حاضر سرویس تولید محتوا در دسترس نیست. لطفاً بعداً دوباره تلاش کنید."
        
        try:
            # Decrypt the key
            decrypted_key = decrypt_secret(key.key_encrypted)
            
            # Create OpenAI client with this key
            client = openai.OpenAI(api_key=decrypted_key)
            
            # Make the API call
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant for Zimmer, a travel and visa services company. Provide clear, concise, and helpful responses to customer inquiries. Keep responses friendly and professional."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            result = response.choices[0].message.content.strip()
            
            # Record successful usage
            total_tokens = response.usage.total_tokens
            key_manager.record_usage(
                key_id=key.id,
                tokens_used=total_tokens,
                ok=True,
                model=response.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                automation_id=automation_id,
                user_id=user_id
            )
            
            return result
            
        except openai.AuthenticationError as e:
            # Authentication error - disable key and try next
            logger.warning(f"Authentication error for key {key.id}: {e}")
            should_retry = key_manager.handle_failure(key.id, "401")
            if not should_retry:
                break
                
        except openai.RateLimitError as e:
            # Rate limit - try next key
            logger.warning(f"Rate limit for key {key.id}: {e}")
            should_retry = key_manager.handle_failure(key.id, "429")
            if not should_retry:
                break
                
        except openai.APIError as e:
            # API error - try next key
            error_code = str(e.status_code) if hasattr(e, 'status_code') else "500"
            logger.error(f"API error for key {key.id}: {e}")
            should_retry = key_manager.handle_failure(key.id, error_code)
            if not should_retry:
                break
                
        except Exception as e:
            # Other errors - log and try next key
            logger.error(f"Unexpected error for key {key.id}: {e}")
            should_retry = key_manager.handle_failure(key.id, "unknown")
            if not should_retry:
                break
    
    # All keys failed
    return "در حال حاضر سرویس تولید محتوا در دسترس نیست. لطفاً بعداً دوباره تلاش کنید."

def generate_gpt_response_single_key(message: str) -> Optional[str]:
    """
    Generate GPT response using single key (legacy behavior)
    """
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant for Zimmer, a travel and visa services company. Provide clear, concise, and helpful responses to customer inquiries. Keep responses friendly and professional."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            max_tokens=150,
            temperature=0.7
        )
        result = response.choices[0].message.content.strip()
        return result
    except Exception as e:
        logger.error(f"GPT API error: {str(e)}")
        if "Incorrect API key" in str(e):
            return f"Hello! I'm Zimmer's AI assistant. I'd be happy to help you with {message.lower()}. Please contact our support team for more detailed assistance."
        return None

def count_tokens(text: str) -> int:
    """
    Estimate token count for text (simplified implementation)
    
    Args:
        text (str): Text to count tokens for
        
    Returns:
        int: Estimated token count
    """
    # Simple estimation: 1 token ≈ 4 characters for English text
    return len(text) // 4

def get_response_cost(tokens_used: int) -> float:
    """
    Calculate cost for GPT-4 response
    
    Args:
        tokens_used (int): Number of tokens used
        
    Returns:
        float: Cost in USD
    """
    # GPT-4 pricing (approximate)
    # Input: $0.03 per 1K tokens
    # Output: $0.06 per 1K tokens
    # For simplicity, we'll use average cost
    cost_per_token = 0.000045  # Average of input/output cost
    return tokens_used * cost_per_token 