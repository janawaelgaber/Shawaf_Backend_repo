"""Omar, SCRUM-130. Celery on Redis. RabbitMQ is not used. The live worker is not a queue here."""

from celery import Celery
from kombu import Queue

from ai.workers.queues import QUEUES

celery_app = Celery("shawaf", broker="redis://localhost:6379/0")
celery_app.conf.task_queues = [Queue(name) for name in QUEUES]
