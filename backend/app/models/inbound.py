from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from ..database import Base

class Inbound(Base):
    __tablename__ = "inbounds"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    protocol: Mapped[str] = mapped_column(String(32), default="vless")
    transport: Mapped[str] = mapped_column(String(32), default="xhttp")
    security: Mapped[str] = mapped_column(String(32), default="tls")
    listen_host: Mapped[str] = mapped_column(String(255), default="0.0.0.0")
    listen_port: Mapped[int] = mapped_column(Integer, default=443)
    path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    flow: Mapped[str | None] = mapped_column(String(64), nullable=True)
    settings_json: Mapped[str] = mapped_column(Text, default="{}")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
