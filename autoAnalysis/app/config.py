# app/config.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Groq settings
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama3-8b-8192"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # File storage
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"

    class Config:
        env_file = ".env"

settings = Settings()
