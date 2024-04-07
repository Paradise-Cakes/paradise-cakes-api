from .base import Base


class DessertImage(Base):
    image_id: str
    dessert_id: str
    file_url: str
    position: int
    created_at: str
    last_updated_at: str
