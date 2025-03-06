from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app.config import Config
from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent
# TEMPLATE_FOLDER = BASE_DIR.parent / "templates"

mail_config = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_FROM_NAME="Customer Services",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    #TEMPLATE_FOLDER= str(TEMPLATE_FOLDER)
)

mail = FastMail(config=mail_config)

def create_message(recipients: list[str], subject: str, body: str):

    message = MessageSchema(
        recipients=recipients, subject=subject, body=body, subtype=MessageType.html
    )

    return message