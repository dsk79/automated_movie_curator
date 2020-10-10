import random
import sys
from datetime import datetime

import models.movie as movie
import models.request as request
from utils.utils import print_and_log

selection_choice_type_list = ["oldest", "newest", "random"]


class RequestController:
    def add_movie_request(self, session, user_id, movie_id):
        """
        Adds an entry into the requests table for the specified user and movie
        :param session:
        :param user_id:
        :param movie_id:
        :return:
        """
        print(f"start {self.add_movie_request.__name__}")
        try:
            # Check if movie already has an active request, if so return information that the movie is already queued
            response = self.__find_request(session, movie_id)
            if response is not None:
                msg = f"Movie id : {movie_id} has already has an active request"
                print(msg)
                return msg

            # insert the request
            msg = self.__insert_request(session, user_id, movie_id)
            print(msg)
            return msg
        except:
            print("Unexpected error:", sys.exc_info()[0])
            session.rollback()
        finally:
            session.close()

    def retrieve_movie_poll_requests(self, session, num_choices, choice_selection="Random"):
        """
        Retrieves a list of all active movie requests and creates a list based on the poll parameters
        :param session:
        :param num_choices:
        :param choice_selection: Determines the method to select which requests are added. Defaults to random
        :return: List of active movie requests, or None if none are found
        """
        print(f"start {self.retrieve_movie_poll_requests.__name__}")

        # Retrieve active requests up to num_choices, and gathered by selection type
        response = self.__find_poll_requests(session,
                                             num_choices=num_choices,
                                             choice_selection_type=choice_selection)
        if response is None:
            msg = f"No active requests found. Try suggesting some movies!"
            print(msg)
            return None
        else:
            return response

    def retrieve_active_movie_request_list(self, session):
        """
        Retrieves all the active movie requests
        :param session:
        :return:
        """

        print(f"start {self.retrieve_active_movie_request_list.__name__}")

        # Retrieve all active requests for listing purposes
        response = self.__find_all_active_requests(session)

        if response is None:
            msg = f"No active requests found. Try suggesting some movies!"
            print(msg)
            return None
        else:
            return response

    def update_request_active_flag(self, session, request_id, is_active):
        """
        Sets the request row to have the passed in is_active flag
        :param request_id:
        :param is_active:
        :param session:
        :return:
        """

        session.query(request.Request) \
            .filter(request.Request.id == request_id) \
            .update({"active": is_active})

    def __insert_request(self, session, user_id, movie_id):
        """
        Inserts a new request into the requests table linking to the user and movie
        :return: current success message
        """
        print(f"start {self.__insert_request.__name__}: user_id: {user_id} movie_id: {movie_id}")

        # Create a new movie row with value of has_role of passed in param and insert it into Movies table
        new_request = request.Request(
            user_id=user_id,
            movie_id=movie_id,
            active=True,
            inserted_dtm=datetime.now()
        )

        # Add the new movie to database
        session.add(new_request)
        session.commit()

        msg = f"end {self.__insert_request.__name__}: inserted request with user: {user_id} and movie_id {movie_id}"
        print_and_log(msg)
        return msg

    def __find_request(self, session, movie_id):
        """
        Retrieves an existing movie suggestion request if it exists
        :param session:
        :param movie_id:
        :return: Movie request if it exists, otherwise None
        """

        results = session.query(request.Request) \
            .filter(request.Request.movie_id == movie_id) \
            .filter(request.Request.active == True)

        if results.count() == 0:
            return None
        else:
            return results

    def __find_poll_requests(self, session, num_choices, choice_selection_type):
        """
        Retrieves all active movie suggestions based on the passed in poll parameters
        :param session:
        :return: List of active movie request any exist, otherwise None
        """
        # Oldest
        if choice_selection_type == selection_choice_type_list[0]:
            results = session.query(request.Request, movie.Movie) \
                .join(movie.Movie, request.Request.movie_id == movie.Movie.id) \
                .filter(request.Request.active == True) \
                .order_by(request.Request.inserted_dtm.asc()) \
                .limit(num_choices)
        # Newest choices
        elif choice_selection_type == selection_choice_type_list[1]:
            results = session.query(request.Request, movie.Movie) \
                .join(movie.Movie, request.Request.movie_id == movie.Movie.id) \
                .filter(request.Request.active == True) \
                .order_by(request.Request.inserted_dtm.desc()) \
                .limit(num_choices)
        elif choice_selection_type == selection_choice_type_list[2]:
            # get all active requests
            # TODO: this is going to be a problem when the request table is too large...
            active_requests = self.__find_all_active_requests(session)

            # get a count of number of active requests
            num_active_requests = active_requests.count()

            # if the total number of choices in the poll is equal or more than the number of active requests,
            # place all of them in the poll
            if num_choices >= num_active_requests:
                results = session.query(request.Request, movie.Movie) \
                    .join(movie.Movie, request.Request.movie_id == movie.Movie.id) \
                    .filter(request.Request.active == True) \
                    .order_by(request.Request.inserted_dtm.asc()) \
                    .limit(num_choices)
            elif num_choices < num_active_requests:
                # there are more requests than number of desired poll slots
                # generate a list of size num_choices, ranging from 0 to num_active_requests
                movie_indexes = random.sample(range(0, num_active_requests), num_choices)

                # TODO refactor this, try to do it with a query or generator at least... working for now.
                movie_ids = []
                for i in movie_indexes:
                    movie_ids.append(active_requests[i].Request.movie_id)

                results = session.query(request.Request, movie.Movie) \
                    .join(movie.Movie, request.Request.movie_id == movie.Movie.id) \
                    .filter(request.Request.movie_id.in_(movie_ids)) \
                    .filter(request.Request.active == True) \

        if results.count() == 0:
            return None
        else:
            return results

    def __find_all_active_requests(self, session):
        """
        Retrieves all active movie suggestions
        :param session:
        :return: List of active movie request any exist, otherwise None
        """
        results = session.query(request.Request, movie.Movie) \
            .join(movie.Movie, request.Request.movie_id == movie.Movie.id) \
            .filter(request.Request.active == True) \
            .order_by(request.Request.inserted_dtm.asc())

        if results.count() == 0:
            return None
        else:
            return results
