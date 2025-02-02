import smtplib
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import lru_cache

from loguru import logger

from core.config import settings
from services.helpers.security import create_token
from utils import singleton


def send_reset_pwd(email: str):
    """
    Отправляет письмо об изменении пароля.

    :param email: Email пользователя.
    """
    token = create_token(
        data=dict(email=email),
        delta=timedelta(minutes=settings.FORGET_PASSWORD_LINK_EXPIRE_MINUTES),
    )
    email_context = {
        "link_expire_minutes": settings.FORGET_PASSWORD_LINK_EXPIRE_MINUTES,
        "reset_link": f"http://localhost/reset-password/{token}",
    }
    subject = "Сброс пароля на сайте localhost"

    body = """
            <h3>Сброс пароля для сайта localhost</h3>
            <p>{reset_link}</p>
            <p>Ссылка будет доступна в течение {link_expire_minutes} минут.</p>
            """.format(**email_context)
    email_service.send_email(email, subject, body)


@singleton
class EmailService:
    """Сервис для отправки почты."""

    def __init__(self):
        self._from = settings.EMAIL_FROM
        self._password = settings.EMAIL_PASSWORD
        self._smtp_server = settings.SMTP_SERVER
        self._smtp_port = 465

    def _create_message(self, email: str, subject, body) -> str:
        message = MIMEMultipart()
        message["From"] = self._from
        message["To"] = email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))
        return message.as_string()

    def send_email(self, email: str, subject: str, body: str) -> None:
        """Отправка письма для сброса пароля."""
        try:
            server = smtplib.SMTP_SSL(self._smtp_server, self._smtp_port, timeout=10)
            try:
                server.login(self._from, self._password)
                message = self._create_message(
                    email,
                    subject,
                    body,
                )
                server.sendmail(from_addr=self._from, to_addrs=[email], msg=message)
            finally:
                server.quit()
        except Exception as e:
            logger.info(f"{e}")


@lru_cache
def get_email_service() -> EmailService:
    """Получение сервиса для отправки почты."""
    return EmailService()


email_service = get_email_service()
