from __future__ import annotations

import discord
from moai.constants.colors import Colors
from moai.botconfig import SERVER_NAME_L, SERVER_NAME_L, ICON_LINK


__all__ = ('Errors')

class Errors:
    """Class representing errors of the bot."""

    # Missing privileges error
    async def privileges():
        embed =  discord.Embed(
            title="Error!",
            description="You don't have permissions to use this command, maybe your account isn't linked?.",
            color=Colors.RED
        )
        embed.set_footer(
            text=f"{SERVER_NAME_L}.xyz",
            icon_url=ICON_LINK
        )

        return embed

