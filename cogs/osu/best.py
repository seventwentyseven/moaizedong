from __future__ import annotations

import datetime
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
from app.objects.player import Player
from app.constants.privileges import Privileges

class Best(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #! Profile command !#
    @cog_ext.cog_slash(
        name="best",
        description="Check user best scores in specified mode.",
        options=CommandOptions.BEST
    )
    async def _profile(self, ctx: SlashContext, user:str=None, mode:str=None,
        size:str="basic", number:int=None, over:int=None, page:int=None):
        """Get user profile in specified mode."""

        #* Get author Privileges
        author_priv = await app.state.services.database.fetch_val(
            "SELECT priv FROM users WHERE discord_id = :id",
            {"id": ctx.author.id}
        )

        #* Get user
        user = await utils.get_user(ctx, user)
        if 'error' in user:
            return await ctx.send(embed=user['embed'])
        else:
            # Assign user to variables
            self_exec = user['self_exec']
            user = user['user']

        #* Privilege checks
        if not user['priv'] & 1: # Target restricted?
            if author_priv < 8192: # Must be an admin to check restricted
                return await ctx.send(embed=Errors.privileges())
            elif ctx.channel_id != Channels.ADMIN_CHAT: # Channel must be admin chat
                return await ctx.send(embed=Errors.AdminChat_only())

        #* If mode not specified, assign user's preferred
        if mode is None:
            mode = user['preferred_mode']

        #* First, check if over was specified
        # This makes list of possible colissions smaller

        if over is not None:
            # Over must be an integer
            if not isinstance(over, int):
                try:
                    over = int(over)
                except ValueError:
                    return await ctx.send(embed=Errors.not_int("over"))

            # Over must be over 10
            if over < 10:
                return await ctx.send(embed=Errors.number_range("over"))

            # Query sql for info about that
            counts = await app.state.services.database.fetch_val(
                "SELECT COUNT(s.id) FROM scores s "
                "LEFT JOIN maps m ON s.map_md5 = m.md5 "
                "WHERE s.pp >= :over AND m.mode = :mode "
                "AND s.userid = :id AND s.grade!='f' AND m.status=2",
                {"over": over, "mode": mode, "id": user['id']}
            )
            embed = discord.Embed(
                description=f"in osu!{variables.mode2strfull[int(mode)]}, "
            )


def setup(bot: commands.Bot):
    bot.add_cog(Best(bot))
