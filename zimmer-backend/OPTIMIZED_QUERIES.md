
# Optimized Query Examples

## 1. User Dashboard Query (Optimized)
```python
def get_user_dashboard_optimized(db: Session, user_id: int):
    # Use single query with proper joins
    query = db.query(
        UserAutomation,
        Automation.name,
        Automation.description,
        Automation.pricing_type,
        Automation.price_per_token,
        Automation.status
    ).join(
        Automation, UserAutomation.automation_id == Automation.id
    ).filter(
        UserAutomation.user_id == user_id
    ).options(
        # Use eager loading to prevent N+1 queries
        joinedload(UserAutomation.automation)
    )
    
    return query.all()
```

## 2. Token Usage Query (Optimized)
```python
def get_weekly_usage_optimized(db: Session, user_id: int):
    # Use indexed columns and proper date functions
    six_days_ago = datetime.utcnow() - timedelta(days=6)
    
    query = db.query(
        func.date(TokenUsage.created_at).label('day'),
        func.sum(TokenUsage.tokens_used).label('tokens'),
        func.count(TokenUsage.id).label('sessions')
    ).filter(
        TokenUsage.user_id == user_id,
        TokenUsage.created_at >= six_days_ago
    ).group_by(
        func.date(TokenUsage.created_at)
    ).order_by('day')
    
    return query.all()
```

## 3. Admin Dashboard Query (Optimized)
```python
def get_admin_dashboard_optimized(db: Session):
    # Use subqueries for better performance
    stats = db.query(
        func.count(User.id).label('total_users'),
        func.count(Automation.id).label('total_automations'),
        func.count(Ticket.id).label('total_tickets'),
        func.count(UserAutomation.id).label('active_automations')
    ).first()
    
    return stats
```
