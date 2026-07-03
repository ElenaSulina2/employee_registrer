from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    MAX_PHOTO_SIZE_KB: int = 200

    class Config:
        env_file = ".env"

settings = Settings()