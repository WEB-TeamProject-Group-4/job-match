from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.database import get_db
from tests.conftest import SQLALCHEMY_DATABASE_URL


# def test_get_db():
#     expected_db_type = Session

#     db_generator = get_db()
#     db = next(db_generator)

#     assert isinstance(db, expected_db_type)

#     db_generator.close()