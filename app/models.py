from .database import base

from sqlalchemy.sql.expression import text
from sqlalchemy import Column, Integer, Text, String, Boolean, DateTime, Date, Numeric


class Transaction(base):

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    receiver = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_type = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)

    