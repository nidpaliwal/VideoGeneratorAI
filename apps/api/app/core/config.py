from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql://videogen:videogen_dev@localhost:5432/videogen"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 30
    JWT_REFRESH_EXPIRY_DAYS: int = 7

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    ELEVENLABS_API_KEY: str = ""
    GOOGLE_CLOUD_TTS_CREDENTIALS: str = ""

    PEXELS_API_KEY: str = ""
    PIXABAY_API_KEY: str = ""

    RUNWAY_API_KEY: str = ""
    LUMA_API_KEY: str = ""

    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_ASSETS: str = "videogen-assets"
    S3_BUCKET_VIDEOS: str = "videogen-videos"
    S3_ENDPOINT_URL: str = "http://localhost:9000"

    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_FREE: str = ""
    STRIPE_PRICE_PRO: str = ""
    STRIPE_PRICE_CREATOR: str = ""

    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""

    FFMPEG_PATH: str = "ffmpeg"
    FFPROBE_PATH: str = "ffprobe"

    RENDER_WORKER_CONCURRENCY: int = 2
    RENDER_TIMEOUT_SECONDS: int = 300

    FREE_TIER_MONTHLY_CREDITS: int = 3
    PRO_TIER_MONTHLY_CREDITS: int = 50
    CREATOR_TIER_MONTHLY_CREDITS: int = 200

    MAX_VIDEO_LENGTH_FREE: int = 60
    MAX_VIDEO_LENGTH_PAID: int = 90


settings = Settings()