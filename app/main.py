from app.csv_handler import CSVHandler
import app.models as models
from app.database import engine, get_sql_db, Base
from fastapi import FastAPI, Body, Response, status, HTTPException, Depends, Request
from app.routers import db_operations, vienna_endpoints, xtb_endpoints, revolut_endpoints, obligacje_endpoint
import psycopg2





app = FastAPI()
app.include_router(db_operations.router)
app.include_router(xtb_endpoints.router)
app.include_router(vienna_endpoints.router)
app.include_router(revolut_endpoints.router)
app.include_router(obligacje_endpoint.router)

models.Base.metadata.create_all(bind=engine)

if __name__ == '__main__':

    pass
    




