from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    MAX_PHOTO_SIZE_KB: int = 200

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore
