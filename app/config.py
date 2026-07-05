from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    MAX_PHOTO_SIZE_KB: int = 200

    model_config = ConfigDict(env_file=".env")

settings = Settings()