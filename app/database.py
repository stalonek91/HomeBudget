from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


SQLALCHEMY_DATABASE_URL = "postgresql://sylwestersojka:123@localhost/homebudget_db"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_sql_db():
    conn = SessionLocal()
    try:
        yield conn
    finally:
        if conn:
            conn.close()