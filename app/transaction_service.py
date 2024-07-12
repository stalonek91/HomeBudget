from sqlalchemy.orm import Session
from app import models

class TransactionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_transactions(self, transaction_data: list[dict]) -> models.Transaction:
        new_transactions = [models.Transaction(**data) for data in transaction_data]
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

