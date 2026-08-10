from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.admin import Admin
from ..security import require_admin, hash_password, verify_password

router = APIRouter(prefix="/api/admins", tags=["admins"])

@router.get("")
def list_admins(db: Session = Depends(get_db), _=Depends(require_admin)):
    return [
        {"id": a.id, "username": a.username, "enabled": a.enabled, "created_at": a.created_at}
        for a in db.query(Admin).all()
    ]

@router.post("")
def create_admin(data: dict, db: Session = Depends(get_db), _=Depends(require_admin)):
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    if not username or not password:
        raise HTTPException(422, "username/password required")
    if db.query(Admin).filter(Admin.username == username).first():
        raise HTTPException(409, "exists")
    a = Admin(username=username, password_hash=hash_password(password))
    db.add(a)
    db.commit()
    return {"id": a.id, "username": a.username}

@router.post("/change-password")
def change_password(data: dict, db: Session = Depends(get_db), current: Admin = Depends(require_admin)):
    old = str(data.get("old_password", ""))
    new = str(data.get("new_password", ""))
    if not verify_password(old, current.password_hash):
        raise HTTPException(401, "Current password is incorrect")
    if len(new) < 10:
        raise HTTPException(422, "New password must be at least 10 characters")
    current.password_hash = hash_password(new)
    db.commit()
    return {"changed": True}
