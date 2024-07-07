from app.csv_handler import CSVHandler
import app.models as models
import app.database as database
from app.database import engine, get_sql_db
from fastapi import FastAPI, Body, Response, status, HTTPException, Depends, Request
from app.routers import db_operations
import psycopg2

path_to_csv = 'Transactions.csv'
csv_instance = CSVHandler(path_to_csv)



app = FastAPI()
models.base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    # df = csv_instance.load_csv()
    # print(df.head(5))
    # new_df = csv_instance.create_df_for_db(df)
    # print(new_df.head(15))
    app.include_router(db_operations.router)




