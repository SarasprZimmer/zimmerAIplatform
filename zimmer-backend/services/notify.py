from sqlalchemy.orm import Session
from models.notification import Notification

def create_notification(db: Session, user_id: int, type: str, title: str, body: str = "", data=None):
    n = Notification(user_id=user_id, type=type, title=title, body=body, data=data or {})
    db.add(n)
    db.commit()
    db.refresh(n)
    return n
