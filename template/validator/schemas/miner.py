from pydantic import BaseModel, HttpUrl
from typing import Optional


class MinerBase(BaseModel):
    miner_hotkey: str
    last_updated: str
    last_amount: float
    transaction_count: int
    


class MinerCreate(MinerBase):
    miner_hotkey: str
    last_updated: str
    last_amount: float
    transaction_count: int


class MinerUpdate(MinerBase):
    last_updated: str
    last_amount: float
    transaction_count: int


# Properties shared by models stored in DB


class MinerInDBBase(MinerBase):
    id: Optional[int] = None
    miner_hotkey: str

    class Config:
        orm_mode = True


# Properties to return to client


class Miner(MinerInDBBase):
    pass


# Properties properties stored in DB


class MinerInDB(MinerInDBBase):
    pass
