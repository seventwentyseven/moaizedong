import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, cog_ext

from moai.constants.slash_options import CommandOptions
from moai.constants.colors import Colors

import app.state
from app.constants.privileges import Privileges
from app.objects.player import Player
class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @cog_ext.cog_slash(
        name="profile",
        description="Check user profile in specified mode.",
        options=CommandOptions.PROFILE
    )
    async def _profile(self, ctx: SlashContext, user:str=None, mode:str=None, size:str="basic"):
        """Get user profile in specified mode."""

        return await ctx.send(f"{user=} {mode=} {size=}")

def setup(bot: commands.Bot):
    bot.add_cog(Profile(bot))
