#!/usr/bin/env python3
"""
Example integration of admin notifications with existing Zimmer systems
"""
from database import SessionLocal
from models.user import User
from models.notification import Notification
from datetime import datetime

def create_maintenance_notification(maintenance_id: str, duration: str, affected_users: list[int] = None):
    """Create maintenance notification for specific users or all users"""
    db = SessionLocal()
    try:
        title = "Scheduled Maintenance"
        body = f"System will be down for maintenance for {duration}"
        data = {
            "maintenance_id": maintenance_id,
            "duration": duration,
            "scheduled_at": datetime.utcnow().isoformat()
        }
        
        if affected_users:
            # Send to specific users
            for user_id in affected_users:
                notification = Notification(
                    user_id=user_id,
                    type="system",
                    title=title,
                    body=body,
                    data=data
                )
                db.add(notification)
        else:
            # Broadcast to all active users
            users = db.query(User.id).filter(User.is_active == True).all()
            for (user_id,) in users:
                notification = Notification(
                    user_id=user_id,
                    type="system",
                    title=title,
                    body=body,
                    data=data
                )
                db.add(notification)
        
        db.commit()
        print(f"✅ Maintenance notification created for {len(affected_users) if affected_users else 'all'} users")
        
    except Exception as e:
        print(f"❌ Failed to create maintenance notification: {e}")
        db.rollback()
    finally:
        db.close()

def create_system_update_notification(version: str, features: list[str]):
    """Create system update notification for all users"""
    db = SessionLocal()
    try:
        title = f"System Update v{version}"
        body = f"New features have been deployed: {', '.join(features)}"
        data = {
            "version": version,
            "features": features,
            "deployed_at": datetime.utcnow().isoformat()
        }
        
        # Get all active users
        users = db.query(User.id).filter(User.is_active == True).all()
        
        # Create notifications in batch
        notifications = []
        for (user_id,) in users:
            notifications.append(Notification(
                user_id=user_id,
                type="system",
                title=title,
                body=body,
                data=data
            ))
        
        db.bulk_save_objects(notifications)
        db.commit()
        print(f"✅ System update notification created for {len(notifications)} users")
        
    except Exception as e:
        print(f"❌ Failed to create system update notification: {e}")
        db.rollback()
    finally:
        db.close()

def create_role_specific_notification(role: str, title: str, body: str, data: dict = None):
    """Create notification for users with specific role"""
    db = SessionLocal()
    try:
        # Get users with specific role
        users = db.query(User.id).filter(User.role == role, User.is_active == True).all()
        
        if not users:
            print(f"⚠️  No active users found with role: {role}")
            return
        
        # Create notifications
        notifications = []
        for (user_id,) in users:
            notifications.append(Notification(
                user_id=user_id,
                type="system",
                title=title,
                body=body,
                data=data or {}
            ))
        
        db.bulk_save_objects(notifications)
        db.commit()
        print(f"✅ Role-specific notification created for {len(notifications)} {role} users")
        
    except Exception as e:
        print(f"❌ Failed to create role-specific notification: {e}")
        db.rollback()
    finally:
        db.close()

def create_payment_failure_notification(user_id: int, payment_id: str, amount: int):
    """Create payment failure notification for specific user"""
    db = SessionLocal()
    try:
        notification = Notification(
            user_id=user_id,
            type="payment",
            title="Payment Failed",
            body=f"Your payment of {amount:,} Rial could not be processed",
            data={
                "payment_id": payment_id,
                "amount": amount,
                "status": "failed",
                "retry_url": f"/payment/retry/{payment_id}"
            }
        )
        db.add(notification)
        db.commit()
        print(f"✅ Payment failure notification created for user {user_id}")
        
    except Exception as e:
        print(f"❌ Failed to create payment failure notification: {e}")
        db.rollback()
    finally:
        db.close()

def create_support_ticket_notification(user_id: int, ticket_id: int, message_preview: str):
    """Create support ticket notification for user"""
    db = SessionLocal()
    try:
        notification = Notification(
            user_id=user_id,
            type="ticket",
            title=f"Support Ticket #{ticket_id} Updated",
            body=f"Your support ticket has received a new response: {message_preview[:100]}...",
            data={
                "ticket_id": ticket_id,
                "message_preview": message_preview[:100],
                "ticket_url": f"/support/{ticket_id}"
            }
        )
        db.add(notification)
        db.commit()
        print(f"✅ Support ticket notification created for user {user_id}")
        
    except Exception as e:
        print(f"❌ Failed to create support ticket notification: {e}")
        db.rollback()
    finally:
        db.close()

# Example usage
if __name__ == "__main__":
    print("🔧 Admin Notification Integration Examples")
    print("=" * 50)
    
    # Example 1: Maintenance notification
    print("\n1️⃣ Maintenance Notification:")
    create_maintenance_notification(
        maintenance_id="maint_2025_001",
        duration="30 minutes",
        affected_users=[1, 2, 3]  # Specific users
    )
    
    # Example 2: System update notification
    print("\n2️⃣ System Update Notification:")
    create_system_update_notification(
        version="2.1.0",
        features=["Real-time notifications", "Improved UI", "Better performance"]
    )
    
    # Example 3: Role-specific notification
    print("\n3️⃣ Role-Specific Notification:")
    create_role_specific_notification(
        role="support_staff",
        title="New Support Guidelines",
        body="Please review the updated support procedures",
        data={"guideline_url": "/docs/support-guidelines-v2"}
    )
    
    # Example 4: Payment failure notification
    print("\n4️⃣ Payment Failure Notification:")
    create_payment_failure_notification(
        user_id=1,
        payment_id="pay_123456",
        amount=100000
    )
    
    # Example 5: Support ticket notification
    print("\n5️⃣ Support Ticket Notification:")
    create_support_ticket_notification(
        user_id=1,
        ticket_id=123,
        message_preview="Thank you for your patience. We have resolved the issue you reported..."
    )
    
    print("\n✅ All integration examples completed!")
