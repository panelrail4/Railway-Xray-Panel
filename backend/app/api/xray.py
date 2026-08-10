import json, shutil, time
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db
from ..models.user import User
from ..models.inbound import Inbound
from ..security import require_admin
from ..config import settings
from ..xray.generator import build_config, write_atomic
from ..xray.validator import validate_config
from ..xray.manager import manager
from ..xray.nginx import write_nginx_config

router = APIRouter(prefix="/api/xray", tags=["xray"])

def rebuild(db):
    config = build_config(db.query(Inbound).all(), db.query(User).all())
    write_atomic(config, settings.XRAY_CONFIG)
    return config

@router.post("/rebuild")
def rebuild_xray(db=Depends(get_db), _=Depends(require_admin)):
    rebuild(db)
    write_nginx_config(db)
    test = validate_config()
    if not test["success"]:
        return {"valid": False, "xray": manager.status(), "error": test["output"]}
    return {"valid": True, "xray": manager.restart()}

@router.post("/start")
def start(_=Depends(require_admin)):
    return manager.start()

@router.post("/stop")
def stop(_=Depends(require_admin)):
    return manager.stop()

@router.post("/restart")
def restart(db=Depends(get_db), _=Depends(require_admin)):
    rebuild(db)
    write_nginx_config(db)
    return manager.restart()

@router.post("/validate")
def validate(_=Depends(require_admin)):
    return validate_config()

@router.get("/status")
def status(_=Depends(require_admin)):
    return manager.status()

@router.get("/log")
def log(_=Depends(require_admin)):
    p = Path(settings.XRAY_LOG)
    if not p.exists():
        return {"log": ""}
    text = p.read_text(errors="replace")
    return {"log": text[-12000:]}


@router.get("/reality")
def reality(_=Depends(require_admin)):
    from ..xray.reality import reality_parameters
    return reality_parameters()

@router.post("/backup")
def backup(_=Depends(require_admin)):
    src = Path(settings.XRAY_CONFIG)
    if not src.exists():
        raise HTTPException(status_code=404, detail="No Xray config")
    dst = src.parent / "backups"
    dst.mkdir(parents=True, exist_ok=True)
    target = dst / f"config-{int(time.time())}.json"
    shutil.copy2(src, target)
    return {"path": str(target)}
