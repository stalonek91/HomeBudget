from fastapi import status, Depends, Body, HTTPException, Request, APIRouter
from sqlalchemy import func, asc
from sqlalchemy.orm import Session
from typing import List
from .. csv_handler import CSVHandler
from app.database import get_sql_db
import app.schemas as schemas
import app.models as models
from app.transaction_service import TransactionService

router = APIRouter(tags=["obligacje_endpoints"], prefix="/obligacje")



@router.put("/update_obligacje/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_202_ACCEPTED)
def update_obligacje(id: int, obligacje_body: schemas.UpdatePortfolioTransaction = Body(...), db: Session = Depends(get_sql_db)):
    print(f'FUNCTION:PUT: /update_obligacje/{id} ')
    transaction_service = TransactionService(db)

    update_data = obligacje_body.model_dump(exclude_unset=True)
    update_data.pop("id", None)

    updated_transaction = transaction_service.update_transaction(model_class=models.obligacje, id=id, transaction_data=update_data)
    
    return updated_transaction
       
       

@router.get("/get_all_obligacje", response_model=List[schemas.PortfolioTransaction], status_code=status.HTTP_200_OK)
def get_all_obligacje(db: Session = Depends(get_sql_db)):
        obligacje_entries = db.query(models.Obligacje).order_by(asc(models.Obligacje.date)).all()
        print(obligacje_entries)
        return obligacje_entries

@router.get("/get_id_obligacje/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_200_OK)
def get_all_obligacje(id: int, db: Session = Depends(get_sql_db)):
        id_obligacje = db.query(models.Obligacje).filter(models.Obligacje.id == id).first()
        return id_obligacje


@router.post("/add_many_obligacje", status_code=status.HTTP_201_CREATED)
def add_many_obligacje(obligacje_entries: List[schemas.PortfolioTransaction] ,db: Session = Depends(get_sql_db)):
    transaction_service = TransactionService(db)

    obligacje_dicts = []
    for entity in obligacje_entries:
            initial_total = entity.initial_amount + entity.deposit_amount
            entity.growth_percentage = ((entity.total_amount - (entity.initial_amount + entity.deposit_amount)) / initial_total) * 100
            obligacje_dict = entity.model_dump()
            obligacje_dicts.append(obligacje_dict)
            
    
    transaction_service.add_transactions(models.Obligacje, obligacje_dicts)

    return {"status": "success", "message": "Transactions added successfully."}
       
    
       
    
@router.post("/add_obligacje_transaction", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_201_CREATED)
def add_obligacje_transaction(obligacje: schemas.PortfolioTransaction, db: Session = Depends(get_sql_db)):
    initial_total = obligacje.initial_amount + obligacje.deposit_amount
    growth_percentage = ((obligacje.total_amount - (obligacje.initial_amount + obligacje.deposit_amount)) / initial_total) * 100

    obligacje_entry = models.Obligacje(
            **obligacje.model_dump()
    )
    obligacje_entry.growth_percentage = growth_percentage

    db.add(obligacje_entry)
    db.commit()
    db.refresh(obligacje_entry)

    return obligacje_entry


@router.delete("/delete_obligacje/{transaction_date}", status_code=status.HTTP_200_OK)
def delete_nokia(transaction_date: str, db: Session = Depends(get_sql_db)):
    
    get_obl_id = db.query(models.Obligacje).filter(models.Obligacje.date == transaction_date)
    obligacja = get_obl_id.first()

    print(f'DEBUG: Transaction_date is type: {type(transaction_date)} and value: {transaction_date}')
    print(f'DEBUG: models.obligacja.date is type: {type(models.Obligacje.date)} with value: {obligacja}')



    if obligacja is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'obligacja with id: {id} has not been found')
      
    try:
        db.delete(obligacja)
        db.commit()
        return f'Entry with date: {obligacja} deleted succesfully!'
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'There has been a problem with deleting from DB: {str(e)}')

        
        
      