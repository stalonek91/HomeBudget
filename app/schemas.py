from pydantic import BaseModel
from datetime import date
from typing import Optional


#Schema for transaction table operation
class TransactionSchema(BaseModel):
    
    id: Optional[int] = None
    date: date
    receiver: str
    title: str
    amount: float
    transaction_type: str
    category: str

    class Config:
        orm_mode = True


class UpdateTransactionSchema(BaseModel):
    
    id: Optional[int] = None
    transaction_date: Optional[date] = None
    receiver: Optional[str] = None
    title: Optional[str] = None
    amount: Optional[float] = None
    transaction_type: Optional[str] = None
    category: Optional[str] = None

    class Config:
        orm_mode = True

class ReturnedTransaction(BaseModel):
    id: int
    receiver: str
    title: str
    amount: float
    category: str

    class Config:
        orm_mode = True