from fastapi import status, Depends, Body, HTTPException, Request, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from .. csv_handler import CSVHandler
from app.database import get_sql_db
import app.schemas as schemas
import app.models as models
from app.transaction_service import TransactionService

router = APIRouter(tags=["xtb_endpoints"], prefix="/xtb")


@router.put("/update_xtb/{id}", response_model=schemas.XTBschema, status_code=status.HTTP_202_ACCEPTED)
def update_xtb(id: int, xtb_body: schemas.UpdateXTBschema = Body(...), db: Session = Depends(get_sql_db)):
    print(f'FUNCTION:PUT: /update_xtb/{id} ')
    transaction_service = TransactionService(db)

    update_data = xtb_body.model_dump(exclude_unset=True)
    update_data.pop("id", None)

    updated_transaction = transaction_service.update_transaction(model_class=models.Etoro, id=id, transaction_data=update_data)
    
    return updated_transaction
       
       

@router.get("/get_all_etoro", response_model=List[schemas.EtoroSchema], status_code=status.HTTP_200_OK)
def get_all_etoro(db: Session = Depends(get_sql_db)):
        etoro_entries = db.query(models.Etoro).all()
        return etoro_entries

@router.get("/get_id_etoro/{id}", response_model=schemas.EtoroSchema, status_code=status.HTTP_200_OK)
def get_all_etoro(id: int, db: Session = Depends(get_sql_db)):
        id_etoro = db.query(models.Etoro).filter(models.Etoro.id == id).first()
        return id_etoro


@router.post("/add_many_etoro", status_code=status.HTTP_201_CREATED)
def add_many_etoro(etoro_entries: List[schemas.EtoroSchema] ,db: Session = Depends(get_sql_db)):
    transaction_service = TransactionService(db)

    etoro_dicts = []
    for entity in etoro_entries:
            initial_total = entity.initial_amount + entity.deposit_amount
            entity.growth_percentage = ((entity.total_amount - (entity.initial_amount + entity.deposit_amount)) / initial_total) * 100
            etoro_dict = entity.model_dump()
            etoro_dicts.append(etoro_dict)
            
    
    transaction_service.add_transactions(models.Etoro, etoro_dicts)

    return {"status": "success", "message": "Transactions added successfully."}
       
    
       
    
@router.post("/add_etoro_transaction", response_model=schemas.EtoroSchema, status_code=status.HTTP_201_CREATED)
def add_etoro_transaction(etoro: schemas.EtoroSchema, db: Session = Depends(get_sql_db)):
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