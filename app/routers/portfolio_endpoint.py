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


@router.get("/generate_summary_overall",response_model=schemas.PortfolioSummarySchema, status_code=status.HTTP_200_OK)
def generate_summary_overall(db: Session = Depends(get_sql_db), model_classes = model_classes):
     
    output_df = pd.DataFrame(columns= ['Date', 'Total_Value', 'Last_month_profit', 'Monthly deposit', 'All_time_profit'])
    list_of_totals = []
    list_of_dates = []

    N = db.query(model_classes['Etoro']).count()

    for i in range(N):
         
    

        for model_name, model_class in model_classes.items():
            
            total = db.query(model_class.total_amount).order_by(asc(model_class.date)).offset(i).first()
            db_date = db.query(model_class.date).order_by(asc(model_class.date)).offset(i).first()

            if total:
                total_value = total[0]
                print(f'Value to be added from: {model_name}: {total}')
                list_of_totals.append(total_value)
            if db_date:
                date_value = db_date[0]
                print(f'Value to be added from: {model_name}: {date_value}')
                list_of_dates.append(date_value)
    

    output_df["Total_Value"] = pd.Series(list_of_totals)
    output_df["Date"] = pd.Series(list_of_dates)
    col_to_dis = ["Total_Value", "Date"]
    print(output_df[col_to_dis])
    output_df = output_df[col_to_dis]

    grouped_df = output_df.groupby('Date').sum().reset_index()
    print(grouped_df)
   

     


@router.post("/generate_summary",response_model=schemas.PortfolioSummarySchema, status_code=status.HTTP_201_CREATED)
def generate_summary(db: Session = Depends(get_sql_db), model_classes = model_classes):
     
    list_of_totals = []
    list_of_deposits = []
    todays_date = datetime.today().strftime('%Y-%m-%d')
    result_dict = {}
    

    for model_name, model_class in model_classes.items():
         total = db.query(model_class.total_amount).order_by(desc(model_class.date)).first()
         if total:
              list_of_totals.append(total[0])

    for model_name, model_class in model_classes.items():
         deposit_amm = db.query(model_class.deposit_amount).order_by(desc(model_class.date)).first()
         print(f"Type of deposit_amm is: {type(deposit_amm)}")
         if deposit_amm:
              deposit_amm = int(deposit_amm[0])
              list_of_deposits.append(deposit_amm)

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



@router.delete("/delete_portfolio/{transaction_date}", status_code=status.HTTP_200_OK)
def delete_oportfolio(transaction_date: str, db: Session = Depends(get_sql_db)):
    get_obl_id = db.query(models.PortfolioSummary).filter(models.PortfolioSummary.date == transaction_date)
    portfolio = get_obl_id.first()


    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'portfolio with id: {id} has not been found')
      
    try:
        db.delete(portfolio)
        db.commit()
        return f'Entry with date: {transaction_date} deleted succesfully!'
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'There has been a problem with deleting from DB: {str(e)}')

        
        
      


