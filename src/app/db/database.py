from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy import create_engine
from app.core.config import settings


SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.DB_URL}/job_match_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
