from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./llm.db"
    authjwt_secret_key: str = "your-secret-key-change-me"
    authjwt_token_location: set = {"headers"}
    authjwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive: bool = True


settings = Settings()