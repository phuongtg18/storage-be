from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

def utc_now():
    return datetime.now(timezone.utc)

class Admin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=80)
    password_hash: str
    created_at: datetime = Field(default_factory=utc_now)

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=120)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=200)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", index=True)
    unit: str = Field(default="pcs", max_length=40)
    quantity: float = Field(default=0, ge=0)
    alert_threshold: float = Field(default=0, ge=0)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

class StockTransaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id", index=True)
    type: str = Field(index=True, max_length=20)  # IN / OUT / ADJUSTMENT
    quantity: float
    quantity_before: float
    quantity_after: float
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now, index=True)
