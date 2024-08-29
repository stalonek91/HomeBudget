from fastapi import status, Depends, Body, HTTPException, Request, APIRouter, UploadFile, File
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from .. csv_handler import CSVHandler
from app.database import get_sql_db
import app.schemas as schemas
import app.models as models
from app.transaction_service import TransactionService
import pandas as pd
from io import StringIO
from datetime import datetime

router = APIRouter(tags=["db_operations"], prefix="/transactions")

@router.get("/get_timeline", status_code=status.HTTP_200_OK)
def get_timeline(db: Session = Depends(get_sql_db)):
       timelines = {}
       for index, value in enumerate(db.query(models.Transaction.exec_month).distinct()):
              timelines[index] = value[0]
              
       return timelines

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

    added_month = None

    print('Entering POST /add_csv request')
    print(('Loading CSV attempt: ...'))

    content = file.file.read().decode('utf-8')
    print('Raw CSV content:')
    print(content)

    df = pd.read_csv(StringIO(content), delimiter=';')

    print(f' Wczytany DF to: {df.head(5)}')

    

    csv_instance = CSVHandler(df)
    df = csv_instance.load_csv()

    if df is not None:
        new_df = csv_instance.create_df_for_db(df)
        if new_df is None:
                raise HTTPException(status_code=500, detail="Error processing DataFrame in create_df_for_db")
        
        new_df = csv_instance.rename_columns(new_df)
        if new_df is None:
                raise HTTPException(status_code=500, detail="Error processing DataFrame in create_df_for_db")

        
    
        try:
            df_to_dict = new_df.to_dict(orient='index')
            print('Dictionary representation of DataFrame:')
            print(df_to_dict[0])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error converting DataFrame to dict: {str(e)}")
        

        try:
            transaction_service = TransactionService(db)
            transaction_service.add_transactions(models.Transaction, list(df_to_dict.values()))
            

            return {
                "status": "success",
                "records_processed:": len(df_to_dict)
            }

        except IntegrityError as e:
               db.rollback()
               raise HTTPException(
                      status_code=status.HTTP_400_BAD_REQUEST,
                      detail="Duplicate ref_number found. This transaction already exists in db"
               )
        
    raise HTTPException(status_code=500, detail="Failed to add transactions to the database")



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
        