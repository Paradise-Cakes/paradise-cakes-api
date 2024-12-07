from typing import List, Optional

from .base import Base


class Image(Base):
    image_id: str
    url: str
    position: int
    file_type: str


class Price(Base):
    dessert_id: Optional[str] = None
    size: str
    base_price: float
    discount: Optional[float] = None


class Dessert(Base):
    dessert_id: str
    name: str
    description: str
    dessert_type: str
    created_at: int
    last_updated_at: int
    visible: bool = False
    prices: Optional[List[Price]] = []
    ingredients: Optional[List[str]] = []
    images: Optional[List[Image]] = []


class PostDessertRequest(Base):
    name: str
    description: str
    dessert_type: str
    prices: Optional[List[Price]] = []
    ingredients: Optional[List[str]] = []
    images: Optional[List[Image]] = []


class PatchDessertRequest(Base):
    name: Optional[str] = None
    description: Optional[str] = None
    prices: Optional[List[Price]] = []
    dessert_type: Optional[str] = None
    ingredients: Optional[List[str]] = []
    images: Optional[List[Image]] = []
    visible: Optional[bool] = None
