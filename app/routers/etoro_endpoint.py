from fastapi import status, Depends, Body, HTTPException, Request, APIRouter
from sqlalchemy import func, asc
from sqlalchemy.orm import Session
from typing import List
from .. csv_handler import CSVHandler
from app.database import get_sql_db
import app.schemas as schemas
import app.models as models
from app.transaction_service import TransactionService

router = APIRouter(tags=["etoro"], prefix="/etoro")

#TODO: check ruff

@router.get("/return_df", status_code=status.HTTP_200_OK)
def return_df(db: Session = Depends(get_sql_db)):
      pass
              


@router.put("/update_etoro/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_202_ACCEPTED)
def update_etoro(id: int, etoro_body: schemas.UpdatePortfolioTransaction = Body(...), db: Session = Depends(get_sql_db)):
    print(f'FUNCTION:PUT: /update_etoro/{id} ')
    transaction_service = TransactionService(db)

    update_data = etoro_body.model_dump(exclude_unset=True)
    update_data.pop("id", None)

    updated_transaction = transaction_service.update_transaction(model_class=models.Etoro, id=id, transaction_data=update_data)
    
    return updated_transaction
       
       

@router.get("/get_all_etoro", response_model=List[schemas.PortfolioTransaction], status_code=status.HTTP_200_OK)
def get_all_etoro(db: Session = Depends(get_sql_db)):
        etoro_entries = db.query(models.Etoro).order_by(asc(models.Etoro.date)).all()
        return etoro_entries

@router.get("/get_id_etoro/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_200_OK)
def get_all_etoro(id: int, db: Session = Depends(get_sql_db)):
        id_etoro = db.query(models.Etoro).filter(models.Etoro.id == id).first()
        return id_etoro


@router.post("/add_many_etoro", status_code=status.HTTP_201_CREATED)
def add_many_etoro(etoro_entries: List[schemas.PortfolioTransaction] ,db: Session = Depends(get_sql_db)):
    transaction_service = TransactionService(db)

    etoro_dicts = []
    for entity in etoro_entries:
            initial_total = entity.initial_amount + entity.deposit_amount
            entity.growth_percentage = ((entity.total_amount - (entity.initial_amount + entity.deposit_amount)) / initial_total) * 100
            etoro_dict = entity.model_dump()
            etoro_dicts.append(etoro_dict)
            
    
    transaction_service.add_transactions(models.Etoro, etoro_dicts)

    return {"status": "success", "message": "Transactions added successfully."}
       
    
       
    
@router.post("/add_etoro_transaction", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_201_CREATED)
def add_etoro_transaction(etoro: schemas.PortfolioTransaction, db: Session = Depends(get_sql_db)):
    initial_total = etoro.initial_amount + etoro.deposit_amount
    growth_percentage = ((etoro.total_amount - (etoro.initial_amount + etoro.deposit_amount)) / initial_total) * 100

    etoro_entry = models.Etoro(
            **etoro.model_dump()
    )
    etoro_entry.growth_percentage = growth_percentage

    db.add(etoro_entry)
    db.commit()
    db.refresh(etoro_entry)

    return etoro_entry



@router.delete("/delete_etoro/{transaction_date}", status_code=status.HTTP_200_OK)
def delete_etoro(transaction_date: str, db: Session = Depends(get_sql_db)):
    
    get_obl_id = db.query(models.Etoro).filter(models.Etoro.date == transaction_date)
    etoro = get_obl_id.first()

    print(f'DEBUG: Transaction_date is type: {type(transaction_date)} and value: {transaction_date}')
    print(f'DEBUG: models.Etoro.date is type: {type(models.Etoro.date)} with value: {etoro}')



    if etoro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'etoro with id: {id} has not been found')
      
    try:
        db.delete(etoro)
        db.commit()
        return f'Entry with date: {etoro} deleted succesfully!'
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'There has been a problem with deleting from DB: {str(e)}')


