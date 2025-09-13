from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user_automation import UserAutomation
from models.user import User
from models.fallback_log import FallbackLog
from services.gpt import search_knowledge_base, generate_gpt_response
from services.token_manager import deduct_tokens
import requests

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/webhook/telegram/{bot_token}")
async def telegram_webhook(bot_token: str, request: Request, db: Session = Depends(get_db)):
    try:
        # 1. Match bot_token to UserAutomation
        ua = db.query(UserAutomation).filter(UserAutomation.telegram_bot_token == bot_token).first()
        if not ua:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot token not recognized")

        # 2. Get client_id from related User
        user = db.query(User).filter(User.id == ua.user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for automation")
        client_id = user.id

        # 3. Extract message from Telegram JSON
        data = await request.json()
        message_text = None
        chat_id = None
        try:
            message_text = data["message"]["text"]
            chat_id = data["message"]["chat"]["id"]
        except (KeyError, TypeError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Telegram payload")

        # 4. Call search_knowledge_base()
        category = "faq"  # You may want to extract/guess category from message or automation context
        kb_answer = search_knowledge_base(db, client_id, category)

        # 5. If not found → call generate_gpt_response()
        response_text = kb_answer
        if not response_text:
            response_text = generate_gpt_response(db, message_text, client_id, category)

        # 6. If GPT returns None → log to FallbackLog
        if not response_text:
            fallback = FallbackLog(
                user_automation_id=ua.id,
                message=message_text,
                error_type="no_answer"
            )
            db.add(fallback)
            db.commit()
            # Reply to user: fallback message
            reply_text = "Sorry, I couldn't answer your question. Our team will follow up soon."
            send_telegram_message(bot_token, chat_id, reply_text)
            return {"status": "fallback", "detail": "No answer found, fallback logged."}

        # 7. If response found: Deduct 1 token, send reply
        if deduct_tokens(db, ua.id, 1):
            send_telegram_message(bot_token, chat_id, response_text)
            return {"status": "ok", "detail": "Response sent and token deducted."}
        else:
            # 8. If not enough tokens → reply: "Please top up"
            send_telegram_message(bot_token, chat_id, "You have run out of tokens. Please top up to continue using the service.")
            return {"status": "no_tokens", "detail": "Not enough tokens."}
            
    except HTTPException:
        raise
    except Exception as e:
        # Log the error and return a generic response
        print(f"Telegram webhook error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing webhook"
        )

def send_telegram_message(bot_token: str, chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}") 