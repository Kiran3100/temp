from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    APP_NAME: str = "Hostel SaaS"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+asyncpg://postgres:Kiran$123@localhost:5432/hostel_saas"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REDIS_URL: str = "redis://localhost:6379/0"
    SENDGRID_API_KEY: str = ""
    FCM_SERVER_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    SLACK_WEBHOOK_URL: str = ""
    SUPER_ADMIN_EMAIL: str = "superadmin@example.com"
    SUPER_ADMIN_PASSWORD: str = "changeme"

settings = Settings()