from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate

async def create_transaction(db: AsyncSession, transaction: TransactionCreate) -> Transaction:
    db_transaction = Transaction(**transaction.model_dump())
    db.add(db_transaction)
    await db.commit()
    return await get_transaction(db, db_transaction.id) 

async def get_transaction(db: AsyncSession, transaction_id: int) -> Optional[Transaction]:
    result = await db.execute(select(Transaction).
                        options(selectinload(Transaction.category)).
                        where(Transaction.id == transaction_id))
    return result.scalar_one_or_none()

async def get_transactions(db: AsyncSession) -> List[Transaction]:
    result = await db.execute(select(Transaction).
                              options(selectinload(Transaction.category))
    )
    return list(result.scalars().all())

async def delete_transaction(db: AsyncSession, transaction_id: int) -> bool:
    db_transaction = await get_transaction(db, transaction_id)
    if db_transaction is None:
        return False
    await db.delete(db_transaction)
    await db.commit()
    return True

async def update_transaction(db: AsyncSession, transaction_id: int, updates: TransactionUpdate) -> Optional[Transaction]:
    db_transaction = await get_transaction(db, transaction_id)
    if db_transaction is None:
        return None
    
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_transaction, field, value)

    await db.commit()
    return await get_transaction(db, transaction_id)
