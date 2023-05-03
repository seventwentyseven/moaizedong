from typing import Literal
from typing import Union
from typing import Optional

import discord

import app.state
from app.objects.player import Player


async def get_user(
    interaction: discord.Interaction,
    user: Union[str, int, None]
) -> Union[dict[str, str], Player]:
    """
    Get a user from a string or int
    interaction `discord.Interaction`: Will get user from interaction if not specified
    user `int | str | None`: The user to get, can be a discord id, username, mention or None
    """
    if user is None:
        user = interaction.user.id
    elif isinstance(user, str) and len(user) > 15: # mention
        user = int(''.join(filter(str.isdigit, user))) # leave digits only

    if isinstance(user, int): # discord id
        user = await app.state.sessions.players.from_cache_or_sql(discord_id=user)
    else: # username
        user = await app.state.sessions.players.from_cache_or_sql(name=user)

    if not user:
        return {'error': 'not found'}, None

