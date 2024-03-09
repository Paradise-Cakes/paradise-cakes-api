from typing import List, Optional
from .base import Base


class Dessert(Base):
    name: str
    description: str
    price: float
    image: Optional[str]
