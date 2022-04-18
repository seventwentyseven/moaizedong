from __future__ import annotations

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, cog_ext

import moai.botconfig as config
from moai.constants.slash_options import CommandOptions
from moai.constants.colors import Colors
from moai.constants.channels import Channels, Emojis
from moai.constants import variables
from moai.objects.errors import Errors
from moai.objects import utils

import app.settings as settings
import app.state
from app.constants.privileges import Privileges

class Best(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #! Score command !#
    @cog_ext.cog_slash(
        name = "scores",
        description = "Shows user's scores",
        options = CommandOptions.SCORES
    )
    async def best(
        self, 
        ctx: SlashContext, 
        user: str = None, 
        mode: str = None
    ):

        # Get author Player object
        if not user:
            author_osuID = await app.state.services.database.fetch_val(
                "SELECT id FROM users WHERE discord_id = :id",
                {"id": ctx.author.id}
            )
        else:
            author_osuID = await app.state.services.database.fetch_val(
                "SELECT id FROM users WHERE name = :name OR safe_name = :name",
                {"name": user}
            )

        author_osuID = int(author_osuID)

        await ctx.send(author_osuID)


def setup(bot: commands.Bot):
    bot.add_cog(Best(bot))