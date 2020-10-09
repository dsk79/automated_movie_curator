import asyncio
import json
from asyncio import gather

import requests

from controllers import Session
from controllers.MovieController import MovieController
from controllers.RequestController import RequestController
from controllers.UserController import UserController
from settings.movie_api import movie_db_api_key
from utils.utils import has_movie_manager_role
from constants.MovieCommandsConstants import failed_msg as failed_msg, emoji_unicode_dict, MOVIE_DATABASE_API_URL, \
    IMDB_URL
from constants.MovieCommandsConstants import removed_msg as removed_msg

# Create controllers
movieController = MovieController()
userController = UserController()
requestController = RequestController()

# flag to parse for movie year
YEAR_FLAG = "-year"


class MovieCommands:

    async def add_movie(self, bot, ctx, args):
        """
        Adds the movie to the movies table if it does not exist. Records the suggestion metadata
        """
        print(f"start {self.add_movie.__name__}")

        # Create new db session
        session = Session()

        # Check if the user already exists in the users table, if not add the user
        user_record = userController.upsert_user_with_role(session, ctx.author, True)
        user_id = user_record.id

        # Parse the args and grab the desired movie title and year
        searched_movie_title, searched_movie_year = self.get_year_and_title(args)

        # Retrieve possible movies based on the title and year and validate them
        response_json, movie_list, validation_result = await self.retrieve_movie_list(ctx, searched_movie_title,
                                                                                      searched_movie_year)

        # If validation failed, return error message here
        if validation_result is not None:
            return validation_result

        # if there is any ambiguity for the movie, have the user determine which movie was intended
        if len(movie_list) > 1:
            msg = f'Multiple possibilities found. Please select from the below list or refine your search.\n'
            print(msg)
            await ctx.send(msg)

            msg = f"API returned {response_json['totalResults']} results but found {len(movie_list)} perfect matches."
            print(msg)

            msg, reaction = await self.write_list_and_emojis(bot, ctx, movie_list)

            if reaction is not None:
                # User responded with the selection from possible movies, process that selection
                index = list(emoji_unicode_dict.values()).index(reaction.emoji)

                selected_movie = movie_list[index]
            else:
                # User timed out on the selection list. Do nothing and return
                msg = f"No movie was selected."
                return msg
        else:
            selected_movie = movie_list[0]

            msg = f"Adding 1 perfect match. {selected_movie['Title']} ({selected_movie['Year']})"
            print(msg)
            await ctx.send(msg)

        try:
            imdb_id, movie_title, movie_year = selected_movie['imdbID'], selected_movie['Title'], selected_movie['Year']

            # Record the movie and suggestion metadata to the database
            movie_record = movieController.add_movie_suggestion_if_not_exists(session, imdb_id, movie_title, movie_year)
        except:
            msg = f"Failed to add {ctx.author.name}'s suggestion of {movie_title} ({movie_year}) to the database."
        finally:
            await ctx.send(msg)

            imdb_db_url = IMDB_URL + selected_movie['imdbID']
            await ctx.send(imdb_db_url)

            # Grab the movie year and title from the response in case no year was passed in
            movie_year, movie_title = selected_movie['Year'], selected_movie['Title']

            # Add the request record linking from user to movie
            requestController.add_movie_request(session, user_id, movie_record.id)

            # Send channel notification confirming role addition
            msg = f'{ctx.author.name}, your suggestion of {movie_title} ({movie_year}) has been added!'
            print(msg)
            await ctx.send(msg)
            session.close()

    async def list_movies(self, ctx):
        """
        Lists all the movies in the suggestion queue from the database
        :param ctx:
        :return:
        """
        # Create new db session
        session = Session()

        # Make the query call in the service layer with the controller
        results = requestController.retrieve_active_movie_request_list(session)

        # Verify there are results
        if not results:
            msg = "```There are no movies in the request queue. Why not add some with the <!add command>?```"
            await ctx.send(msg)
            return msg

        # Print out the movies in a numbered list
        msg = ""
        i = 1
        for result in results:
            print(result)
            movie = result.Movie
            msg += f"{i}) {movie.movie_title} ({movie.movie_year})\n"
            i += 1

            if i % 10 == 1:
                await ctx.send(msg)
                msg = ""

        # After the printing out full sets of 10, print out any remaining movies
        if i % 10 != 1:
            await ctx.send(msg)

    async def retrieve_movie_list(self, ctx, searched_movie_title, searched_movie_year):
        # Call internet movie database to query
        response_json = self.get_movie_api_response(searched_movie_title,
                                                    searched_movie_year)
        # validate the API search returned valid results
        validation_result = self.validate_movie_search_results(ctx,
                                                               response_json,
                                                               searched_movie_title,
                                                               searched_movie_year)

        # A not None result means there was an error, return the error message
        if validation_result is not None:
            return response_json, None, validation_result

        # Retrieve list of either movies that are exact match for the title, or all the movies returned from API
        movie_list = self.generate_movie_list(response_json,
                                              searched_movie_title,
                                              searched_movie_year)

        return response_json, movie_list, validation_result

    async def write_list_and_emojis(self, bot, ctx, movies):
        """
        Iterates over list of results and adds emojis reactions.  Sets timeouts for waiting user reaction
        :param bot: reference to running bot
        :param ctx: discord message context
        :param movies: list of movies from API
        :return: msg and reaction selected
        """

        msg = ""
        i = 0
        for x in range(0, len(movies)):
            movie = movies[i]

            # Increment i to pull the matching emoji value and increment for next iteration
            i += 1
            msg += f"{emoji_unicode_dict[i]} {movie['Title']} ({movie['Year']})"

            imdb_db_url = " <" + IMDB_URL + movie['imdbID'] + ">\n"
            msg += imdb_db_url

        # Add instructions and ping the user
        msg += f"\n<@{ctx.author.id}> please add the reaction matching your movie (only one movie can be chosen)"

        print(msg)
        movie_list_msg = await ctx.send(f"{msg}")

        # Wait for each emoji to be written before accepting any responses
        for i in range(1, len(movies) + 1):
            await gather(movie_list_msg.add_reaction(emoji_unicode_dict[i]))

        # Callback function to check for user and message response
        def check(reaction, user):
            print(f"inside check. emoji {reaction.emoji} and user is {user}")
            # Generate list of unicode emojis
            number_emoji_list = emoji_unicode_dict.values()

            # verify the reaction is one of the numbered emoji and the command issuer is the person who reacted
            return reaction.emoji in number_emoji_list and user.id == ctx.author.id

        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=15.0, check=check)
        except asyncio.TimeoutError as e:
            msg = f"No emoji response received from {ctx.author.name}. " \
                  f"Please retry your suggestion or narrow your search."
            print(msg)
            await ctx.send(msg)

            reaction = None
            return msg, reaction
        else:
            msg = f"Received valid emoji {reaction.emoji} from user {user}"
            print(msg)
            return msg, reaction

    def get_year_and_title(self, args):
        # See if args contains -year and it's location is 1 less than length
        #  if so, last element is year, join other arguments as movie title
        if YEAR_FLAG in args and len(args) > 2:
            # args[-1] is year, args[-2] = YEAR_FLAG, rest of args is movie title
            searched_movie_title = ' '.join(args[:-2])
            searched_movie_year = args[-1]
        else:
            # no year was supplied, take entire string as movie title
            searched_movie_title = ' '.join(args)
            searched_movie_year = None
        return searched_movie_title, searched_movie_year

    def get_movie_api_response(self, searched_movie_title, searched_movie_year):
        """
        Calls out to the movie API and retrieves list of movies based on title and year
        :param movie_title: search string for movie name
        :param movie_year: optional param for the movie year
        :return: json parsed object of the API response
        """

        # Calls out to the internet movie database API and queries based on the passed in movie and year
        if searched_movie_year is None:
            querystring = {"page": "1", "r": "json", "type": "movie", "s": searched_movie_title}
        else:
            querystring = {"page": "1", "r": "json", "type": "movie", "y": searched_movie_year,
                           "s": searched_movie_title}

        headers = {
            'x-rapidapi-host': "movie-database-imdb-alternative.p.rapidapi.com",
            'x-rapidapi-key': movie_db_api_key
        }

        response = requests.request("GET", MOVIE_DATABASE_API_URL, headers=headers, params=querystring)
        print(response.text)

        # Parse the response text into a json object
        response_json = json.loads(response.text)
        return response_json

    def validate_movie_search_results(self, ctx, response_json, searched_movie_title, searched_movie_year):
        """
        Validates the response from the movie database API call
        :param ctx: discord context
        :param response_json: parsed json response from the movie database API call
        :param searched_movie_title: user entered search string
        :param searched_movie_year: optional user entered search year
        :return: None if no errors found, otherwise returns error message
        """

        # Verify a match was found, otherwise inform user no movies matching were found
        if response_json['Response'] == 'False' or response_json['totalResults'] == 0:
            msg = f'{ctx.author.name}, no movies were found with the name of {searched_movie_title}!'
            if searched_movie_year:
                msg = msg + f' ({searched_movie_year})'
            print(msg)
            return msg

        # No errors were found, so return None
        return None

    def generate_movie_list(self, response_json, searched_movie_title, searched_movie_year):
        """
        Checks if there is an exact match of the user's search title
        :param response_json: parsed json response from the movie database API call
        :param searched_movie_title: user entered search string
        :param searched_movie_year: optional user entered search year
        :return: List containing all exact matches by title (and year if provided)
        """
        movies = response_json['Search']

        movie_matches = []

        # If the user did not enter a year, match only on title
        if searched_movie_year is None:
            for movie in movies:
                #  case insensitive match, store this
                if movie['Title'].lower() == searched_movie_title.lower():
                    movie_matches.append(movie)
        else:
            for movie in movies:
                #  case insensitive match, store this
                if movie['Title'].lower() == searched_movie_title.lower() and movie['Year'] == searched_movie_year:
                    movie_matches.append(movie)

        # Return only the potentially matching movies
        if len(movie_matches) > 0:
            return movie_matches

        # We found no good match candidates, return the original list back as the movie list found
        return movies

    async def remove_movies(self, ctx, args):
        """
        Removes the movie(s) specified from the request table if
        """
        print(f"start {self.remove_movies.__name__}")

        # Verify at least 1 potential movie is passed as a param
        if len(args) < 1:
            msg = f"Please specify at least 1 movie to remove from the suggestion list"
            print(msg)
            # await ctx.send(msg)
            return msg, ""

        if len(args) > 10:
            msg = f"Please specify a maximum of 10 movies at a time"
            print(msg)
            # await ctx.send(msg)
            return msg, ""

        # Create new db session
        session = Session()

        # Retrieve the user's ID to verify they are the requestor
        user = userController.get_user(session, ctx.author)

        # Query the database for open requests (similar to the !list command)
        results = requestController.retrieve_active_movie_request_list(session)

        # Parse the args and convert to a sorted list of ints
        movie_ids_to_remove = {}
        try:
            for arg in args:
                # subtract 1 from the passed in value because the query set is 0 based index
                movie_index = int(arg) - 1

                if movie_index < 0 or movie_index >= results.count():
                    raise IndexError(arg)

                # Map the request_id to user id, requested remove index, and the movie title
                movie_ids_to_remove.update({results[movie_index].Request.id:
                                            [results[movie_index].Request.user_id,
                                             arg,
                                             results[movie_index].Movie.movie_title]})
        except ValueError:
            msg = f"Please use numbers corresponding to the movies in the !list command"
            print(msg)
            # await ctx.send(msg)
            return msg, ""
        except IndexError as ex:
            msg = f"Please make sure the id {ex} of the movie you wish to remove matches what is shown in the !list command"
            print(msg)
            # await ctx.send(msg)
            return msg, ""

        # Check if the requestor has the movie_manager_role which allows removal for any movie
        is_movie_manager = has_movie_manager_role(ctx)

        # Initialize strings to hold information for movies that were removed or skipped
        removed_movies = ""
        failed_movies = ""

        # Iterate over all the movies to be removed and check if the request is valid
        for k, v in movie_ids_to_remove.items():
            # Only allow movies requested by the user or movie manager role to be removed
            if v[0] == user.id or is_movie_manager:
                # Set the request to inactive
                requestController.update_request_active_flag(session,
                                                             request_id=k,
                                                             is_active=False)

                # Add the movie's index and title to the message
                removed_movies += f"{v[1]}) {v[2]}\n"
            else:
                # User did not request movie, and does not have movie manager role, fail to remove this movie
                failed_movies += f"{v[1]}) {v[2]}\n"

        # commit and close db session
        session.commit()
        session.close()

        # Return strings
        removed_movie_resp = ""
        failed_movie_resp = ""

        # if any movies were removed, append
        if removed_movies:
            removed_movie_resp = removed_msg + removed_movies
        if failed_movies:
            failed_movie_resp = failed_msg + failed_movies

        # Return strings containing removed movies and movies not removed
        return removed_movie_resp, failed_movie_resp
