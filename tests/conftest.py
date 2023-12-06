import pytest

from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.db.database import get_db, Base
from app.main import app


@pytest.fixture
def db() -> Session:
    """
    Provides a SQLAlchemy session for testing purposes.

    This fixture returns a session connected to an in-memory SQLite database.
    It's intended for use in tests that require database access but should not
    affect the production database.

    Returns:
        Session: A SQLAlchemy session object.
    """
    return TestingSessionLocal()


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def test_db():
    """
    Sets up and tears down an in-memory SQLite database for testing.

    This fixture creates all tables in the Base metadata before tests run and
    drops them after tests complete. It ensures that tests run with a clean
    database every time.

    Yields:
        None: This fixture doesn't return any value.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    """
    Overrides the 'get_db' dependency for testing.

    This function replaces the standard database session with a session connected
    to the in-memory SQLite database. It's used to override the app's dependency
    during tests to ensure isolation from the production database.

    Yields:
        Generator[Session, None, None]: A generator yielding the test database session.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope='module')
def client() -> Generator:
    """
    Provides a test client for the FastAPI application.

    This fixture is used to create a TestClient instance with the FastAPI app.
    It allows for sending HTTP requests to the app and receiving responses
    without running a server. Ideal for testing HTTP endpoints.

    Yields:
        Generator[TestClient, None, None]: A generator yielding the FastAPI TestClient.
    """
    with TestClient(app) as c:
        yield c
