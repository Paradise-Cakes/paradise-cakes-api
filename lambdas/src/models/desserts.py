from typing import List, Optional
from .base import Base


class Image(Base):
    image_id: str
    url: str
    position: int


class Price(Base):
    size: str
    base: float


class Dessert(Base):
    dessert_id: str = None
    name: str = None
    description: str = None
    prices: List[Price] = None
    dessert_type: str = None
    ingredients: Optional[List[str]] = None
    created_at: str = None
    updated_at: str = None
    images: Optional[List[Image]] = None


class PostDessertRequest(Base):
    name: str
    description: str
    prices: List[Price]
    dessert_type: str
    ingredients: List[str]
