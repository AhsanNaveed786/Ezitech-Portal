database_url = "postgresql://postgres:Thakar0.1@localhost:5432/ezitech_portal"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(database_url)
session = sessionmaker(bind=engine)()

from sqlalchemy.orm import declarative_base
Base = declarative_base()
