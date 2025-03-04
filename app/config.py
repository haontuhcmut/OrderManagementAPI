from passlib.crypto.scrypt import backend
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir/".env"

print(env_path)

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    DOMAIN: str
    REDIS_URL: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str

    model_config = SettingsConfigDict(env_file=env_path, extra="ignore")


Config = Settings()


#Celery config
broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
broker_connection_retry_on_startup=True

    