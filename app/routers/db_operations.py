from fastapi import status, Depends, Body, HTTPException, Request, APIRouter
from sqlalchemy.orm import Session
from typing import List


router = APIRouter(tags=["db_operations"])

@router.get("/")
def main():
    return {"Hello": "World"}