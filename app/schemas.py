from pydantic import BaseModel
from datetime import date
from typing import Optional

class UpdatePortfolioTransaction(BaseModel):

    id: Optional[int] = None
    date: Optional[date]
    initial_amount: Optional[float]
    deposit_amount: Optional[float]
    total_amount: Optional[float]
    growth_percentage: Optional[float] = None

class PortfolioTransaction(BaseModel):

    id: Optional[int] = None
    date: date
    initial_amount: float
    deposit_amount: float
    total_amount: float
    growth_percentage: Optional[float] = None

    class Config:
        orm_mode = True




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
    ref_number: Optional[str] = None

    class Config:
        orm_mode = True

class ReturnedTransaction(BaseModel):
    id: int
    receiver: str
    title: str
    amount: float
    category: str
    ref_number: str

    class Config:
        orm_mode = True


class ReturnSummary(BaseModel):
        income: float
        expenses: float

class ReturnDate(BaseModel):
    date: date

class PortfolioSummarySchema(BaseModel):
    id: Optional[int] = None
    Date: date
    Total_Value: float
    Deposits: float


    class Config:
        orm_mode = True


