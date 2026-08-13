from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base  


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)

    transactions: Mapped[List["Transaction"]] = relationship(back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"