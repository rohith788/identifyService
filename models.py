from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey,or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Replace with your database connection details
engine = create_engine('sqlite:///contacts.db') # Adjust for your database engine

# Define database models
Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'
    # Create the db models with the necessary models
    id = Column(Integer, primary_key=True)
    phoneNumber = Column(String, nullable=True)
    email = Column(String, nullable=True)
    linkedId = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    linkPrecedence = Column(String, nullable=False, default='primary')
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow)
    deletedAt = Column(DateTime, nullable=True)

# Create database engine and session maker
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_db():
    db = Session()
    try:
        return db
    finally:
        db.close()