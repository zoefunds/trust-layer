from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "TrustLayer API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Email (Brevo)
    BREVO_API_KEY: str
    BREVO_SENDER_EMAIL: str = "preciousmofeoluwa@gmail.com"
    BREVO_SENDER_NAME: str = "TrustLayer"

    # Wallet encryption
    WALLET_ENCRYPTION_KEY: str  # 32-byte hex key for AES-256

    # GenLayer
    GENLAYER_STUDIO_URL: str = "https://studio.genlayer.com"
    GENLAYER_CONTRACT_ADDRESS: Optional[str] = None
    # StudioNet sandbox account used to sign transactions (Hardhat default test key — safe for testnet-only use)
    GENLAYER_PRIVATE_KEY: str = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

    # Sentry
    SENTRY_DSN: Optional[str] = None

    # CORS
    FRONTEND_URL: str = "https://trust-layer.vercel.app"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
