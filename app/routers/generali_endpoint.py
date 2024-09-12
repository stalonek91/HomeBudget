from fastapi import status, Depends, Body, HTTPException, Request, APIRouter
from sqlalchemy import func, asc
from sqlalchemy.orm import Session
from typing import List
from .. csv_handler import CSVHandler
from app.database import get_sql_db
import app.schemas as schemas
import app.models as models
from app.transaction_service import TransactionService
from decimal import Decimal

router = APIRouter(tags=["generali_endpoints"], prefix="/generali")


@router.put("/update_generali/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_202_ACCEPTED)
def update_generali(id: int, generali_body: schemas.UpdatePortfolioTransaction = Body(...), db: Session = Depends(get_sql_db)):
    print(f'FUNCTION:PUT: /update_generali/{id} ')
    transaction_service = TransactionService(db)

    update_data = generali_body.model_dump(exclude_unset=True)
    update_data.pop("id", None)

    updated_transaction = transaction_service.update_transaction(model_class=models.Generali, id=id, transaction_data=update_data)
    
    return updated_transaction
       
       

@router.get("/get_all_generali", response_model=List[schemas.PortfolioTransaction], status_code=status.HTTP_200_OK)
def get_all_generali(db: Session = Depends(get_sql_db)):
        generali_entries = db.query(models.Generali).order_by(asc(models.Generali.date)).all()
        print(generali_entries)
        return generali_entries

@router.get("/get_id_generali/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_200_OK)
def get_all_generali(id: int, db: Session = Depends(get_sql_db)):
        id_generali = db.query(models.Generali).filter(models.Generali.id == id).first()
        return id_generali


@router.post("/add_many_generali", status_code=status.HTTP_201_CREATED)
def add_many_generali(generali_entries: List[schemas.PortfolioTransaction] ,db: Session = Depends(get_sql_db)):
    transaction_service = TransactionService(db)

    generali_dicts = []
    for entity in generali_entries:
            
            generali_dict = entity.model_dump()
            generali_dicts.append(generali_dict)
            
    
    transaction_service.add_transactions(models.Generali, generali_dicts)

    return {"status": "success", "message": "Transactions added successfully."}
       
    
       
    
@router.post("/add_generali_transaction", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_201_CREATED)
def add_generali_transaction(generali: schemas.PortfolioTransaction, db: Session = Depends(get_sql_db)):
    

    latest_entry = db.query(models.Generali).order_by(models.Generali.date.desc()).first()
    print(latest_entry.deposit_amount)

    if latest_entry:
         new_deposit_amount = latest_entry.deposit_amount + Decimal(generali.deposit_amount)
    else:
         new_deposit_amount = Decimal(generali.deposit_amount)
         

    generali_entry = models.Generali()(
            date=generali.date,
            deposit_amount=new_deposit_amount,
            total_amount=generali.total_amount
    )
    

    db.add(generali_entry)
    db.commit()
    db.refresh(generali_entry)

    return generali_entry


@router.delete("/delete_generali/{transaction_date}", status_code=status.HTTP_200_OK)
def delete_ogenerali(transaction_date: str, db: Session = Depends(get_sql_db)):
    get_obl_id = db.query(models.Generali).filter(models.Generali.date == transaction_date)
    generali = get_obl_id.first()

    if generali is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'generali with id: {id} has not been found')
    
    print(f'DEBUG: Transaction_date is type: {type(transaction_date)} and value: {transaction_date}')
    print(f'DEBUG: models.Generali.date is type: {type(models.Generali.date)} with value: {generali}')

    try:
        db.delete(generali)
        db.commit()
        return None
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'There has been a problem with deleting from DB: {str(e)}')

        
        
      
