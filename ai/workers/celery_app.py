"""Omar, SCRUM-130. Celery on Redis. RabbitMQ is not used. The live worker is not a queue here."""

import json
import os
from datetime import datetime, timezone

from celery import Celery, bootsteps
from kombu import Exchange, Queue
from redis import Redis

from ai.workers.queues import CALLBACKS, MEDIA_CLIPS, QUEUES


celery_app = Celery("shawaf",broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),)

celery_app.conf.task_queues = [
    Queue(
        name=name,
        exchange=Exchange(name, type="direct"),
        routing_key=name,
    ) 
    for name in QUEUES
]
celery_app.conf.task_create_missing_queues = False

celery_app.conf.task_routes = {
    "media.cut_clip": {"queue": MEDIA_CLIPS},
    "callbacks.deliver": {"queue": CALLBACKS},
}


celery_app.conf.update(
    imports=("ai.workers.tasks.callbacks",),
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(name="ping")
def ping() -> str:
    return "pong"
class RedisHeartbeat(bootsteps.StartStopStep):
    requires = {"celery.worker.consumer.tasks:Tasks"}

    def __init__(self, consumer, **kwargs):
        self.timer_entry = None
        self.client = Redis.from_url(
            consumer.app.conf.broker_url,
            socket_connect_timeout=1,
            socket_timeout=1,
        )

    def start(self, consumer):
        self.client.ping()
        self.publish(consumer)
        self.timer_entry = consumer.timer.call_repeatedly(
            5.0,
            self.publish,
            (consumer,),
        )

    def publish(self, consumer):
        queues = sorted(queue.name for queue in consumer.task_consumer.queues)
        seen_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        payload = {
            "queues": queues,
            "seen_at": seen_at.replace("+00:00", "Z"),
        }
        self.client.set(f"worker:{consumer.hostname}", json.dumps(payload))

    def stop(self, consumer):
        if self.timer_entry is not None:
            self.timer_entry.cancel()
            self.timer_entry = None


celery_app.steps["consumer"].add(RedisHeartbeat)