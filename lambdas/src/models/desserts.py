from typing import List, Optional

from .base import Base


class Image(Base):
    image_id: str
    url: str
    position: int
    file_type: str


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
    created_at: int = None
    last_updated_at: int = None
    images: Optional[List[Image]] = None
    visible: bool = False


class PostDessertRequest(Base):
    name: str
    description: str
    prices: List[Price]
    dessert_type: str
    ingredients: List[str]


class PatchDessertRequest(Base):
    name: Optional[str] = None
    description: Optional[str] = None
    prices: Optional[List[Price]] = None
    dessert_type: Optional[str] = None
    ingredients: Optional[List[str]] = None
    images: Optional[List[Image]] = None
    visible: Optional[bool] = None
