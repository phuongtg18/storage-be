from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from app.database import get_session
from app.models import Item, Category, StockTransaction
from app.schemas import ItemCreate, ItemUpdate, ItemRead
from app.security import get_current_admin
from app.services.inventory import item_status

router = APIRouter(prefix="/items", tags=["Items"], dependencies=[Depends(get_current_admin)])

def serialize_item(item: Item, category: Category | None):
    return ItemRead(
        id=item.id, name=item.name, category_id=item.category_id,
        category_name=category.name if category else None,
        unit=item.unit, quantity=item.quantity, alert_threshold=item.alert_threshold,
        status=item_status(item), notes=item.notes,
        created_at=item.created_at, updated_at=item.updated_at,
    )

@router.get("", response_model=list[ItemRead])
def list_items(
    search: str | None = None,
    category_id: int | None = None,
    status: str | None = Query(default=None, pattern="^(IN_STOCK|RUNNING_LOW|CRITICAL_OUT)$"),
    sort_by: str = Query(default="name", pattern="^(name|quantity|created_at|updated_at)$"),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    statement = select(Item)
    if search:
        statement = statement.where(Item.name.contains(search))
    if category_id is not None:
        statement = statement.where(Item.category_id == category_id)
    if status == "CRITICAL_OUT":
        statement = statement.where(Item.quantity <= 0)
    elif status == "RUNNING_LOW":
        statement = statement.where(and_(Item.quantity > 0, Item.quantity <= Item.alert_threshold))
    elif status == "IN_STOCK":
        statement = statement.where(Item.quantity > Item.alert_threshold)
    column = getattr(Item, sort_by)
    statement = statement.order_by(column.desc() if order == "desc" else column.asc())
    items = session.exec(statement.offset(offset).limit(limit)).all()
    result = []
    for item in items:
        category = session.get(Category, item.category_id) if item.category_id else None
        result.append(serialize_item(item, category))
    return result

@router.post("", response_model=ItemRead, status_code=201)
def create_item(data: ItemCreate, session: Session = Depends(get_session)):
    if data.category_id is not None and not session.get(Category, data.category_id):
        raise HTTPException(404, "Category not found")
    obj = Item(**data.model_dump())
    session.add(obj)
    session.commit()
    session.refresh(obj)
    category = session.get(Category, obj.category_id) if obj.category_id else None
    return serialize_item(obj, category)

@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, session: Session = Depends(get_session)):
    obj = session.get(Item, item_id)
    if not obj:
        raise HTTPException(404, "Item not found")
    category = session.get(Category, obj.category_id) if obj.category_id else None
    return serialize_item(obj, category)

@router.put("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, data: ItemUpdate, session: Session = Depends(get_session)):
    obj = session.get(Item, item_id)
    if not obj:
        raise HTTPException(404, "Item not found")
    changes = data.model_dump(exclude_unset=True)
    if "category_id" in changes and changes["category_id"] is not None:
        if not session.get(Category, changes["category_id"]):
            raise HTTPException(404, "Category not found")
    for key, value in changes.items():
        setattr(obj, key, value)
    from datetime import datetime, timezone
    obj.updated_at = datetime.now(timezone.utc)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    category = session.get(Category, obj.category_id) if obj.category_id else None
    return serialize_item(obj, category)

@router.delete("/{item_id}")
def delete_item(item_id: int, session: Session = Depends(get_session)):
    obj = session.get(Item, item_id)
    if not obj:
        raise HTTPException(404, "Item not found")
    if session.exec(select(StockTransaction).where(StockTransaction.item_id == item_id)).first():
        raise HTTPException(409, "Item has stock history and cannot be deleted")
    session.delete(obj)
    session.commit()
    return {"message": "Item deleted"}
