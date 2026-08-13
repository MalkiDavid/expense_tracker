from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category
from app.schemas.category import CategoryCreate


async def create_category(db: AsyncSession, category: CategoryCreate) -> Category:
    db_category = Category(name=category.name)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def get_category(db: AsyncSession, category_id: int) -> Optional[Category]:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def get_categories(db: AsyncSession) -> List[Category]:
    result = await db.execute(select(Category))
    return list(result.scalars().all())


async def delete_category(db: AsyncSession, category_id: int) -> bool:
    db_category = await get_category(db, category_id)
    if db_category is None:
        return False
    await db.delete(db_category)
    await db.commit()
    return True