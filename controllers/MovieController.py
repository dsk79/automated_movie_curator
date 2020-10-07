import sys
from datetime import datetime

import models.movie as movie
from utils.utils import print_and_log


class MovieController:
    def add_movie_suggestion_if_not_exists(self, session, imdb_id, movie_title, movie_year):
        """
        Adds the a movie suggestion to the movies table if it does not already exist
        """
        print(f"inside {self.add_movie_suggestion_if_not_exists.__name__} start")

        # if movie already exists, do nothing and return
        results = self.__get_movie(session, imdb_id)
        if results.count() > 0:
            msg = f"{imdb_id} already exists in the database."
            print(msg)
            return results.one()

        try:
            # insert a movie here
            movie_record = self.__insert_movie(session, imdb_id, movie_title, movie_year)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            session.rollback()
        finally:
            return movie_record

    def __get_movie(selfs, session, imdb_id):
        """
        Retrieves movie from the database if it exists
        :param session:
        :param imdb_id:
        :return:
        """

        results = session.query(movie.Movie).filter(movie.Movie.movie_id == imdb_id)
        return results

    def __insert_movie(self, session, imdb_id, movie_title, movie_year):
        """
        Inserts a new discord movie into the Movies table with title and year
        :return: current movie
        """
        print(f"start {self.__insert_movie.__name__}: {movie_title} {movie_year}")

        # Create a new movie row with value of has_role of passed in param and insert it into Movies table
        new_movie = movie.Movie(
            movie_id=imdb_id,
            movie_title=movie_title,
            movie_year=movie_year,
            inserted_dtm=datetime.now()
        )

        # Add the new movie to database
        session.add(new_movie)
        session.commit()

        msg = f"end {self.__insert_movie.__name__}: inserted movie {movie_title} ({movie_year})"
        print_and_log(msg)
        return new_movie

