from .base import Base


class DessertImage(Base):
    image_id: str
    dessert_id: str
    position: int
    created_at: str
    last_updated_at: str
    file_extension: str
    url: str
