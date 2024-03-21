from typing import List, Optional
from .base import Base


class Image(Base):
    uri: str


class Price(Base):
    size: str
    base: float


class Dessert(Base):
    dessert_id: str = None
    name: str = None
    description: str = None
    prices: List[Price] = None
    dessert_type: str = None
    image_urls: Optional[List[Image]] = None
    ingredients: Optional[List[str]] = None
