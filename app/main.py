from app.csv_handler import CSVHandler
import app.models as models
from app.database import engine, get_sql_db, Base
from fastapi import FastAPI, Body, Response, status, HTTPException, Depends, Request
from app.routers import db_operations, xtb_endpoints
import psycopg2





app = FastAPI()
app.include_router(db_operations.router)
app.include_router(xtb_endpoints.router)
models.Base.metadata.create_all(bind=engine)

if __name__ == '__main__':

    pass
    




