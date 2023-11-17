import pytest
from sqlalchemy.orm import Session
from unittest.mock import MagicMock


@pytest.fixture
def db():
    return MagicMock(spec=Session)