from app.mail import create_message, mail
from celery import Celery
from asgiref.sync import async_to_sync

c_app = Celery()
c_app.config_from_object("app.config")


@c_app.task()
def send_email(recipients: list[str], subject: str, body: str):

    messages = create_message(recipients, subject, body)

    async_to_sync(mail.send_message)(messages)
    print("Email sent")
