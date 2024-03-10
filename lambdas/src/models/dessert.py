from typing import List, Optional
from .base import Base


class Dessert(Base):
    uid: str
    name: str
    description: str
    price: float
    dessert_type: str
    image: Optional[str]
