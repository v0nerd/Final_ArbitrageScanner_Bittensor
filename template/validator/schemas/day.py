from pydantic import BaseModel, HttpUrl
from typing import Optional


class DayBase(BaseModel):
    miner_hotkey: str
    total_profit: float
    timestamp: str


class DayCreate(DayBase):
    miner_hotkey: str
    total_profit: float
    timestamp: str


class DayUpdate(DayBase):
    pass


# Properties shared by models stored in DB


class DayInDBBase(DayBase):
    id: Optional[int] = None
    miner_hotkey: str

    class Config:
        orm_mode = True


# Properties to return to client


class Day(DayInDBBase):
    pass


# Properties properties stored in DB


class DayInDB(DayInDBBase):
    pass
