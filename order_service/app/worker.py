from __future__ import annotations

import json
import logging
import time

import pika
from pika.exceptions import AMQPConnectionError
from sqlalchemy import select

from app.db import session_scope
from app.init_db import init_db
from app.models import Order, OrderEvent
from app.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
)
logger = logging.getLogger('order-worker')


def process_message(body: bytes) -> None:
    payload = json.loads(body.decode('utf-8'))
    order_id = payload['order_id']

    with session_scope() as session:
        order = session.get(Order, order_id)
        if order is None:
            logger.warning('Order %s does not exist; skipping message', order_id)
            return

        duplicate_event = session.scalar(
            select(OrderEvent).where(
                OrderEvent.order_id == order_id,
                OrderEvent.event_type == 'ORDER_PROCESSED',
            )
        )
        if duplicate_event is not None:
            logger.info('Order %s already processed; ignoring duplicate message', order_id)
            return

        order.status = 'PROCESSED'
        session.add(
            OrderEvent(
                order_id=order_id,
                event_type='ORDER_PROCESSED',
                payload=payload,
            )
        )
        logger.info('Order %s processed successfully', order_id)


def run_worker() -> None:
    init_db()

    credentials = pika.PlainCredentials(settings.rabbitmq_user, settings.rabbitmq_password)
    parameters = pika.ConnectionParameters(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        credentials=credentials,
        heartbeat=30,
    )

    while True:
        try:
            logger.info('Connecting to RabbitMQ at %s:%s', settings.rabbitmq_host, settings.rabbitmq_port)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
            channel.basic_qos(prefetch_count=1)

            def callback(ch: pika.adapters.blocking_connection.BlockingChannel, method, properties, body: bytes) -> None:
                try:
                    process_message(body)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception:
                    logger.exception('Failed to process message')
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_consume(queue=settings.rabbitmq_queue, on_message_callback=callback)
            logger.info('Worker started, waiting for messages')
            channel.start_consuming()
        except AMQPConnectionError:
            logger.exception('RabbitMQ unavailable; retrying soon')
            time.sleep(settings.worker_poll_interval_seconds)
        except KeyboardInterrupt:
            logger.info('Worker stopped by user')
            break
        except Exception:
            logger.exception('Unexpected worker error; retrying soon')
            time.sleep(settings.worker_poll_interval_seconds)


if __name__ == '__main__':
    run_worker()
