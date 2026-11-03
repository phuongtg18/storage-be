from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from app.database import get_session
from app.models import Category, Item
from app.schemas import CategoryCreate, CategoryUpdate, CategoryRead
from app.security import get_current_admin

router = APIRouter(prefix="/categories", tags=["Categories"], dependencies=[Depends(get_current_admin)])

@router.get("", response_model=list[CategoryRead])
def list_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category).order_by(Category.name)).all()

@router.post("", response_model=CategoryRead, status_code=201)
def create_category(data: CategoryCreate, session: Session = Depends(get_session)):
    obj = Category(**data.model_dump())
    session.add(obj)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Category name already exists")
    session.refresh(obj)
    return obj

@router.put("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, data: CategoryUpdate, session: Session = Depends(get_session)):
    obj = session.get(Category, category_id)
    if not obj:
        raise HTTPException(404, "Category not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    session.add(obj)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Category name already exists")
    session.refresh(obj)
    return obj

@router.delete("/{category_id}")
def delete_category(category_id: int, session: Session = Depends(get_session)):
    obj = session.get(Category, category_id)
    if not obj:
        raise HTTPException(404, "Category not found")
    if session.exec(select(Item).where(Item.category_id == category_id)).first():
        raise HTTPException(409, "Category is assigned to items")
    session.delete(obj)
    session.commit()
    return {"message": "Category deleted"}
