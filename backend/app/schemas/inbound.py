from pydantic import BaseModel, Field

class InboundCreate(BaseModel):
    name: str
    protocol: str = 'vless'
    transport: str = 'xhttp'
    security: str = 'tls'
    listen_port: int = Field(default=10000, ge=1, le=65535)
    path: str | None = '/xhttp'
    flow: str | None = None
    settings: dict = {}

class InboundResponse(InboundCreate):
    id: int
    enabled: bool
