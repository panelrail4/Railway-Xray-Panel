from pydantic import BaseModel, Field
from typing import Any

class InboundCreate(BaseModel):
    name: str
    protocol: str = 'vless'
    transport: str = 'xhttp'
    security: str = 'tls'
    listen_port: int = Field(default=10000, ge=1, le=65535)
    path: str | None = '/xray'
    flow: str | None = None
    settings: dict[str, Any] = Field(default_factory=dict)

class InboundResponse(InboundCreate):
    id: int
    enabled: bool
    listen_host: str = '127.0.0.1'
