from fastapi import status, Depends, Body, HTTPException, Request, APIRouter
from sqlalchemy import func, asc
from sqlalchemy.orm import Session
from typing import List
from .. csv_handler import CSVHandler
from app.database import get_sql_db
import app.schemas as schemas
import app.models as models
from app.transaction_service import TransactionService

router = APIRouter(tags=["revolut_endpoints"], prefix="/revolut")


@router.put("/update_revolut/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_202_ACCEPTED)
def update_revolut(id: int, revolut_body: schemas.UpdatePortfolioTransaction = Body(...), db: Session = Depends(get_sql_db)):
    print(f'FUNCTION:PUT: /update_revolut/{id} ')
    transaction_service = TransactionService(db)

    update_data = revolut_body.model_dump(exclude_unset=True)
    update_data.pop("id", None)

    updated_transaction = transaction_service.update_transaction(model_class=models.revolut, id=id, transaction_data=update_data)
    
    return updated_transaction
       
       

@router.get("/get_all_revolut", response_model=List[schemas.PortfolioTransaction], status_code=status.HTTP_200_OK)
def get_all_revolut(db: Session = Depends(get_sql_db)):
        revolut_entries = db.query(models.Revolut).order_by(asc(models.Revolut)).all()
        print(revolut_entries)
        return revolut_entries

@router.get("/get_id_revolut/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_200_OK)
def get_all_revolut(id: int, db: Session = Depends(get_sql_db)):
        id_revolut = db.query(models.Revolut).filter(models.Revolut.id == id).first()
        return id_revolut


@router.post("/add_many_revolut", status_code=status.HTTP_201_CREATED)
def add_many_revolut(revolut_entries: List[schemas.PortfolioTransaction] ,db: Session = Depends(get_sql_db)):
    transaction_service = TransactionService(db)

    revolut_dicts = []
    for entity in revolut_entries:
            initial_total = entity.initial_amount + entity.deposit_amount
            entity.growth_percentage = ((entity.total_amount - (entity.initial_amount + entity.deposit_amount)) / initial_total) * 100
            revolut_dict = entity.model_dump()
            revolut_dicts.append(revolut_dict)
            
    
    transaction_service.add_transactions(models.Revolut, revolut_dicts)

    return {"status": "success", "message": "Transactions added successfully."}
       
    
       
    
@router.post("/add_revolut_transaction", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_201_CREATED)
def add_revolut_transaction(revolut: schemas.PortfolioTransaction, db: Session = Depends(get_sql_db)):
    initial_total = revolut.initial_amount + revolut.deposit_amount
    growth_percentage = ((revolut.total_amount - (revolut.initial_amount + revolut.deposit_amount)) / initial_total) * 100

    revolut_entry = models.Revolut(
            **revolut.model_dump()
    )
    revolut_entry.growth_percentage = growth_percentage

    db.add(revolut_entry)
    db.commit()
    db.refresh(revolut_entry)

    return revolut_entry
