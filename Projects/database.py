from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

# SQLALCHEMY_DATABASE_URL = "sqlite:///./Projects.db"
password = 'test@1234'
encoded_password = quote_plus(password)
SQLALCHEMY_DATABASE_URL = f'postgresql://testuser:{encoded_password}@localhost/test'
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
