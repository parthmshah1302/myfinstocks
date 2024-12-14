from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Family:
    id: Optional[int]
    name: str

@dataclass
class Client:
    id: Optional[int]
    name: str
    family_id: int

@dataclass
class Holding:
    id: Optional[int]
    client_id: int
    ticker: str
    quantity: int
    buy_price: float
    buy_date: date