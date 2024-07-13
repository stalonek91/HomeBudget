from fastapi import status, Depends, Body, HTTPException, Request, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from .. csv_handler import CSVHandler
from .. database import get_sql_db
import app.schemas as schemas
import app.models as models
from app.transaction_service import TransactionService

router = APIRouter(tags=["db_operations"], prefix="/transactions")

#TODO: check ruff
#TODO: create mechanism to prevent adding twice same CSV (based on already existing data)
#TODO: new tables for other portfolio with monthly deposits



@router.post("/add_etoro_transaction", response_model=schemas.EtoroSchema, status_code=status.HTTP_201_CREATED)
def add_etoro_transaction(etoro: schemas.EtoroSchema, db: Session = Depends(get_sql_db)):
    initial_total = etoro.initial_amount + etoro.deposit_amount
    growth_percentage = ((etoro.total_amount - etoro.initial_amount) / initial_total) * 100

    etoro_entry = models.Etoro(
            **etoro.model_dump()
    )

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




@router.post("/add_csv", status_code=status.HTTP_201_CREATED)
def add_csv(db: Session = Depends(get_sql_db)):
        

    path_to_csv = '/Users/sylwestersojka/Documents/HomeBudget/Transactions.csv'
    csv_instance = CSVHandler(path_to_csv)
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
        new_transactions =  transaction_service.add_transactions(list(df_to_dict.values()))
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
        