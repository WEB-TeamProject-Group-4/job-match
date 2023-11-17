import pytest
from sqlalchemy.orm import Session
from unittest.mock import MagicMock


@pytest.fixture(scope='session')
def db():
    return MagicMock(spec=Session)