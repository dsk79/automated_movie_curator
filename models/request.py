from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from models.movie import Movie
from models.user import User

Base = declarative_base()


class Request(Base):
    __tablename__ = 'requests'

    id = Column(Integer, primary_key=True, nullable=True)
    user_id = Column(Integer, ForeignKey(User.id))
    movie_id = Column(Integer, ForeignKey(Movie.id))
    active = Column(Boolean, nullable=False)
    inserted_dtm = Column(DateTime, nullable=True)

    def __repr__(self):
        return f'Request(id={self.id}, user_id={self.user_id}, movie_id={self.movie_id}, ' \
               f'active={self.active}, inserted_dtm={self.inserted_dtm}'
