from typing import List, Optional
from src.models.base import Base


class Dessert(Base):
    name: str
    description: str
    price: float
    image: Optional[str]
