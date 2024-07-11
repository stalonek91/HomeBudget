from app.csv_handler import CSVHandler
import app.models as models
import app.database as database
from app.database import engine, get_sql_db
from fastapi import FastAPI, Body, Response, status, HTTPException, Depends, Request
from app.routers import db_operations
import psycopg2





app = FastAPI()
app.include_router(db_operations.router)
models.base.metadata.create_all(bind=engine)

if __name__ == '__main__':

    pass
    




