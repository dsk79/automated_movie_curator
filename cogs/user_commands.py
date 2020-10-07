from discord.ext import commands

from services import UserCommandsService
from utils import utils

# Create instance of the service
user_commands = UserCommandsService.UserCommands()


class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='add_role',
        description='Adds the Movie Viewer role to the user.',
        aliases=['a']
    )
    async def add_role_command(self, ctx):
        msg = await user_commands.add_role(ctx, ctx.message.author)
        utils.print_and_log(msg)
        return

    @commands.command(
        name='remove_role',
        description='Removes the Movie Viewer role to the user.',
        aliases=['r']
    )
    async def remove_role_command(self, ctx):
        msg = await user_commands.remove_role(ctx, ctx.message.author)
        utils.print_and_log(msg)
        return

    @add_role_command.error
    async def add_role_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            utils.print_and_log(error)
            msg = f"{ctx.message.author.name}, you already have the role added!"
            await ctx.send(f"```{msg}```")

    @remove_role_command.error
    async def remove_role_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            utils.print_and_log(error)
            msg = f"{ctx.message.author.name}, you do not have the role to remove!"
            await ctx.send(f"```{msg}```")


def setup(bot):
    bot.add_cog(UserCommands(bot))
