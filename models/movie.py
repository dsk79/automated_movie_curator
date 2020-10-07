from sqlalchemy import Column, Integer, String, DateTime, VARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, nullable=True)
    movie_id = Column(VARCHAR(50), nullable=True)
    movie_title = Column(String(50), nullable=True)
    movie_year = Column(Integer, nullable=True)
    inserted_dtm = Column(DateTime, nullable=True)

    def __repr__(self):
        return f'Movie(id={self.id}, movie_id={self.movie_id}, movie_title={self.movie_title}, ' \
               f'movie_year={self.movie_year}, inserted_dtm={self.inserted_dtm}'
