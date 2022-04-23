from __future__ import annotations

import datetime
import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext

import moai.botconfig as config
from moai.constants.slash_options import CommandOptions
from moai.constants.channels import Channels
from moai.constants import variables
from moai.objects.errors import Errors
from moai.objects import utils

import app.settings as settings
import app.state

class Restrict(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #! Profile command !#
    @cog_ext.cog_slash(
        name="restrict",
        description="Check user best scores in specified mode.",
        options=CommandOptions.BEST
    )
    async def _restrict(self, ctx: SlashContext, user:str=None, mode:str=None,
        size:str="basic", over:int=None, page:int=None):
        """Get user profile in specified mode."""

def setup(bot: commands.Bot):
    bot.add_cog(Restrict(bot))
