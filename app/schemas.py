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