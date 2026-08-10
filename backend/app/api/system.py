import os
from fastapi import APIRouter, Depends
from ..security import require_admin
from ..xray.manager import manager
router=APIRouter(prefix="/api/system",tags=["system"])
@router.get("/capabilities")
def capabilities(_=Depends(require_admin)):
    tcp_domain=os.getenv("RAILWAY_TCP_PROXY_DOMAIN"); tcp_port=os.getenv("RAILWAY_TCP_PROXY_PORT")
    return {
      "environment":"railway" if os.getenv("RAILWAY_ENVIRONMENT_NAME") else "generic",
      "public_domain":os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("PUBLIC_HOST"),
      "private_domain":os.getenv("RAILWAY_PRIVATE_DOMAIN"),
      "tcp_proxy":bool(tcp_domain and tcp_port),
      "tcp_proxy_domain":tcp_domain,
      "tcp_proxy_port":int(tcp_port) if tcp_port and tcp_port.isdigit() else None,
      "tcp_application_port":os.getenv("RAILWAY_TCP_APPLICATION_PORT"),
      "edge_tls":os.getenv("RAILWAY_EDGE_TLS","true").lower() in ("1","true","yes","on"),
      "volume_mount_path":os.getenv("RAILWAY_VOLUME_MOUNT_PATH"),
      "replica_id":os.getenv("RAILWAY_REPLICA_ID"),
      "capabilities":{"raw":True,"xhttp":True,"websocket":True,"grpc":True,"tls":True,"reality":True},
      "xray_available":manager.available()
    }
