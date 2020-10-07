from sqlalchemy import Column, Integer, String, DateTime, Boolean, VARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=True)
    discord_id = Column(VARCHAR(120), nullable=True)
    discord_name = Column(String(64), nullable=True)
    has_role = Column(Boolean, default=False, nullable=True)
    inserted_dtm = Column(DateTime, nullable=True)

    def __repr__(self):
        return f'User(id={self.id}, discord_id={self.discord_id}, discord_name={self.discord_name}, ' \
               f'has_role={self.has_role}, inserted_dtm={self.inserted_dtm}'
