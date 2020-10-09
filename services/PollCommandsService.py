from asyncio import gather

from constants.MovieCommandsConstants import emoji_unicode_dict, IMDB_URL
from constants.PollCommandsConstants import NUM_CHOICES_FLAG, DEFAULT_NUM_CHOICES, MAX_NUM_CHOICES, \
    SELECTION_CHOICE_TYPE_FLAG, DEFAULT_SELECTION_CHOICE_TYPE, selection_choice_type_list
from controllers import Session
from controllers.RequestController import RequestController

requestController = RequestController()


class PollCommands:
    async def create_movie_poll(self, bot, ctx, args):

        """
        Creates a poll with active movie requests
        """
        print(f"start {self.create_movie_poll.__name__}")

        # Create new db session
        session = Session()

        # parse arguments for number of desired choices
        num_choices = self.__parse_num_choices_flag(args)

        # parse arguments for the type poll to create
        selection_choice_type = self.__parse_choices_selection_type_flag(ctx, args)

        # Retrieve active requests based on the parameters
        requests_list = requestController.retrieve_movie_poll_requests(session,
                                                                       num_choices=num_choices,
                                                                       choice_selection=selection_choice_type)

        if requests_list is None:
            msg = f"No active movie suggestions found. Try !add <movie name> to suggest some!"
            print(msg)
            await ctx.send(msg)
            return
        else:
            # Print out the movies and make a poll
            i = 0
            msg = ""
            for x in range(0, requests_list.count()):
                request = requests_list[i]

                # Increment i to pull the matching emoji value and increment for next iteration
                i += 1
                msg += f"{emoji_unicode_dict[i]} {request.Movie.movie_title} ({request.Movie.movie_year})"

                # Create IMDB URL for the movie listing
                imdb_db_url = " - <" + IMDB_URL + request.Movie.movie_id + ">\n"
                msg += imdb_db_url

            # Send message containing the movies to the channel
            poll_list_msg = await ctx.send(msg)

            # Add polling options
            i = 0
            for i in range(0, requests_list.count()):
                i += 1
                await gather(poll_list_msg.add_reaction(emoji_unicode_dict[i]))

            return

    def __parse_num_choices_flag(self, args):
        print(f"start {self.__parse_num_choices_flag.__name__}")

        # See if args contains -max
        if NUM_CHOICES_FLAG in args and len(args) >= 2:
            # Verify that -max flag is not the last argument (needs an int after it for number)
            flag_index = args.index(NUM_CHOICES_FLAG)
            num_choices_index = flag_index + 1

            if num_choices_index < len(args):
                num_choices = int(args[num_choices_index])

                # Limit the choices to MAX_NUM_CHOICES to prevent polls that are too big
                if num_choices <= MAX_NUM_CHOICES:
                    return num_choices

        return DEFAULT_NUM_CHOICES

    def __parse_choices_selection_type_flag(self, ctx, args):
        print(f"start {self.__parse_choices_selection_type_flag.__name__}")

        # See if args contains -type flag
        if SELECTION_CHOICE_TYPE_FLAG in args and len(args) >= 2:
            # Verify that -type flag is not the last argument (needs an string after it for the type)
            flag_index = args.index(SELECTION_CHOICE_TYPE_FLAG)
            selection_choice_type_index = flag_index + 1

            # Verify there is a value after the -type flag
            if selection_choice_type_index < len(args):
                selection_type = (args[selection_choice_type_index]).lower()

                # Found a valid parameter type, return that
                if selection_type in selection_choice_type_list:
                    return selection_type

                msg = f"Selection type not recognized. Valid types are {selection_choice_type_list}. " \
                      f"Creating a poll of type {DEFAULT_SELECTION_CHOICE_TYPE}"
                print(msg)

        # Any other scenario, return a default poll
        return DEFAULT_SELECTION_CHOICE_TYPE
