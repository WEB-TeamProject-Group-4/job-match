from app.db.database import get_db
from sqlalchemy.orm import Session

def test_get_db():
    expected_db_type = Session

    db_generator = get_db()
    db = next(db_generator)

    assert isinstance(db, expected_db_type)

    db_generator.close()