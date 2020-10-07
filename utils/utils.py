import logging

import discord

import settings.discord as settings


# function to help facilitate logging
def print_and_log(msg):
    print(msg)
    logging.info(msg)


# Function to get the specified role from the server
def get_server_role(ctx, role_id):
    role = discord.utils.get(ctx.guild.roles,
                             id=role_id)
    return role


# helper function to determine if a user has the specified role
def user_has_role(member, role_id):
    return any(x.id == role_id for x in member.roles)


# Helper function to determine if a user has the server specific movie role
def has_movie_role(ctx):
    """
    Returns if the message sender has the movie role. The user on the server is the source of truth,
    not the database
    """
    movie_role = get_server_role(ctx, settings.movie_role_id)

    has_role = user_has_role(ctx.author, movie_role.id)

    msg = f"{ctx.message.author} has_movie_role is {has_role}"
    print_and_log(msg)

    return has_role


# Helper function to determine if a user does not have the server specific movie role
def not_has_movie_role(ctx):
    """
    Returns if the message sender does not have the movie role. The user on the server is the source of truth,
    not the database
    """
    movie_role = get_server_role(ctx, settings.movie_role_id)

    not_has_role = not user_has_role(ctx.author, movie_role.id)

    msg = f"{ctx.message.author} not_has_movie_role is {not_has_role}"
    print_and_log(msg)

    return not_has_role


# Helper function to determine if a user has either the movie_manager role or is the server owner
def has_movie_manager_role(ctx):
    """
    Returns true if the message sender is either server owner or has the movie manager role
    :param ctx:
    :return:
    """
    movie_manager_role = get_server_role(ctx, settings.movie_manager_role_id)

    has_role = (ctx.author == ctx.guild.owner) or (user_has_role(ctx.author, movie_manager_role.id))

    msg = f"{ctx.message.author} has_movie_manager_role is {has_role}"
    print_and_log(msg)

    return has_role
