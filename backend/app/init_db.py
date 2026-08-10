from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .models import Admin
from .config import settings
from .security import hash_password

def init_db():
    Base.metadata.create_all(engine)
    db: Session = SessionLocal()
    try:
        admin = db.query(Admin).filter(Admin.username == settings.ADMIN_USERNAME).first()
        if not admin:
            db.add(Admin(
                username=settings.ADMIN_USERNAME,
                password_hash=hash_password(settings.ADMIN_PASSWORD)
            ))
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
