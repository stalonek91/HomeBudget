from fastapi import status, Depends, Body, HTTPException, Request, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from .. csv_handler import CSVHandler
from app.database import get_sql_db
import app.schemas as schemas
import app.models as models
from app.transaction_service import TransactionService

router = APIRouter(tags=["vienna_endpoints"], prefix="/vienna")


@router.put("/update_vienna/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_202_ACCEPTED)
def update_vienna(id: int, vienna_body: schemas.UpdatePortfolioTransaction = Body(...), db: Session = Depends(get_sql_db)):
    print(f'FUNCTION:PUT: /update_vienna/{id} ')
    transaction_service = TransactionService(db)

    update_data = vienna_body.model_dump(exclude_unset=True)
    update_data.pop("id", None)

    updated_transaction = transaction_service.update_transaction(model_class=models.vienna, id=id, transaction_data=update_data)
    
    return updated_transaction
       

@router.get("/get_all_dates", response_model=List[schemas.ReturnDate], status_code=status.HTTP_200_OK)
def get_all_dates(db: Session = Depends(get_sql_db)):
        vienna_entries = db.query(models.Vienna.date).all()
        
        return vienna_entries

@router.get("/get_all_vienna", response_model=List[schemas.PortfolioTransaction], status_code=status.HTTP_200_OK)
def get_all_vienna(db: Session = Depends(get_sql_db)):
        vienna_entries = db.query(models.Vienna).all()
        
        return vienna_entries

@router.get("/get_id_vienna/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_200_OK)
def get_all_vienna(id: int, db: Session = Depends(get_sql_db)):
        id_vienna = db.query(models.Vienna).filter(models.Vienna.id == id).first()
        return id_vienna


@router.post("/add_many_vienna", status_code=status.HTTP_201_CREATED)
def add_many_vienna(vienna_entries: List[schemas.PortfolioTransaction] ,db: Session = Depends(get_sql_db)):
    transaction_service = TransactionService(db)

    vienna_dicts = []
    for entity in vienna_entries:
            initial_total = entity.initial_amount + entity.deposit_amount
            entity.growth_percentage = ((entity.total_amount - (entity.initial_amount + entity.deposit_amount)) / initial_total) * 100
            vienna_dict = entity.model_dump()
            vienna_dicts.append(vienna_dict)
            
    
    transaction_service.add_transactions(models.Vienna, vienna_dicts)

    return {"status": "success", "message": "Transactions added successfully."}
       
    
       
    
@router.post("/add_vienna_transaction", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_201_CREATED)
def add_vienna_transaction(vienna: schemas.PortfolioTransaction, db: Session = Depends(get_sql_db)):
    initial_total = vienna.initial_amount + vienna.deposit_amount
    growth_percentage = ((vienna.total_amount - (vienna.initial_amount + vienna.deposit_amount)) / initial_total) * 100

    vienna_entry = models.Vienna(
            **vienna.model_dump()
    )
    vienna_entry.growth_percentage = growth_percentage

    db.add(vienna_entry)
    db.commit()
    db.refresh(vienna_entry)

    return vienna_entry