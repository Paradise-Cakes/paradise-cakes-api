from typing import Dict, List, Optional
from uuid import UUID

import pytest

from src.models.base import Base


def test_base_model():
    class ExampleModel(Base):
        id: str
        name: Optional[str]
        thing: Optional[Dict]
        stuff: Optional[List]

    new_model = ExampleModel(
        id="id",
        name="ex",
        thing={"thing1": "ex"},
        stuff=[1, 2, 3],
    )

    assert new_model.clean() == {
        "id": "id",
        "name": "ex",
        "thing": {"thing1": "ex"},
        "stuff": [1, 2, 3],
    }


def test_base_model_uuid():
    class ExampleModel(Base):
        id: UUID
        name: Optional[str]
        thing: Optional[Dict]
        stuff: Optional[List]

    new_model = ExampleModel(
        id="1f4d1ba8-33ea-409b-9c99-9ccc1a35fd24",
        name="ex",
        thing={"thing1": "ex"},
        stuff=[1, 2, 3],
    )

    assert new_model.clean() == {
        "id": "1f4d1ba8-33ea-409b-9c99-9ccc1a35fd24",
        "name": "ex",
        "thing": {"thing1": "ex"},
        "stuff": [1, 2, 3],
    }


def test_base_model_none_attrs():
    class ExampleModel(Base):
        id: UUID
        name: Optional[str]
        thing: Optional[Dict] = None
        stuff: Optional[List] = None

    new_model = ExampleModel(
        id="1f4d1ba8-33ea-409b-9c99-9ccc1a35fd24",
        name="ex",
    )

    assert new_model.clean() == {
        "id": "1f4d1ba8-33ea-409b-9c99-9ccc1a35fd24",
        "name": "ex",
    }
