from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = "CHANGE-ME"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "change-me"
    DATABASE_URL: str = "sqlite:////data/panel.db"
    XRAY_PATH: str = "/usr/local/bin/xray"
    XRAY_CONFIG: str = "/data/xray/config.json"
    XRAY_LOG: str = "/data/xray/xray.log"
    XRAY_START_ON_BOOT: bool = True
    XRAY_DEFAULT_LISTEN_PORT: int = 443
    PUBLIC_HOST: str = ""
    PUBLIC_PORT: int = 0
    TLS_CERT_FILE: str = ""
    TLS_KEY_FILE: str = ""
    REALITY_PRIVATE_KEY: str = ""
    REALITY_PUBLIC_KEY: str = ""
    REALITY_SERVER_NAME: str = ""
    REALITY_SHORT_ID: str = ""
    RAILWAY_EDGE_TLS: bool = True
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
