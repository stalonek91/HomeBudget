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

router = APIRouter(tags=["xtb_endpoints"], prefix="/xtb")


@router.put("/update_xtb/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_202_ACCEPTED)
def update_xtb(id: int, xtb_body: schemas.UpdatePortfolioTransaction = Body(...), db: Session = Depends(get_sql_db)):
    print(f'FUNCTION:PUT: /update_xtb/{id} ')
    transaction_service = TransactionService(db)

    update_data = xtb_body.model_dump(exclude_unset=True)
    update_data.pop("id", None)

    updated_transaction = transaction_service.update_transaction(model_class=models.Xtb, id=id, transaction_data=update_data)
    
    return updated_transaction
       
       

@router.get("/get_all_xtb", response_model=List[schemas.PortfolioTransaction], status_code=status.HTTP_200_OK)
def get_all_xtb(db: Session = Depends(get_sql_db)):
        xtb_entries = db.query(models.Xtb).order_by(asc(models.Xtb.date)).all()
        print(xtb_entries)
        return xtb_entries

@router.get("/get_id_xtb/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_200_OK)
def get_all_xtb(id: int, db: Session = Depends(get_sql_db)):
        id_xtb = db.query(models.Xtb).filter(models.Xtb.id == id).first()
        return id_xtb


@router.post("/add_many_xtb", status_code=status.HTTP_201_CREATED)
def add_many_xtb(xtb_entries: List[schemas.PortfolioTransaction] ,db: Session = Depends(get_sql_db)):
    transaction_service = TransactionService(db)

    xtb_dicts = []
    for entity in xtb_entries:
            
            xtb_dict = entity.model_dump()
            xtb_dicts.append(xtb_dict)
            
    
    transaction_service.add_transactions(models.Xtb, xtb_dicts)

    return {"status": "success", "message": "Transactions added successfully."}
       
    
       
    
@router.post("/add_xtb_transaction", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_201_CREATED)
def add_xtb_transaction(xtb: schemas.PortfolioTransaction, db: Session = Depends(get_sql_db)):
    

    latest_entry = db.query(models.Xtb).order_by(models.Xtb.date.desc()).first()
    print(latest_entry.deposit_amount)

    if latest_entry:
         new_deposit_amount = latest_entry.deposit_amount + Decimal(xtb.deposit_amount)
    else:
         new_deposit_amount = Decimal(xtb.deposit_amount)
         

    xtb_entry = models.Xtb(
            date=xtb.date,
            deposit_amount=new_deposit_amount,
            total_amount=xtb.total_amount
    )
    

    db.add(xtb_entry)
    db.commit()
    db.refresh(xtb_entry)

    return xtb_entry


@router.delete("/delete_xtb/{transaction_date}", status_code=status.HTTP_200_OK)
def delete_xtb(transaction_date: str, db: Session = Depends(get_sql_db)):
    
    get_obl_id = db.query(models.Xtb).filter(models.Xtb.date == transaction_date)
    xtb = get_obl_id.first()

    print(f'DEBUG: Transaction_date is type: {type(transaction_date)} and value: {transaction_date}')
    print(f'DEBUG: models.obligacja.date is type: {type(models.Xtb.date)} with value: {xtb}')



    if xtb is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'obligacja with id: {id} has not been found')
      
    try:
        db.delete(xtb)
        db.commit()
        return f'Entry with date: {xtb} deleted succesfully!'
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'There has been a problem with deleting from DB: {str(e)}')