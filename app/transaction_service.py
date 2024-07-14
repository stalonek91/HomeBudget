from sqlalchemy.orm import Session
from app import models
from typing import Type, List, Dict, Any, TypeVar
from app.database import Base


SQLAlchemyModel = TypeVar('SQLAlchemyModel', bound=Base)

class TransactionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    #Creating function to check if that entry already exists in db


    def add_transactions(self, model_class: Type[SQLAlchemyModel], transaction_data: List[Dict[str, Any]]) -> List[SQLAlchemyModel]:
        new_transactions = [model_class(**data) for data in transaction_data]
        self.db.add_all(new_transactions)
        self.db.commit()
        for transaction in new_transactions:
            self.db.refresh(transaction)
        return new_transactions
    

    def add_transaction(self, transaction_data: dict) -> models.Transaction:
        new_transaction = models.Transaction(**transaction_data)
        self.db.add(new_transaction)
        self.db.commit()
        self.db.refresh(new_transaction)

        return new_transaction

