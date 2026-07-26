from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sys
import os

# Ensure the root directory is in the path to import Base
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(128), nullable=False)
    salt = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    watchlist_items = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    portfolio_transactions = relationship("PortfolioTransaction", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(10), index=True, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="watchlist_items")

    def __repr__(self):
        return f"<Watchlist user={self.user_id} symbol={self.symbol}>"


class PortfolioTransaction(Base):
    __tablename__ = "portfolio_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(10), index=True, nullable=False)
    transaction_type = Column(String(10), nullable=False)  # 'BUY' or 'SELL'
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="portfolio_transactions")

    def __repr__(self):
        return f"<Transaction user={self.user_id} {self.transaction_type} {self.shares} {self.symbol} @ {self.price}>"
