"""
Script to make a user an admin
Usage: python make_admin.py <email>
"""
import sys
from sqlmodel import Session, select, create_engine
from main import User, DATABASE_URL

def make_admin(email: str):
    engine = create_engine(DATABASE_URL, echo=False)
    
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        
        if not user:
            print(f"❌ User with email '{email}' not found")
            return False
        
        if user.is_admin:
            print(f"✓ User '{email}' is already an admin")
            return True
        
        user.is_admin = True
        session.commit()
        print(f"✓ User '{email}' is now an admin!")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    success = make_admin(email)
    sys.exit(0 if success else 1)
