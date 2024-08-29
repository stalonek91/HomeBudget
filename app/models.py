from app.database import Base

from sqlalchemy.sql.expression import text
from sqlalchemy import Column, Integer, Text, String, Boolean, DateTime, Date, Numeric, Computed


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    receiver = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_type = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    ref_number = Column(String(100), nullable=False, unique=True)
    exec_month = Column(String(255), nullable=False)


class Etoro(Base):

    __tablename__ = "etoro"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    initial_amount = Column(Numeric(10, 2), nullable=False)
    deposit_amount = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    

class Xtb(Base):

    __tablename__ = "xtb"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    initial_amount = Column(Numeric(10, 2), nullable=False)
    deposit_amount = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    


class Vienna(Base):

    __tablename__ = "vienna"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    initial_amount = Column(Numeric(10, 2), nullable=False)
    deposit_amount = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)

class Revolut(Base):

    __tablename__ = "revolut"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    initial_amount = Column(Numeric(10, 2), nullable=False)
    deposit_amount = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    

class Obligacje(Base):

    __tablename__ = "obligacje"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    initial_amount = Column(Numeric(10, 2), nullable=False)
    deposit_amount = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    


class Generali(Base):

    __tablename__ = "generali"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    initial_amount = Column(Numeric(10, 2), nullable=False)
    deposit_amount = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    

class Nokia(Base):

    __tablename__ = "nokia"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    initial_amount = Column(Numeric(10, 2), nullable=False)
    deposit_amount = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    


class PortfolioSummary(Base):
    
    __tablename__ = "portfolio"
    
    id = Column(Integer, primary_key=True, index=True)
    Date = Column(Date, nullable=False, unique=True)
    Total_Value = Column(Numeric(10, 2), nullable=False)
    Deposits = Column(Numeric(10, 2), nullable=False)
    Profit = Column(Numeric(10,2), Computed('"Total_Value" - "Deposits"', persisted=True), nullable=True)
    
