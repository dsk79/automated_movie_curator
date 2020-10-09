import discord
from discord.ext.commands import CheckFailure

import settings.discord as settings
from controllers import Session
from controllers.UserController import UserController
from utils import utils
# Create instance of the UserController
from utils.utils import has_movie_role

controller = UserController()


class UserCommands:

    async def add_role(self, ctx, member: discord.Member):
        """
        Adds role to the discord user. Adds or updates the user in the db Users table to have has_role = True
        """
        print(f"start {self.add_role.__name__}")

        # Retrieve the movie role on the server based on the setting id
        movie_role = utils.get_server_role(ctx, settings.movie_role_id)

        # Create new db session
        session = Session()

        try:
            # If the user doesn't exist in our database, add them with has_role True
            user = controller.upsert_user_with_role(session, member, True)

            # Send channel notification confirming role addition
            msg = f'{member.name} has been granted the role {movie_role.name}!'
        except:
            msg = f'Failed to update {member.name} with role {movie_role.name} in database.'
            return msg
        finally:
            session.close()

        # After the user in the db has been set properly, Check if the discord user already has the role otherwise
        # sync the user and the database entry
        if not has_movie_role(ctx):
            print("user does not have role while attempting to add role, no check failure raised")
            # Add the role to user on the discord if they do not have it already
            await member.add_roles(movie_role)
        else:
            err_msg = "user has role while attempting to add role, check failure raised"
            print(err_msg)
            raise CheckFailure(err_msg)

        # Send message to channel
        await ctx.send(f"```{msg}```")

        # Return message to api for logging
        return f"End: UserCommandsService.{self.add_role.__name__}(): {msg}"

    async def remove_role(self, ctx, member: discord.Member):
        """
        Removes role from the discord user. Adds or updates the user in the db Users table to have has_role = False
        """
        print(f"start {self.remove_role.__name__}")

        # Retrieve the movie role on the server based on the setting id
        movie_role = utils.get_server_role(ctx, settings.movie_role_id)

        # Create new db session
        session = Session()

        try:
            # If the user doesn't exist in our database, add them with has_role False
            user = controller.upsert_user_with_role(session, member, False)

            # Send channel notification confirming role addition
            msg = f'{member.name} no longer has the role {movie_role.name}!'
        except:
            msg = f'Failed to remove {movie_role.name} from {member.name} in database.'
            return msg
        finally:
            session.close()

        # After the user in the db has been set properly, Check if the discord user already has the role otherwise
        # sync the user and the database entry
        if has_movie_role(ctx):
            print("user does has role while attempting to remove role, no check failure raised")
            # Add the role to user on the discord if they do not have it already
            await member.remove_roles(movie_role)
        else:
            err_msg = "user does not have role while attempting to remove role, check failure raised"
            raise CheckFailure(err_msg)
            print(err_msg)

        # Send message to channel
        await ctx.send(f"```{msg}```")

        # Return message to api for logging
        return f"End: UserCommandsService.{self.remove_role.__name__}(): {msg}"
