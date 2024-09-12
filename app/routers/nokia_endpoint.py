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

router = APIRouter(tags=["nokia_endpoints"], prefix="/nokia")


@router.put("/update_nokia/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_202_ACCEPTED)
def update_nokia(id: int, nokia_body: schemas.UpdatePortfolioTransaction = Body(...), db: Session = Depends(get_sql_db)):
    print(f'FUNCTION:PUT: /update_nokia/{id} ')
    transaction_service = TransactionService(db)

    update_data = nokia_body.model_dump(exclude_unset=True)
    update_data.pop("id", None)

    updated_transaction = transaction_service.update_transaction(model_class=models.Nokia, id=id, transaction_data=update_data)
    
    return updated_transaction
       
       

@router.get("/get_all_nokia", response_model=List[schemas.PortfolioTransaction], status_code=status.HTTP_200_OK)
def get_all_nokia(db: Session = Depends(get_sql_db)):
        nokia_entries = db.query(models.Nokia).order_by(asc(models.Nokia.date)).all()
        print(nokia_entries)
        return nokia_entries

@router.get("/get_id_nokia/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_200_OK)
def get_all_nokia(id: int, db: Session = Depends(get_sql_db)):
        id_nokia = db.query(models.Nokia).filter(models.Nokia.id == id).first()
        return id_nokia


@router.post("/add_many_nokia", status_code=status.HTTP_201_CREATED)
def add_many_nokia(nokia_entries: List[schemas.PortfolioTransaction] ,db: Session = Depends(get_sql_db)):
    transaction_service = TransactionService(db)

    nokia_dicts = []
    for entity in nokia_entries:
            
            nokia_dict = entity.model_dump()
            nokia_dicts.append(nokia_dict)
            
    
    transaction_service.add_transactions(models.Nokia, nokia_dicts)

    return {"status": "success", "message": "Transactions added successfully."}
       
    
       
    
@router.post("/add_nokia_transaction", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_201_CREATED)
def add_nokia_transaction(nokia: schemas.PortfolioTransaction, db: Session = Depends(get_sql_db)):
    

    latest_entry = db.query(models.Nokia).order_by(models.Nokia.date.desc()).first()
    print(latest_entry.deposit_amount)

    if latest_entry:
         new_deposit_amount = latest_entry.deposit_amount + Decimal(nokia.deposit_amount)
    else:
         new_deposit_amount = Decimal(nokia.deposit_amount)
         

    nokia_entry = models.Nokia(
            date=nokia.date,
            deposit_amount=new_deposit_amount,
            total_amount=nokia.total_amount
    )
    

    db.add(nokia_entry)
    db.commit()
    db.refresh(nokia_entry)

    return nokia_entry


@router.delete("/delete_nokia/{transaction_date}", status_code=status.HTTP_200_OK)
def delete_nokia(transaction_date: str, db: Session = Depends(get_sql_db)):
    
    get_obl_id = db.query(models.Nokia).filter(models.Nokia.date == transaction_date)
    nokia = get_obl_id.first()

    print(f'DEBUG: Transaction_date is type: {type(transaction_date)} and value: {transaction_date}')
    print(f'DEBUG: models.Nokia.date is type: {type(models.Nokia.date)} with value: {nokia}')



    if nokia is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'nokia with id: {id} has not been found')
      
    try:
        db.delete(nokia)
        db.commit()
        return f'Entry with date: {nokia} deleted succesfully!'
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'There has been a problem with deleting from DB: {str(e)}')

        
        
      

