from fastapi import status, Depends, Body, HTTPException, Request, APIRouter
from sqlalchemy import func, asc
from sqlalchemy.orm import Session
from typing import List
from .. csv_handler import CSVHandler
from app.database import get_sql_db
import app.schemas as schemas
import app.models as models
from app.transaction_service import TransactionService

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
            initial_total = entity.initial_amount + entity.deposit_amount
            entity.growth_percentage = ((entity.total_amount - (entity.initial_amount + entity.deposit_amount)) / initial_total) * 100
            xtb_dict = entity.model_dump()
            xtb_dicts.append(xtb_dict)
            
    
    transaction_service.add_transactions(models.Xtb, xtb_dicts)

    return {"status": "success", "message": "Transactions added successfully."}
       
    
       
    
@router.post("/add_xtb_transaction", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_201_CREATED)
def add_xtb_transaction(xtb: schemas.PortfolioTransaction, db: Session = Depends(get_sql_db)):
    initial_total = xtb.initial_amount + xtb.deposit_amount
    growth_percentage = ((xtb.total_amount - (xtb.initial_amount + xtb.deposit_amount)) / initial_total) * 100

    xtb_entry = models.Xtb(
            **xtb.model_dump()
    )
    xtb_entry.growth_percentage = growth_percentage

    db.add(xtb_entry)
    db.commit()
    db.refresh(xtb_entry)

    return xtb_entry