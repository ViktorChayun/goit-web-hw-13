from pydantic_settings import BaseSettings
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / 'config.env'


class Settings(BaseSettings):
    secret_key: str
    algorithm: str
    db_url: str
    mail_username: str
    mail_from: str
    mail_password: str
    mail_port: int
    mail_server: str
    mail_start_tls: bool
    mail_ssl_tls: bool
    mail_use_credentials: bool
    mail_validate_certs: bool
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_cache_timeout: int = 900
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        env_file = CONFIG_FILE
        env_file_encoding = "utf-8"


settings = Settings()
