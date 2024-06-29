from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your database connection details
DATABASE_URL = "sqlite:///users.db"  # Adjust for your database engine

# Define database models
Base = declarative_base()

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255))
    phoneNumber = Column(String(10))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deletedAt = Column(DateTime, nullable=True)
    linkedID = Column(Integer)
    linkedPrecidnece = Column(String(9))

# Create database engine and session maker
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()