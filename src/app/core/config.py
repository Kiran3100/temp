from pydantic_settings import BaseSettings
from pydantic import Field, AnyUrl


class Settings(BaseSettings):
    APP_NAME: str = "Hostel SaaS"
    DEBUG: bool = False
    # DB
    DATABASE_URL: str = "postgresql+psycopg://postgres:Kiran$123@localhost:5432/hostel_saas"
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    # 3rd party
    SENDGRID_API_KEY: str = ""
    FCM_SERVER_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    SLACK_WEBHOOK_URL: str = ""
    # Security
    SUPER_ADMIN_EMAIL: str = "superadmin@example.com"
    SUPER_ADMIN_PASSWORD: str = "changeme"

    class Config:
        env_file = ".env"

settings = Settings()
