from fastapi import status, Depends, Body, HTTPException, Request, APIRouter
from sqlalchemy import desc, func, asc
from sqlalchemy.orm import Session
from typing import List
from .. csv_handler import CSVHandler
from app.database import get_sql_db
import app.schemas as schemas
import app.models as models
from app.transaction_service import TransactionService
import pandas as pd
from datetime import datetime

router = APIRouter(tags=["portfolio_endpoints"], prefix="/portfolio")

model_classes = {
    'Etoro': models.Etoro,
    'Xtb': models.Xtb,
    'Vienna': models.Vienna,
    'Revolut': models.Revolut,
    'Obligacje': models.Obligacje,
    'Generali': models.Generali,
    'Nokia': models.Nokia
}

#TODO: Implementing % of total portfolio

@router.get("/calculate_perc/", status_code=status.HTTP_200_OK)
def calculate_perc(db: Session = Depends(get_sql_db), model_classes=model_classes):
     
    wallet_totals = {}
    total_portfolio_amount = 0.0

    for wallet_name, wallet_model in model_classes.items():
          total_amount = db.query(wallet_model.total_amount).order_by(desc(wallet_model.date)).first()
          total_amount = float(total_amount[0])

          wallet_totals[wallet_name] = total_amount
          total_portfolio_amount += total_amount




    wallet_percentages = {wallet:(amount / total_portfolio_amount) * 100 for wallet, amount in wallet_totals.items()}

    df = pd.DataFrame(list(wallet_percentages.items()), columns=['Wallet', 'Percentage'])
    df['Percentage'] = df['Percentage'].round(2)

    return df.to_dict(orient='records')

@router.put("/update_portfolio/{id}", response_model=schemas.PortfolioTransaction, status_code=status.HTTP_202_ACCEPTED)
def update_portfolio(id: int, portfolio_body: schemas.UpdatePortfolioTransaction = Body(...), db: Session = Depends(get_sql_db)):
    print(f'FUNCTION:PUT: /update_portfolio/{id} ')
    transaction_service = TransactionService(db)

    update_data = portfolio_body.model_dump(exclude_unset=True)
    update_data.pop("id", None)

    updated_transaction = transaction_service.update_transaction(model_class=models.PortfolioSummary, id=id, transaction_data=update_data)
    
    return updated_transaction
       
       

@router.get("/get_all_portfolio", response_model=List[schemas.PortfolioSummarySchema], status_code=status.HTTP_200_OK)
def get_all_portfolio(db: Session = Depends(get_sql_db)):
        portfolio_entries = db.query(models.PortfolioSummary).order_by(asc(models.PortfolioSummary.date)).all()
        print(portfolio_entries)
        return portfolio_entries

@router.get("/get_id_portfolio/{id}", response_model=schemas.PortfolioSummarySchema, status_code=status.HTTP_200_OK)
def get_all_portfolio(id: int, db: Session = Depends(get_sql_db)):
        id_portfolio = db.query(models.PortfolioSummary).filter(models.PortfolioSummary.id == id).first()
        return id_portfolio



    
#TODO: implement generate_portfolio_entry function
# columns from each table with total amount
#'total_amount'
# check if sum of last deposit per month can be added like n - n-1 

@router.post("/generate_summary",response_model=schemas.PortfolioSummarySchema, status_code=status.HTTP_201_CREATED)
def generate_summary(db: Session = Depends(get_sql_db), model_classes = model_classes):
     
    list_of_totals = []
    list_of_deposits = []
    todays_date = datetime.today().strftime('%Y-%m-%d')
    

    for model_name, model_class in model_classes.items():
         total = db.query(model_class.total_amount).order_by(desc(model_class.date)).first()
         if total:
              list_of_totals.append(total[0])

    for model_name, model_class in model_classes.items():
         sum_of_each_dep = db.query(func.sum(model_class.deposit_amount)).scalar()
         if sum_of_each_dep:
              list_of_deposits.append(sum_of_each_dep)

    sum_of_totals = sum(list_of_totals)
    sum_of_deposits = sum(list_of_deposits)

    last_total_entry = db.query(models.PortfolioSummary).order_by(desc(models.PortfolioSummary.date)).offset(0).first()
    value_last_total_entry = last_total_entry.sum_of_acc if last_total_entry else None


    print(sum_of_deposits)
    transaction_data = {    
        'date': todays_date,
        'sum_of_acc': sum_of_totals,
        'last_update_profit': sum_of_totals-value_last_total_entry if value_last_total_entry else 0,
        'sum_of_deposits': sum_of_deposits,
        'all_time_profit': sum_of_totals-sum_of_deposits}

    transaction = TransactionService(db)
    transaction.add_transaction(model_class=models.PortfolioSummary, transaction_data=transaction_data)

    print(sum(list_of_totals))
    return transaction_data




@router.delete("/delete_portfolio/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_oportfolio(id: int, db: Session = Depends(get_sql_db)):
    get_obl_id = db.query(models.PortfolioSummary).filter(models.PortfolioSummary.id == id)
    portfolio = get_obl_id.first()

    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'portfolio with id: {id} has not been found')
      
    try:
        db.delete(portfolio)
        db.commit()
        return None
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'There has been a problem with deleting from DB: {str(e)}')

        
        
      


