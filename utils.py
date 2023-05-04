from typing import Literal
from typing import Union
from typing import Optional

import discord

import app.state
from app.objects.player import Player


async def get_user(
    interaction: discord.Interaction = None,
    user: Union[str, int, None] = None
) -> Union[dict[str, str], Player]:
    """
    Get a user from a string or int
    interaction `discord.Interaction`: Will get user from interaction if not specified
    user `int | str | None`: The user to get, can be a discord id, username, mention or None
    """

    if not (user or interaction):
        raise TypeError("Function requires interaction or user to be specified")

    if not user and interaction:
        user = await app.state.sessions.players.from_cache_or_sql(discord_id=interaction.user.id)
    elif isinstance(user, str) and len(user) > 15:
        user = app.state.sessions.players.from_cache_or_sql(
            discord_id=int("".join(filter(str.isdigit, user)))
        )
    elif isinstance(user, str) and len(user) <= 15:
        user = await app.state.sessions.players.from_cache_or_sql(name=user)

    if not user:
        return ({"error": "not found"}, None)