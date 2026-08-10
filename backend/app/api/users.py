import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse
from ..security import require_admin
from ..xray.runtime import rebuild_and_restart

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(User).order_by(User.id.desc()).all()

@router.post("", response_model=UserResponse)
def create_user(data: UserCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    username = data.username.strip()
    if not username:
        raise HTTPException(422, "Username required")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    u = User(username=username, uuid=str(uuid.uuid4()), traffic_limit=data.traffic_limit, expire_at=data.expire_at)
    db.add(u)
    db.commit()
    db.refresh(u)
    try:
        result = rebuild_and_restart(db)
        if result.get("status") == "error":
            db.delete(u)
            db.commit()
            rebuild_and_restart(db)
            raise HTTPException(status_code=422, detail=result.get("error"))
    except HTTPException:
        raise
    except Exception as e:
        db.delete(u)
        db.commit()
        rebuild_and_restart(db)
        raise HTTPException(500, str(e))
    return u

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    db.delete(u)
    db.commit()
    result = rebuild_and_restart(db)
    return {"deleted": True, "xray": result}
