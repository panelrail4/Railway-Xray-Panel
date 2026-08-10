from fastapi import APIRouter
from ..database import engine
from ..xray.manager import manager

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
def health():
    try:
        with engine.connect() as c:
            c.exec_driver_sql("SELECT 1")
        db = "ok"
    except Exception:
        db = "error"
    return {"status": "ok" if db == "ok" else "degraded", "database": db, "xray": manager.status()["status"]}
