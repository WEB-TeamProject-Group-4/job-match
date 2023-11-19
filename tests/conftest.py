import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, Session
from app.db.database import get_db, Base
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool


@pytest.fixture
def db() -> Session:
    return TestingSessionLocal()


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope='module')
def client() -> Generator:
    with TestClient(app) as c:
        yield c

