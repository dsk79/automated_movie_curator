from discord.ext import commands

from services import MovieCommandsService
from utils import utils
from utils.utils import has_movie_role

# Create instance of the service
movie_commands = MovieCommandsService.MovieCommands()


class MovieCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='add',
        description='Adds a movie to suggestion list.\n'
                    'Optional flag of "-year" may be used to specify a year to narrow results.',
        usage='<movie_name>\n'
              '\nAdd a movie made in a specific year\n'
              '\t!add <movie_name> -year <movie_year>\n'
              '\nExample of adding the movie "The Lion King" made in 1994\n'
              '\t!add The Lion King -year 1994'
    )
    @commands.check(has_movie_role)
    async def add_movie_command(self, ctx, *args):
        msg = await movie_commands.add_movie(self.bot, ctx, args)

        utils.print_and_log(msg)
        return

    @commands.command(
        name='list',
        description='Lists all movies in the suggestion queue.'
    )
    @commands.check(has_movie_role)
    async def list_movies_command(self, ctx):
        # msg = await movie_commands.list_movies(ctx)
        msg = await movie_commands.list_movies(ctx)

        utils.print_and_log(msg)
        return

    @commands.command(
        name='remove',
        description='Removes the specified movie from the suggestion queue.\n'
                    'Pass in 1 or more movie index numbers with spaces.\n'
                    'Only the movie manager role or the original requester may remove a movie',
        usage='<movie_index_number> <movie_index_number2> <movie_index_number3>.'
    )
    @commands.check(has_movie_role)
    async def remove_movie_command(self, ctx, *args):
        removed_movie_resp, failed_movie_resp = await movie_commands.remove_movies(ctx, args)

        if removed_movie_resp:
            utils.print_and_log(removed_movie_resp)
            await ctx.send(f"```{removed_movie_resp}```")
        if failed_movie_resp:
            utils.print_and_log(failed_movie_resp)
            await ctx.send(f"```{failed_movie_resp}```")
        return

    @add_movie_command.error
    async def add_movie_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            utils.print_and_log(error)
            msg = f"{ctx.message.author.name}, there was an error when adding your request! :( Please try again!"
            await ctx.send(f"```{msg}```")


def setup(bot):
    bot.add_cog(MovieCommands(bot))
