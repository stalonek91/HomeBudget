from fastapi import status, Depends, Body, HTTPException, Request, APIRouter
from sqlalchemy import func, asc
from sqlalchemy.orm import Session
from typing import List
from .. csv_handler import CSVHandler
from app.database import get_sql_db
import app.schemas as schemas
import app.models as models
from app.transaction_service import TransactionService

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
            initial_total = entity.initial_amount + entity.deposit_amount
            entity.growth_percentage = ((entity.total_amount - (entity.initial_amount + entity.deposit_amount)) / initial_total) * 100
            generali_dict = entity.model_dump()
            generali_dicts.append(generali_dict)
            
    
    transaction_service.add_transactions(models.Generali, generali_dicts)

    return {"status": "success", "message": "Transactions added successfully."}
       
    
       
    
@router.post("/add_generali_transaction", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_201_CREATED)
def add_generali_transaction(generali: schemas.PortfolioTransaction, db: Session = Depends(get_sql_db)):
    initial_total = generali.initial_amount + generali.deposit_amount
    growth_percentage = ((generali.total_amount - (generali.initial_amount + generali.deposit_amount)) / initial_total) * 100

    generali_entry = models.Generali(
            **generali.model_dump()
    )
    generali_entry.growth_percentage = growth_percentage

    db.add(generali_entry)
    db.commit()
    db.refresh(generali_entry)

    return generali_entry


@router.delete("/delete_generali/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ogenerali(id: int, db: Session = Depends(get_sql_db)):
    get_obl_id = db.query(models.Generali).filter(models.Generali.id == id)
    generali = get_obl_id.first()

    if generali is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'generali with id: {id} has not been found')
      
    try:
        db.delete(generali)
        db.commit()
        return None
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'There has been a problem with deleting from DB: {str(e)}')

        
        
      
