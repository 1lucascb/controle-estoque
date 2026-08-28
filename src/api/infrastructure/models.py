from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.infrastructure.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)

    # Relationships
    stock_logs: Mapped[List["StockLog"]] = relationship("StockLog", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_amount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    min_stock_threshold: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    image_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    stock_logs: Mapped[List["StockLog"]] = relationship(
        "StockLog", back_populates="product", cascade="all, delete-orphan"
    )

    @property
    def is_low_stock(self) -> bool:
        """Helper to quickly check if alert should be triggered."""
        return self.current_amount <= self.min_stock_threshold


class StockLog(Base):
    __tablename__ = "stock_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    previous_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    new_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    change_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="stock_logs")
    user: Mapped["User"] = relationship("User", back_populates="stock_logs")