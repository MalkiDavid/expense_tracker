from datetime import date as date_type
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.category import CategoryRead

class TransactionBase(BaseModel):
    date: date_type
    amount: Decimal
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    category_id: int

class TransactionRead(TransactionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category: CategoryRead

class TransactionUpdate(BaseModel):
    date: Optional[date_type] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    category_id: Optional[int] = None