from .base import Base


class DessertImage(Base):
    image_id: str
    dessert_id: str
    position: int
    created_at: int
    last_updated_at: int
    file_extension: str
    url: str
