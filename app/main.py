from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import categories, transactions
from app.models import category, transaction
from app.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Expense Tracker", lifespan=lifespan)

app.include_router(categories.router)
app.include_router(transactions.router)