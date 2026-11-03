from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.database import get_session
from app.models import Item, StockTransaction
from app.schemas import StockRequest, StockAdjustRequest, StockTransactionRead, ItemRead
from app.security import get_current_admin
from app.services.inventory import change_stock, item_status

router = APIRouter(prefix="/stock", tags=["Stock"], dependencies=[Depends(get_current_admin)])

@router.post("/in", response_model=ItemRead)
def stock_in(data: StockRequest, session: Session = Depends(get_session)):
    item = session.get(Item, data.item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    item = change_stock(session, item, data.quantity, "IN", data.note)
    return ItemRead(id=item.id, name=item.name, category_id=item.category_id, unit=item.unit,
        quantity=item.quantity, alert_threshold=item.alert_threshold, status=item_status(item),
        notes=item.notes, created_at=item.created_at, updated_at=item.updated_at)

@router.post("/out", response_model=ItemRead)
def stock_out(data: StockRequest, session: Session = Depends(get_session)):
    item = session.get(Item, data.item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    item = change_stock(session, item, -data.quantity, "OUT", data.note)
    return ItemRead(id=item.id, name=item.name, category_id=item.category_id, unit=item.unit,
        quantity=item.quantity, alert_threshold=item.alert_threshold, status=item_status(item),
        notes=item.notes, created_at=item.created_at, updated_at=item.updated_at)

@router.post("/adjust", response_model=ItemRead)
def stock_adjust(data: StockAdjustRequest, session: Session = Depends(get_session)):
    item = session.get(Item, data.item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    delta = data.new_quantity - item.quantity
    item = change_stock(session, item, delta, "ADJUSTMENT", data.note or "Manual stock adjustment")
    return ItemRead(id=item.id, name=item.name, category_id=item.category_id, unit=item.unit,
        quantity=item.quantity, alert_threshold=item.alert_threshold, status=item_status(item),
        notes=item.notes, created_at=item.created_at, updated_at=item.updated_at)

@router.get("/history", response_model=list[StockTransactionRead])
def stock_history(
    item_id: int | None = None,
    type: str | None = Query(default=None, pattern="^(IN|OUT|ADJUSTMENT)$"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    statement = select(StockTransaction)
    if item_id is not None:
        statement = statement.where(StockTransaction.item_id == item_id)
    if type:
        statement = statement.where(StockTransaction.type == type)
    return session.exec(statement.order_by(StockTransaction.created_at.desc())
                        .offset(offset).limit(limit)).all()
