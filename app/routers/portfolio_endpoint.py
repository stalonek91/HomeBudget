from fastapi import status, Depends, Body, HTTPException, Request, APIRouter
from sqlalchemy import desc
from sqlalchemy.orm import Session
from typing import List
from .. csv_handler import CSVHandler
from app.database import get_sql_db
import app.schemas as schemas
import app.models as models
from app.transaction_service import TransactionService

router = APIRouter(tags=["portfolio_endpoints"], prefix="/portfolio")


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
        portfolio_entries = db.query(models.PortfolioSummary).all()
        print(portfolio_entries)
        return portfolio_entries

@router.get("/get_id_portfolio/{id}", response_model=schemas.PortfolioSummarySchema, status_code=status.HTTP_200_OK)
def get_all_portfolio(id: int, db: Session = Depends(get_sql_db)):
        id_portfolio = db.query(models.PortfolioSummary).filter(models.PortfolioSummary.id == id).first()
        return id_portfolio



    
#TODO: implement generate_portfolio_entry function
# columns from each table with total amount
#'total_amount'

@router.post("/generate_summary",response_model=schemas.PortfolioSummarySchema, status_code=status.HTTP_201_CREATED)
def generate_summary(db: Session = Depends(get_sql_db)):
     
    model_classes = {
        'Etoro': models.Etoro,
        'Xtb': models.Xtb,
        'Vienna': models.Vienna,
        'Revolut': models.Revolut,
        'Obligacje': models.Obligacje,
        'Generali': models.Generali,
        'Nokia': models.Nokia
    }
    list_of_totals = []
    

    for model_name, model_class in model_classes.items():
         total = db.query(model_class.total_amount).order_by(desc(model_class.date)).first()
         if total:
              list_of_totals.append(total[0])

    sum_of_totals = sum(list_of_totals)
    transaction_data = {    
        'date': '2024-07-21',
        'sum_of_acc': sum_of_totals,
        'last_update_profit': 0,
        'sum_of_deposits': 0,
        'all_time_profit': 0}

    transaction = TransactionService(db)
    add_summary = transaction.add_transaction(model_class=models.PortfolioSummary, transaction_data=transaction_data)



        
    print(sum(list_of_totals))
    return list_of_totals




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

        
        
      


