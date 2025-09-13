import sys
sys.path.append('.')
from database import SessionLocal, engine, Base
from models.user import User

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Get database session
db = SessionLocal()

try:
    # Count and list users
    users = db.query(User).all()
    print(f'Found {len(users)} users:')
    for user in users:
        print(f'- {user.email} ({user.name})')
    
    if len(users) > 0:
        confirm = input('Delete all users? (type YES): ')
        if confirm == 'YES':
            db.query(User).delete()
            db.commit()
            print('Users deleted!')
        else:
            print('Cancelled')
    else:
        print('No users to delete')
finally:
    db.close()
