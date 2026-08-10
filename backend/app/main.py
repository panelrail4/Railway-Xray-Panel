from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .api import auth, users, inbounds, system, health, subscriptions, stats, xray, admin, qr
from .init_db import init_db
from .database import SessionLocal
from .models import User, Inbound
from .config import settings
from .xray.generator import build_config, write_atomic
from .xray.manager import manager
from .xray.nginx import write_nginx_config
from .railway_domain import ensure_public_domain

app = FastAPI(title="Railway XPanel", version="1.0.10")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(inbounds.router)
app.include_router(system.router)
app.include_router(health.router)
app.include_router(subscriptions.router)
app.include_router(stats.router)
app.include_router(xray.router)
app.include_router(admin.router)
app.include_router(qr.router)

@app.on_event("startup")
def startup():
    ensure_public_domain()
    init_db()
    db = SessionLocal()
    try:
        write_atomic(
            build_config(db.query(Inbound).all(), db.query(User).all()),
            settings.XRAY_CONFIG
        )
        if settings.XRAY_START_ON_BOOT:
            manager.start()
        write_nginx_config(db)
    finally:
        db.close()

@app.on_event("shutdown")
def shutdown():
    manager.stop()

static = Path(__file__).parent / "static"
if static.exists():
    app.mount("/assets", StaticFiles(directory=static / "assets"), name="assets")
    @app.get("/{path:path}")
    def frontend(path: str):
        return FileResponse(static / "index.html")
