from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_host: str = os.getenv('APP_HOST', '0.0.0.0')
    app_port: int = int(os.getenv('APP_PORT', '8000'))
    database_url: str = os.getenv(
        'DATABASE_URL',
        'postgresql+psycopg://postgres:postgres@localhost:5432/orders_db',
    )
    rabbitmq_host: str = os.getenv('RABBITMQ_HOST', 'localhost')
    rabbitmq_port: int = int(os.getenv('RABBITMQ_PORT', '5672'))
    rabbitmq_user: str = os.getenv('RABBITMQ_USER', 'guest')
    rabbitmq_password: str = os.getenv('RABBITMQ_PASSWORD', 'guest')
    rabbitmq_queue: str = os.getenv('RABBITMQ_QUEUE', 'orders.created')
    worker_poll_interval_seconds: float = float(os.getenv('WORKER_POLL_INTERVAL_SECONDS', '2'))


settings = Settings()
