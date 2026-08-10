from sqlalchemy.orm import Session
from ..models import Inbound, User
from ..config import settings
from .generator import build_config, write_atomic
from .manager import manager

def rebuild_and_restart(db: Session):
    config = build_config(db.query(Inbound).all(), db.query(User).all())
    write_atomic(config, settings.XRAY_CONFIG)
    return manager.restart()
