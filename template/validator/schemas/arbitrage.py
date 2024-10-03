from pydantic import BaseModel, HttpUrl
from typing import Optional


class ArbitrageBase(BaseModel):
    miner_hotkey: str
    pair: str
    exchange_from: str
    exchange_to: str
    price_from: float
    price_to: float
    fees_from: float
    fees_to: float
    amount: float
    timestamp: str
    profit: float


class ArbitrageCreate(ArbitrageBase):
    miner_hotkey: str
    pair: str
    exchange_from: str
    exchange_to: str
    price_from: float
    price_to: float
    fees_from: float
    fees_to: float
    amount: float
    timestamp: str
    profit: float


class ArbitrageUpdate(ArbitrageBase):
    pass


# Properties shared by models stored in DB


class ArbitrageInDBBase(ArbitrageBase):
    id: Optional[int] = None
    miner_hotkey: str

    class Config:
        orm_mode = True


# Properties to return to client


class Arbitrage(ArbitrageInDBBase):
    pass


# Properties properties stored in DB


class ArbitrageInDB(ArbitrageInDBBase):
    pass
