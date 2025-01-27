import asyncio

from celery import Celery

from core.config import settings
from services.mailer import send_reset_pwd

celery = Celery(__name__)
if settings.CELERY_BROKER_URL:
    celery.conf.broker_url = settings.CELERY_BROKER_URL
    celery.conf.broker_connection_retry_on_startup = True
    loop = asyncio.get_event_loop()
else:
    celery.conf.task_always_eager = True


def perform_async_task(coro):
    if celery.conf.task_always_eager:
        asyncio.gather(coro)
    else:
        task = loop.create_task(coro)
        loop.run_until_complete(task)


@celery.task(name="send_reset_pwd_task", ignore_result=True)
def send_reset_pwd_task(email: str):
    """Задача отправки ссылки для сброса пароля"""
    send_reset_pwd(email)
