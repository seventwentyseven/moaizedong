from typing import Union
from typing import Optional

import discord
import traceback
from discord.ext import commands
from discord import app_commands # im using discord.py rewrite(2.0.0)


from app.objects.player import Player

from moaizedong import botconfig
from moaizedong import utils

class RecentCmd(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client

    @app_commands.command(
        name="recent",
        description="Get the recent play(s) of a user",
    )
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="Standard", value=0),
            app_commands.Choice(name="Taiko", value=1),
            app_commands.Choice(name="Catch the Beat", value=2),
            app_commands.Choice(name="Mania", value=3),
            app_commands.Choice(name="Standard +RX", value=4),
            app_commands.Choice(name="Taiko +RX", value=5),
            app_commands.Choice(name="Catch the Beat +RX", value=6),
            #app_commands.Choice(name="Mania +RX", value=7),
            app_commands.Choice(name="Standard +AP", value=8),
        ],
        paged=[
            app_commands.Choice(name="Single Score", value=0),
            app_commands.Choice(name="Multiple Scores", value=1),
        ]
    )
    # describe the arguments
    @app_commands.describe(
        user="The user to get the recent play(s) of. Defaults to the user who invoked the command",
        mode="Mode to get the recent play(s). Defaults to preferred mode.",
        page="Page number. Defaults to 1",
        paged="Whether to show multiple scores or a single score. Defaults to Single Score",
    )
    async def recent(
        self,
        interaction: discord.Interaction,
        user: Optional[str] = None,
        mode: Optional[int] = None,
        page: Optional[int] = None,
        paged: Optional[int] = 0,
    ) -> None:
        try:
            # get the user
            user: Player = await utils.get_user(interaction, user)
            if isinstance(user, dict):
                return await interaction.response.send_message(user['error'])

            # get the mode
            if mode == None:
                mode = user.preferred_mode

            return await interaction.response.send_message("**DEBUG**\n" + str(locals()))
        except:
            if interaction.user.id in botconfig.OWNERS:
                return await interaction.response.send_message(
                    f"```py\n{traceback.format_exc()}```",
                    ephemeral=True,
                )
            else:
                return await interaction.response.send_message(
                    "An error occured. Please try again later. If this error persists, please contact devs.",
                    ephemeral=True,
                )

async def setup(client):
    await client.add_cog(RecentCmd(client))
