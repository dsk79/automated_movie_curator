from discord.ext import commands

from services import PollCommandsService
from utils.utils import has_movie_manager_role, originated_from_server

# Create instance of the service
poll_commands = PollCommandsService.PollCommands()


class PollCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='create_poll',
        description='Creates a poll to vote on a movie.\n'
                    '\tThe default poll choices is 4\n'
                    '\tThe default poll type is Random\n\n'
                    'Optional different flags may be used to configure the poll:\n'
                    '\t-max <maximum_number_of_poll_choices>\n'
                    '\t-type <random|oldest|newest>',
        usage='\n'
              '\nCreate a poll with 5 choices with movies picked randomly:\n'
              '\t!create_poll -max 5\n\n'
              'Create a poll with the default 4 choices max and taking the oldest reqest:\n'
              '\t!create_poll -type oldest\n\n'
              'Create a poll with 3 choices max and taking the most recent requests:\n'
              '\t!create_poll -max 3 -type newest'
    )
    @commands.check(has_movie_manager_role)
    @commands.check(originated_from_server)
    async def create_movie_poll_command(self, ctx, *args):
        msg = await poll_commands.create_movie_poll(self.bot, ctx, args)

        return


def setup(bot):
    bot.add_cog(PollCommands(bot))
