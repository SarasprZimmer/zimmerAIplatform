# Notifications System - Zimmer Backend

A lightweight notifications MVP for the Zimmer platform that allows creating, listing, and managing user notifications.

## Features

- ✅ **User-specific notifications** - Each notification is tied to a specific user
- ✅ **Multiple notification types** - Support for 'payment', 'ticket', 'system', etc.
- ✅ **Rich content** - Title, body, and optional JSON data payload
- ✅ **Read status tracking** - Mark individual or all notifications as read
- ✅ **Pagination support** - List notifications with limit/offset
- ✅ **Automatic timestamps** - Created and read timestamps
- ✅ **Cascade deletion** - Notifications are deleted when user is deleted

## Database Schema

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(64) NOT NULL,
    title VARCHAR(200) NOT NULL,
    body VARCHAR(2000),
    data JSON,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ix_notifications_user_id ON notifications(user_id);
```

## API Endpoints

### List Notifications
```http
GET /api/notifications?limit=20&offset=0
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "type": "payment",
    "title": "Payment Successful",
    "body": "Your payment has been processed",
    "data": {"payment_id": 123, "amount": 100000},
    "is_read": false,
    "created_at": "2025-08-27T22:32:57.229093",
    "read_at": null
  }
]
```

### Mark Specific Notifications as Read
```http
POST /api/notifications/mark-read
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "updated": 3
}
```

### Mark All Notifications as Read
```http
POST /api/notifications/mark-all-read
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "updated": 5
}
```

## Usage Examples

### Creating Notifications

```python
from services.notify import create_notification
from database import SessionLocal

# Create a payment notification
db = SessionLocal()
notification = create_notification(
    db=db,
    user_id=1,
    type="payment",
    title="Payment Successful",
    body="Your payment of 100,000 Rial has been processed successfully.",
    data={"payment_id": 123, "amount": 100000}
)
db.close()
```

### Creating System Notifications

```python
# System maintenance notification
create_notification(
    db=db,
    user_id=1,
    type="system",
    title="Scheduled Maintenance",
    body="System will be down for maintenance on Sunday 2-4 AM",
    data={"maintenance_id": "maint_001", "duration": "2 hours"}
)
```

### Creating Ticket Notifications

```python
# Support ticket update
create_notification(
    db=db,
    user_id=1,
    type="ticket",
    title="Ticket #123 Updated",
    body="Your support ticket has received a new response",
    data={"ticket_id": 123, "status": "updated"}
)
```

## Integration Points

### Payment System Integration
```python
# In payment callback handler
def payment_success_callback(payment_id, user_id, amount):
    create_notification(
        db=db,
        user_id=user_id,
        type="payment",
        title="Payment Successful",
        body=f"Your payment of {amount:,} Rial has been processed.",
        data={"payment_id": payment_id, "amount": amount}
    )
```

### Support System Integration
```python
# In ticket message handler
def ticket_message_created(ticket_id, user_id, message):
    create_notification(
        db=db,
        user_id=user_id,
        type="ticket",
        title=f"Ticket #{ticket_id} Updated",
        body="Your support ticket has received a new response",
        data={"ticket_id": ticket_id, "message_preview": message[:100]}
    )
```

### Automation System Integration
```python
# In automation status change handler
def automation_status_changed(user_id, automation_id, status):
    create_notification(
        db=db,
        user_id=user_id,
        type="automation",
        title="Automation Status Changed",
        body=f"Your automation status has changed to {status}",
        data={"automation_id": automation_id, "status": status}
    )
```

## Frontend Integration

### React Hook Example
```typescript
import { useState, useEffect } from 'react';

interface Notification {
  id: number;
  type: string;
  title: string;
  body?: string;
  data?: any;
  is_read: boolean;
  created_at: string;
  read_at?: string;
}

export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    try {
      const response = await fetch('/api/notifications');
      const data = await response.json();
      setNotifications(data);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (ids: number[]) => {
    try {
      await fetch('/api/notifications/mark-read', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids })
      });
      await fetchNotifications(); // Refresh list
    } catch (error) {
      console.error('Failed to mark notifications as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await fetch('/api/notifications/mark-all-read', {
        method: 'POST'
      });
      await fetchNotifications(); // Refresh list
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  return {
    notifications,
    loading,
    markAsRead,
    markAllAsRead,
    refresh: fetchNotifications
  };
};
```

## Testing

Run the test script to verify the system:
```bash
python test_notifications.py
```

## Migration

The notifications table was created with migration:
```bash
alembic -c alembic.ini revision --autogenerate -m "add notifications table"
alembic -c alembic.ini upgrade head
```

## Admin → Internal Notifications

Administrators can create and broadcast notifications to users through dedicated admin endpoints.

### Create Notifications for Specific Users

```http
POST /api/admin/notifications
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "user_ids": [1, 2, 3],
  "type": "system",
  "title": "Scheduled Maintenance",
  "body": "System will be down for maintenance on Sunday 2-4 AM",
  "data": {"maintenance_id": "maint_001", "duration": "2 hours"}
}
```

**Response:**
```json
{
  "created": 3
}
```

### Broadcast Notifications to All Users

```http
POST /api/admin/notifications/broadcast
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "type": "system",
  "title": "System Update",
  "body": "New features have been deployed",
  "data": {"version": "2.1.0", "features": ["notifications", "improved-ui"]}
}
```

**Response:**
```json
{
  "created": 150
}
```

### Broadcast to Specific Role

```http
POST /api/admin/notifications/broadcast
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "type": "system",
  "title": "Support Staff Notice",
  "body": "New support guidelines have been published",
  "role": "support_staff",
  "data": {"guideline_url": "/docs/support-guidelines"}
}
```

**Response:**
```json
{
  "created": 25
}
```

### Security & Rate Limiting

- **Authentication**: All endpoints require admin access (`admin_required` dependency)
- **Rate Limiting**: Recommended to implement at API gateway level
- **Validation**: Input validation with Pydantic schemas
- **Bulk Operations**: Uses `bulk_save_objects` for efficient batch inserts

### Admin Usage Examples

```python
# Send maintenance notice to specific users
admin_create_notification(
    user_ids=[1, 5, 10],
    type="system",
    title="Database Maintenance",
    body="Database will be unavailable for 30 minutes",
    data={"maintenance_window": "2025-08-28 02:00-02:30"}
)

# Broadcast system update to all users
admin_broadcast_notification(
    type="system",
    title="New Features Available",
    body="Check out the new notification system!",
    data={"features": ["real-time", "mark-as-read", "admin-broadcast"]}
)

# Send role-specific notification
admin_broadcast_notification(
    type="system",
    title="Support Guidelines Updated",
    body="Please review the new support procedures",
    role="support_staff",
    data={"guideline_version": "2025.1"}
)
```

## Future Enhancements

- [ ] **Push notifications** - WebSocket/SSE for real-time updates
- [ ] **Email notifications** - Send email copies of important notifications
- [ ] **Notification preferences** - User settings for notification types
- [ ] **Bulk operations** - Delete multiple notifications
- [ ] **Notification templates** - Predefined templates for common notifications
- [ ] **Notification analytics** - Track read rates and engagement
- [ ] **Scheduled notifications** - Send notifications at specific times
- [ ] **Notification categories** - Organize notifications by priority/importance
