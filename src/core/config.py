from os import getenv
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    db_url: str = "sqlite+aiosqlite://" + getenv("DATABASE_URL")
    db_echo: bool = getenv("DATABASE_ECHO")


settings = Settings()
