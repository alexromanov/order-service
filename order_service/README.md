# Order Processing Service

A small Python service for practicing integration testing with real dependencies.

## What it does

- exposes an HTTP API for creating and reading orders
- stores orders in PostgreSQL
- publishes `order created` messages to RabbitMQ
- runs a background worker that consumes messages and marks orders as `PROCESSED`
- writes processing events into `order_events`

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- RabbitMQ
- pika

## API

### Create order

`POST /orders`

Request:

```json
{
  "customer_id": "cust-123",
  "product": "keyboard",
  "quantity": 2
}
```

Response:

```json
{
  "id": 1,
  "status": "NEW"
}
```

### Get order

`GET /orders/{id}`

Response:

```json
{
  "id": 1,
  "customer_id": "cust-123",
  "product": "keyboard",
  "quantity": 2,
  "status": "PROCESSED",
  "created_at": "2026-03-26T10:00:00"
}
```

## Run locally with Docker Compose

```bash
docker compose up --build
```

Services:
- API: `http://localhost:8000`
- RabbitMQ UI: `http://localhost:15672`
- PostgreSQL: `localhost:5432`

## Run without Docker for the app code

Start PostgreSQL and RabbitMQ first, then:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/orders_db'
export RABBITMQ_HOST='localhost'
export RABBITMQ_PORT='5672'
export RABBITMQ_USER='guest'
export RABBITMQ_PASSWORD='guest'

uvicorn app.api:app --reload
python -m app.worker
```