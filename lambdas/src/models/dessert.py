from typing import List, Optional
from .base import Base


class Dessert(Base):
    uid: str = None
    name: str = None
    description: str = None
    price: float = 0.0
    dessert_type: str = None
    image_url: Optional[str] = None
