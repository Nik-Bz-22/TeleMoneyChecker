from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field
from datetime import date

class TransactionBase(BaseModel):
    name: str
    amount_uah: Decimal
    date: date
    telegram_user_id: str



class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(TransactionBase):
    name: Optional[str] = None
    amount_uah: Optional[Decimal] = None
    date: Optional[date] = None
    transaction_id: int


class DateRange(BaseModel):
    start: Optional[date] = None
    end: Optional[date] = None


class TransactionRead(BaseModel):
    id: int
    name: str
    amount_uah: Decimal
    amount_usd: Decimal
    date: date
    telegram_user_id: str

    class Config:
        orm_mode = True