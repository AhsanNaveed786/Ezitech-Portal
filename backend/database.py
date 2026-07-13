from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine

database_url = "postgresql://postgres:Thakar0.1@localhost:5432/ezitech_portal"

engine = create_engine(database_url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()