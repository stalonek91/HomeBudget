from sqlalchemy.orm import Session
from app import models
from typing import Type, List, Dict, Any, TypeVar
from app.database import Base
from fastapi import HTTPException, status


SQLAlchemyModel = TypeVar('SQLAlchemyModel', bound=Base)

class TransactionService:
    def __init__(self, db: Session) -> None:
        self.db = db

   
    def add_transactions(self, model_class: Type[SQLAlchemyModel], transaction_data: List[Dict[str, Any]]) -> List[SQLAlchemyModel]:
        new_transactions = [model_class(**data) for data in transaction_data]
        self.db.add_all(new_transactions)
        self.db.commit()
        for transaction in new_transactions:
            self.db.refresh(transaction)
        return new_transactions
    

    def add_transaction(self, model_class: Type[SQLAlchemyModel], transaction_data: Dict[str, Any]) -> SQLAlchemyModel:
        new_transaction = model_class(**transaction_data)
        self.db.add(new_transaction)
        self.db.commit()
        self.db.refresh(new_transaction)

        return new_transaction
    
    def update_transaction(self, model_class: Type[SQLAlchemyModel], id: int, transaction_data: Dict[str, Any]) -> SQLAlchemyModel:
        transaction_query = self.db.query(model_class).filter(model_class.id == id)
        transaction_value = transaction_query.first()

        if not transaction_value:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Looked etoro id: {id} not found!')
        
        try:
            transaction_query.update(transaction_data, synchronize_session=False)
            self.db.commit()
            self.db.refresh(transaction_value)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Following error occured {str(e)}')
       
        return transaction_value


        


