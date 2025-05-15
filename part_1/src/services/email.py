from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.configuration.config import settings


email_conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Viktor Ch.",
    MAIL_STARTTLS=settings.mail_start_tls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=settings.mail_use_credentials,
    VALIDATE_CERTS=settings.mail_validate_certs,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates'
)


async def send_verificatoin_email(
    email: EmailStr,
    username: str,
    host: str
):
    try:
        # токен для верифікації email
        token_verification = await auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Congirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification
            },
            subtype=MessageType.html
        )
        fm = FastMail(email_conf)
        await fm.send_message(
            message,
            template_name="email_verification_template.html"
        )
    except ConnectionError as err:
        print(err)


async def send_reset_password_email(
    email: EmailStr,
    username: str,
    host: str
):
    try:
        # токен для скиадння паролю
        passwortd_reset_token = await auth_service.create_password_reset_token({"sub": email})
        message = MessageSchema(
            subject="Password reset",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": passwortd_reset_token
            },
            subtype=MessageType.html
        )
        fm = FastMail(email_conf)
        await fm.send_message(
            message,
            template_name="email_password_reset_template.html"
        )
    except ConnectionError as err:
        print(err)
