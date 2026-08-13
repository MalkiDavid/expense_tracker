from sqlalchemy import Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import date as date_type
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[date_type] = mapped_column(index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    description: Mapped[Optional[str]] = mapped_column(default=None)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, date={self.date}, amount={self.amount})>"