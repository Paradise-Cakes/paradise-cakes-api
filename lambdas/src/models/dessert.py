from typing import List, Optional
from .base import Base


class Dessert(Base):
    name: str
    description: str
    price: float
    dessert_type: str
    image: Optional[str]
