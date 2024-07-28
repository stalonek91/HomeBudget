from fastapi import status, Depends, Body, HTTPException, Request, APIRouter, UploadFile, File
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from .. csv_handler import CSVHandler
from app.database import get_sql_db
import app.schemas as schemas
import app.models as models
from app.transaction_service import TransactionService
import pandas as pd
from io import StringIO

router = APIRouter(tags=["db_operations"], prefix="/transactions")

#TODO: check ruff
#TODO: new tables for other portfolio with monthly deposits
    # tbi -> revolut, vienna, obligacje, generali, akcje_nokii

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
        etoro_entries = db.query(models.Etoro).all()
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






@router.get("/get_summary", response_model=schemas.ReturnSummary, status_code=status.HTTP_200_OK)
def get_summary(db: Session = Depends(get_sql_db)):
    income = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.amount > 0).scalar()
    print(type(income))
    
    expenses = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.amount <0).scalar()

    income_float = float(income) if income is not None else 0.0
    expenses_float = float(expenses) if expenses is  not None else 0.0

    response = {
           "income": income_float,
           "expenses": expenses_float
    }

    return response



#FIXME: change the logic to allow file to be passed instead of path
@router.post("/add_csv", status_code=status.HTTP_201_CREATED)
def add_csv(file: UploadFile = File(...), db: Session = Depends(get_sql_db)):

    print('Entering POST /add_csv request')
    print(('Loading CSV attempt: ...'))

    content = file.file.read().decode('utf-8')
    df = pd.read_csv(StringIO(content), delimiter=';')

    print(f'TOP5 rows of df: {df.head(5)}')

    csv_instance = CSVHandler(df)
    df = csv_instance.load_csv()

    if df is not None:
        new_df = csv_instance.create_df_for_db(df)
        if new_df is None:
                raise HTTPException(status_code=500, detail="Error processing DataFrame in create_df_for_db")
        
        new_df = csv_instance.rename_columns(new_df)
        if new_df is None:
                raise HTTPException(status_code=500, detail="Error processing DataFrame in create_df_for_db")

        print(f"Type of new_df: {type(new_df)}")
        print(new_df.head())
    
        try:
            df_to_dict = new_df.to_dict(orient='index')
            print(df_to_dict[0])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error converting DataFrame to dict: {str(e)}")
        
        transaction_service = TransactionService(db)
        new_transactions =  transaction_service.add_transactions(models.Transaction, list(df_to_dict.values()))
        ids = [transaction.id for transaction in new_transactions]

        return {
               "status": "success",
               "records_processed:": len(df_to_dict)
        }

        
    return f'Added properly!!!'



@router.get("/get_transactions", response_model=List[schemas.TransactionSchema], status_code=status.HTTP_200_OK)
def get_transactions(db: Session = Depends(get_sql_db)):
    transactions = db.query(models.Transaction).all()
    return transactions


@router.get("/get_transaction_by_id/{id}", response_model=schemas.ReturnedTransaction, status_code=status.HTTP_200_OK)
def get_transaction_by_id(id: int, db: Session = Depends(get_sql_db)):
        transaction = db.query(models.Transaction).filter(models.Transaction.id == id).first()
        if not transaction:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Transaction with id: {id} not found!')
        
        return transaction


@router.post("/add_transaction", response_model=schemas.TransactionSchema, status_code=status.HTTP_201_CREATED)
def add_transaction(transaction: schemas.TransactionSchema, db: Session = Depends(get_sql_db)):
                    new_transaction = models.Transaction(
                            **transaction.model_dump()
                    )
                    db.add(new_transaction)
                    db.commit()
                    db.refresh(new_transaction)

                    
                    return new_transaction


@router.put("/update_transaction/{id}", response_model=schemas.ReturnedTransaction, status_code=status.HTTP_200_OK)
def update_transaction(id: int, transaction_data: schemas.TransactionSchema = Body(...), db: Session = Depends(get_sql_db)):
        transaction_query = db.query(models.Transaction).filter(models.Transaction.id == id)
        transaction = transaction_query.first()


        if not transaction:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Transaction with id: {id} not found!')
        
        print(f'Transaction_data: {transaction_data.model_dump()}')
        try:
            transaction_query.update(transaction_data.model_dump(), synchronize_session=False)
            db.commit()
        except Exception as e:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Following error occured {str(e)}')
        
        return transaction


@router.patch("/partialupdate_transaction/{id}", response_model=schemas.ReturnedTransaction, status_code=status.HTTP_200_OK)
def partial_update(id: int, transaction_data: schemas.UpdateTransactionSchema = Body(...), db: Session = Depends(get_sql_db)):
        
        transaction_query = db.query(models.Transaction).filter(models.Transaction.id == id)
        transaction = transaction_query.first()

        if not transaction:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Looked transaction not found id: {id}')
        
        transaction_body = transaction_data.model_dump(exclude_unset=True)
        print(f'Printing content for PATCH request: {transaction_body}')

        for k,v in transaction_body.items():
                setattr(transaction,k,v)
        
        db.commit()
        db.refresh(transaction)

        return transaction
        