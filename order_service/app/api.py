from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.init_db import init_db
from app.models import Order
from app.publisher import RabbitMQPublisher
from app.schemas import CreateOrderRequest, OrderDetailsResponse, OrderResponse

app = FastAPI(title='Order Processing Service', version='1.0.0')
publisher = RabbitMQPublisher()


@app.on_event('startup')
def startup() -> None:
    init_db()


@app.get('/health')
def healthcheck() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/orders', response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(payload: CreateOrderRequest, db: Session = Depends(get_db)) -> OrderResponse:
    order = Order(
        customer_id=payload.customer_id,
        product=payload.product,
        quantity=payload.quantity,
        status='NEW',
    )
    try:
        db.add(order)
        db.flush()

        publisher.publish_order_created(
            {
                'order_id': order.id,
                'customer_id': order.customer_id,
                'product': order.product,
                'quantity': order.quantity,
            }
        )
        db.commit()
        db.refresh(order)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail='Failed to create order') from exc

    return OrderResponse(id=order.id, status=order.status)


@app.get('/orders/{order_id}', response_model=OrderDetailsResponse)
def get_order(order_id: int, db: Session = Depends(get_db)) -> OrderDetailsResponse:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail='Order not found')

    return OrderDetailsResponse(
        id=order.id,
        customer_id=order.customer_id,
        product=order.product,
        quantity=order.quantity,
        status=order.status,
        created_at=order.created_at,
    )
