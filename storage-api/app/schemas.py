from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AdminResponse(BaseModel):
    id: int
    username: str

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = None

class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category_id: Optional[int] = None
    unit: str = Field(default="pcs", min_length=1, max_length=40)
    quantity: float = Field(default=0, ge=0)
    alert_threshold: float = Field(default=0, ge=0)
    notes: Optional[str] = None

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    category_id: Optional[int] = None
    unit: Optional[str] = Field(default=None, min_length=1, max_length=40)
    alert_threshold: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = None

class ItemRead(BaseModel):
    id: int
    name: str
    category_id: Optional[int]
    category_name: Optional[str] = None
    unit: str
    quantity: float
    alert_threshold: float
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

class StockRequest(BaseModel):
    item_id: int
    quantity: float = Field(gt=0)
    note: Optional[str] = None

class StockAdjustRequest(BaseModel):
    item_id: int
    new_quantity: float = Field(ge=0)
    note: Optional[str] = None

class StockTransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    item_id: int
    type: str
    quantity: float
    quantity_before: float
    quantity_after: float
    note: Optional[str]
    created_at: datetime

class DashboardRead(BaseModel):
    total_items: int
    in_stock: int
    running_low: int
    critical_out: int
    total_quantity: float
