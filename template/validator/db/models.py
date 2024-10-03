from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from template.validator.db.base_class import Base

class Miner(Base):
    __tablename__ = "miner"

    id = Column(Integer, primary_key=True, index=True)
    miner_hotkey = Column(String(256), nullable=False, unique=True)
    last_updated = Column(String(256), nullable=False)
    last_amount = Column(Float, nullable=False)
    transaction_count = Column(Integer, nullable=False)
    arbitrages = relationship("Arbitrage", back_populates="miner", cascade="all, delete-orphan")
    days = relationship("Day", back_populates="miner", cascade="all, delete-orphan")

class Arbitrage(Base):
    __tablename__ = "arbitrage"

    id = Column(Integer, primary_key=True, index=True)
    miner_hotkey = Column(String(256), ForeignKey("miner.miner_hotkey"), nullable=False)
    pair = Column(String, nullable=False)
    exchange_from = Column(String, nullable=False)
    exchange_to = Column(String, nullable=False)
    price_from = Column(Float, nullable=False)
    price_to = Column(Float, nullable=False)
    fees_from = Column(Float, nullable=False)
    fees_to = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(String, nullable=False)
    profit = Column(Float, nullable=False)
    miner = relationship("Miner", back_populates="arbitrages")

class Day(Base):
    __tablename__ = "day"

    id = Column(Integer, primary_key=True, index=True)
    miner_hotkey = Column(String(256), ForeignKey("miner.miner_hotkey"), nullable=False)
    total_profit = Column(Float, nullable=False)
    timestamp = Column(String, nullable=False)
    miner = relationship("Miner", back_populates="days")