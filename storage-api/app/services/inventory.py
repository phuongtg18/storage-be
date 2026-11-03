from datetime import datetime, timezone
from fastapi import HTTPException
from sqlmodel import Session
from app.models import Item, StockTransaction

def item_status(item: Item) -> str:
    if item.quantity <= 0:
        return "CRITICAL_OUT"
    if item.quantity <= item.alert_threshold:
        return "RUNNING_LOW"
    return "IN_STOCK"

def change_stock(session: Session, item: Item, change: float, kind: str, note: str | None):
    before = item.quantity
    after = before + change
    if after < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    item.quantity = after
    item.updated_at = datetime.now(timezone.utc)
    session.add(item)
    session.add(StockTransaction(
        item_id=item.id,
        type=kind,
        quantity=abs(change),
        quantity_before=before,
        quantity_after=after,
        note=note,
    ))
    session.commit()
    session.refresh(item)
    return item
