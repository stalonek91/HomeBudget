from fastapi import status, Depends, Body, HTTPException, APIRouter, UploadFile, File
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List
from io import StringIO
import pandas as pd
import logging

from app.csv_handler import CSVHandler
from app.database import get_sql_db
import app.schemas as schemas
import app.models as models
from app.transaction_service import TransactionService




router = APIRouter(tags=["db_operations"], prefix="/transactions")

@router.get("/get_timeline", status_code=status.HTTP_200_OK)
def get_timeline(db: Session = Depends(get_sql_db)):

       timelines = [value[0] for index, value in enumerate(db.query(models.Transaction.exec_month).distinct())]
       return timelines

@router.get("/get_summary", response_model=schemas.ReturnSummary, status_code=status.HTTP_200_OK)
def get_summary(db: Session = Depends(get_sql_db)):
    try:
        income = db.query(func.sum(models.Transaction.amount)).filter(
                models.Transaction.amount > 0).scalar()
        expenses = db.query(func.sum(models.Transaction.amount)).filter(
                models.Transaction.amount <0).scalar()
    except Exception as e:
           logging.error(f"Database error: {str(e)}")
           raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    income_float = float(income) if income is not None else 0.0
    expenses_float = float(expenses) if expenses is  not None else 0.0

    response = {
           "income": income_float,
           "expenses": expenses_float
    }

    return response


@router.post("/add_csv",response_model=schemas.ADDCSVResponse, status_code=status.HTTP_201_CREATED)
def add_csv(file: UploadFile = File(...), db: Session = Depends(get_sql_db)):

    added_month = None

    logging.info('Entering POST /add_csv request')
    logging.debug('Loading CSV attempt...')

    content = file.file.read().decode('utf-8')
    logging.debug('Raw CSV content:')
    logging.debug(content)

    df = pd.read_csv(StringIO(content), delimiter=';')

    logging.debug(f'Loaded DataFrame head: {df.head(5)}')


    csv_instance = CSVHandler(df)
    df = csv_instance.load_csv()

    if df is not None:
        new_df = csv_instance.create_df_for_db(df)
        if new_df is None:
                logging.error("Error processing DataFrame in create_df_for_db")
                raise HTTPException(status_code=500, detail="Error processing DataFrame in create_df_for_db")
        
        new_df = csv_instance.rename_columns(new_df)
        if new_df is None:
                logging.error("Error processing DataFrame in create_df_for_db")
                raise HTTPException(status_code=500, detail="Error processing DataFrame in create_df_for_db")

        
    
        try:
            df_to_dict = new_df.to_dict(orient='index')
            print('Dictionary representation of DataFrame:')
            print(df_to_dict[0])
        except Exception as e:
            logging.error(f"Error converting DataFrame to dict: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error converting DataFrame to dict: {str(e)}")
        

        try:
            transaction_service = TransactionService(db)
            transaction_service.add_transactions(models.Transaction, list(df_to_dict.values()))
            

            return schemas.ADDCSVResponse(
                status="success",
                records_processed=len(df_to_dict)
            )

        except IntegrityError as e:
               db.rollback()
               raise HTTPException(
                      status_code=status.HTTP_400_BAD_REQUEST,
                      detail="Duplicate ref_number found. This transaction already exists in db"
               )
        
    raise HTTPException(status_code=500, detail="Failed to add transactions to the database")



@router.get("/get_transactions", response_model=List[schemas.TransactionSchema], status_code=status.HTTP_200_OK)
def get_transactions(db: Session = Depends(get_sql_db)):
    try:
        transactions = db.query(models.Transaction).all()
        return transactions
    except SQLAlchemyError as e:
           logging.error(f"Databas error: {str(e)}")
           raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve transactions")


@router.get("/get_transaction_by_id/{transaction_id}", response_model=schemas.ReturnedTransaction, status_code=status.HTTP_200_OK)
def get_transaction_by_id(transaction_id: int, db: Session = Depends(get_sql_db)):
        try:
            logging.info(f"Fetching transaction with id {transaction_id}")

            transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
            if not transaction:
                    logging.warning(f"Transaction with id {transaction_id} not found.")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Transaction with id: {transaction_id} not found!')
            
            return transaction
        except SQLAlchemyError as e:
               logging.error(f"Database error in 'get_transaction_by_id/{transaction_id}' as {str(e)}")
               raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve transactions by ID")


@router.post("/add_transaction", response_model=schemas.TransactionSchema, status_code=status.HTTP_201_CREATED)
def add_transaction(transaction_data: schemas.TransactionSchema, db: Session = Depends(get_sql_db)):
                    try:
                        logging.info(f"Transaction added with ID {new_transaction.id}")
                        new_transaction = models.Transaction(
                                **transaction_data.model_dump()
                        )
                        db.add(new_transaction)
                        db.commit()
                        db.refresh(new_transaction)

                        
                        return new_transaction
                    except SQLAlchemyError as e:
                           db.rollback()
                           logging.error(f"Add transaction failed as {str(e)}")
                           raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed at adding transaction")


@router.put("/update_transaction/{id}", response_model=schemas.ReturnedTransaction, status_code=status.HTTP_200_OK)
def update_transaction(id: int, transaction_data: schemas.TransactionSchema = Body(...), db: Session = Depends(get_sql_db)):
        transaction_query = db.query(models.Transaction).filter(models.Transaction.id == id)
        transaction = transaction_query.first()


        if not transaction:
                logging.warning(f"Transaction with id {id} not found for update.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Transaction with id: {id} not found!')
        
        logging.debug(f'Transaction_data for update: {transaction_data.model_dump()}')

        try:
            transaction_query.update(transaction_data.model_dump(), synchronize_session=False)
            db.commit()
            db.refresh(transaction)
            return transaction
        except SQLAlchemyError() as e:
                logging.error(f"Error updating transaction with id {id}: {str(e)}")
                db.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error occurred: {str(e)}')
        
        


@router.patch("/partialupdate_transaction/{id}", response_model=schemas.ReturnedTransaction, status_code=status.HTTP_200_OK)
def partial_update(id: int, transaction_data: schemas.UpdateTransactionSchema = Body(...), db: Session = Depends(get_sql_db)):
        
        transaction_query = db.query(models.Transaction).filter(models.Transaction.id == id)
        transaction = transaction_query.first()

        if not transaction:
                logging.warning(f"Transaction with id {id} not found for update.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Looked transaction not found id: {id}')
        
        transaction_body = transaction_data.model_dump(exclude_unset=True)
        print(f'Printing content for PATCH request: {transaction_body}')

        try:
            for k,v in transaction_body.items():
                    setattr(transaction,k,v)
            
            db.commit()
            db.refresh(transaction)
            return transaction
        except SQLAlchemyError as e:
            logging.error(f"Error partially updating transaction with id {id}: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to partially update transaction")
              
        