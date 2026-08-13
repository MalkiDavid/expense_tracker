from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from app.crud import transaction as transaction_crud

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionRead, status_code=201)
async def create_transaction(transaction: TransactionCreate, 
                             db: AsyncSession = Depends(get_db)):
    return await transaction_crud.create_transaction(db, transaction)


@router.get("/", response_model=List[TransactionRead])
async def list_transactions(db: AsyncSession = Depends(get_db)):
    return await transaction_crud.get_transactions(db)


@router.get("/{transaction_id}", response_model=TransactionRead)
async def read_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    db_transaction = await transaction_crud.get_transaction(db, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction


@router.delete("/{transaction_id}", status_code=204)
async def remove_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await transaction_crud.delete_transaction(db, transaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")

@router.patch("/{transaction_id}", response_model=TransactionRead)
async def update_transaction(transaction_id: int, updates: TransactionUpdate, db: AsyncSession = Depends(get_db)):
    db_transaction = await transaction_crud.update_transaction(db, transaction_id, updates)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction