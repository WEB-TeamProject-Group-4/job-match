from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy import create_engine

password = "55555"
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://root:{password}@localhost/job_match_db"

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
