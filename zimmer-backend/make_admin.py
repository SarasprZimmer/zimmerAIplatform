import sqlite3
from utils.security import hash_password

def make_user_admin(user_id: int = 1):
    """Make a user an admin by setting is_admin = True"""
    conn = sqlite3.connect('zimmer_dashboard.db')
    cur = conn.cursor()
    
    # Check if user exists
    cur.execute("SELECT id, name, email, is_admin FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    
    if not user:
        print(f"User with ID {user_id} not found!")
        return False
    
    print(f"Current user: {user}")
    
    # Update user to admin
    cur.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user_id,))
    conn.commit()
    
    # Verify the change
    cur.execute("SELECT id, name, email, is_admin FROM users WHERE id = ?", (user_id,))
    updated_user = cur.fetchone()
    print(f"Updated user: {updated_user}")
    
    conn.close()
    return True

def create_admin_user(name: str, email: str, password: str):
    """Create a new admin user"""
    conn = sqlite3.connect('zimmer_dashboard.db')
    cur = conn.cursor()
    
    # Check if user already exists
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cur.fetchone():
        print(f"User with email {email} already exists!")
        return False
    
    # Hash password
    hashed_password = hash_password(password)
    
    # Insert new admin user
    cur.execute(
        "INSERT INTO users (name, email, password_hash, is_admin) VALUES (?, ?, ?, ?)",
        (name, email, hashed_password, True)
    )
    conn.commit()
    
    # Get the new user
    user_id = cur.lastrowid
    cur.execute("SELECT id, name, email, is_admin FROM users WHERE id = ?", (user_id,))
    new_user = cur.fetchone()
    print(f"Created admin user: {new_user}")
    
    conn.close()
    return True

if __name__ == "__main__":
    print("Making user ID 1 an admin...")
    make_user_admin(1)
    
    print("\nTo create a new admin user, uncomment and modify the line below:")
    # create_admin_user("Admin Name", "admin@example.com", "secure_password")