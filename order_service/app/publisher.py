from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Generator

import pika
from pika.adapters.blocking_connection import BlockingChannel

from app.settings import settings


class RabbitMQPublisher:
    def __init__(self) -> None:
        credentials = pika.PlainCredentials(settings.rabbitmq_user, settings.rabbitmq_password)
        parameters = pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            credentials=credentials,
            heartbeat=30,
        )
        self._parameters = parameters

    @contextmanager
    def channel(self) -> Generator[BlockingChannel, None, None]:
        connection = pika.BlockingConnection(self._parameters)
        try:
            channel = connection.channel()
            channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
            yield channel
        finally:
            connection.close()

    def publish_order_created(self, payload: dict) -> None:
        body = json.dumps(payload).encode('utf-8')
        with self.channel() as channel:
            channel.basic_publish(
                exchange='',
                routing_key=settings.rabbitmq_queue,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json',
                ),
            )
