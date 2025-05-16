from typing import Optional, List
from pydantic_settings import BaseSettings
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / '.env'


class Settings(BaseSettings):
    django_secret_key: str
    django_debug: bool
    django_allowed_hosts: Optional[List[str]] = []

    db_engine: str
    db_host: str
    db_user: str
    db_pass: str
    db_name: str
    db_port: str

    mail_username: str
    mail_from: str
    mail_password: str
    mail_port: int
    mail_server: str
    mail_start_tls: bool
    mail_ssl_tls: bool
    mail_use_credentials: bool
    mail_validate_certs: bool
    mail_backend: str

    class Config:
        env_file = CONFIG_FILE
        env_file_encoding = "utf-8"


settings = Settings()
DB_URI = (
    f"postgresql+psycopg2://{settings.db_user}:{settings.db_pass}@"
    f"{settings.db_host}:{settings.db_port}/{settings.db_name}"
)
