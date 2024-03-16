from typing import List, Optional, Dict
from .base import Base


class Image(Base):
    uri: str
    description: str


class Dessert(Base):
    dessert_id: str = None
    name: str = None
    description: str = None
    price: Dict[str, float] = None
    dessert_type: str = None
    image_urls: Optional[List[Image]] = None
