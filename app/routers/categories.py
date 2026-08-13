from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError 
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryRead
from app.crud import category as category_crud

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryRead, status_code=201)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await category_crud.create_category(db, category)
    except:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category name already exists")

@router.get("/", response_model=List[CategoryRead])
async def list_categories(db: AsyncSession = Depends(get_db)):
    return await category_crud.get_categories(db)


@router.get("/{category_id}", response_model=CategoryRead)
async def read_category(category_id: int, db: AsyncSession = Depends(get_db)):
    db_category = await category_crud.get_category(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


@router.delete("/{category_id}", status_code=204)
async def remove_category(category_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await category_crud.delete_category(db, category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")