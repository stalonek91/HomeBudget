from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL")
print("Environment variable DB_URL:", os.getenv("DB_URL"))
print("SQLAlchemy path:", os.__file__)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
base = declarative_base()

def get_sql_db():
    conn = SessionLocal()
    try:
        yield conn
    finally:
        if conn:
            conn.close()