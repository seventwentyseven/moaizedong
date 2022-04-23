from __future__ import annotations

import datetime
import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext

import moai.botconfig as config
from moai.constants.slash_options import CommandOptions
from moai.constants.channels import Channels
from moai.constants.colors import Colors
from moai.constants import variables
from moai.objects.errors import Errors
from moai.objects import utils

from app.objects.player import Player
from app.constants.privileges import Privileges
from cmyui import Ansi, log
from app.discord import Webhook
import app.settings as settings
import app.state

class Restricts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #! Profile command !#
    @cog_ext.cog_slash(
        name="restrict",
        description="Restrict user",
        options=CommandOptions.RESTRICT,
    )

    async def _restrict(self, ctx: SlashContext, user:str=None, reason:str=None):
        """Restrict user (Admin required)"""

        error = False
        #* Permission checks
        author = await app.state.services.database.fetch_one(
            "SELECT id, priv FROM users WHERE discord_id=:d_id",
            {"d_id": ctx.author.id}
        )
        if not author:
            return await ctx.send(embed=Errors.notLinked())

        #* Account is linked, convert to dict and check privileges
        author = dict(author)
        # Check for privileges
        if not author["priv"] & 8192:
            return await ctx.send(embed=Errors.privileges())

        #* Get author object
        ao = await app.state.sessions.players.from_cache_or_sql(id=author["id"])

        #* Get user object
        po = await app.state.sessions.players.from_cache_or_sql(name=user)
        if not po:
            return await ctx.send(embed=Errors.user_not_found(short=True))

        #* Security checks
        if ctx.channel.id != Channels.ADMIN_CHAT:
            return await ctx.send(embed=Errors.AdminChat_only())
        elif po.id == ao.id:
            return await ctx.send(embed=Errors.default("You can't restrict yourself!"))
        elif po.id==1:
            return await ctx.send(embed=Errors.default("You can't restrict Moai 🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿🗿!"))

        #* Privilege checks
        # Owners don't give a fuck about permissions
        if author['id'] in config.OWNERS_OSU:
            pass
        # Developers can restrict up to developers
        elif author['priv'] & 16384 and po.priv.value > 16383:
            return await ctx.send(embed=Errors.default("You can't restrict developers!"))
        # Admins (8192) can restrict everyone up to 4095
        elif author["priv"] & 8192 and po.priv.value > 4095:
            return await ctx.send(embed=Errors.default("Admins can restrict everyone up to Nominator!"))

        #* Other checks
        if po.restricted:
            return await ctx.send(embed=Errors.default("This user is already restricted!"))


        #* All checks passed
        # Restrict this most likley cheating piece of shit
        await po.remove_privs(Privileges.NORMAL)

        await app.state.services.database.execute(
            "INSERT INTO logs "
            "(`from`, `to`, `action`, `msg`, `time`) "
            "VALUES (:from, :to, :action, :msg, NOW())",
            {"from": ao.id, "to": po.id, "action": "restrict", "msg": reason},
        )

        for mode in (0, 1, 2, 3, 4, 5, 6, 8):
            await app.state.services.redis.zrem(
                f"bancho:leaderboard:{mode}",
                po.id,
            )
            await app.state.services.redis.zrem(
                f'bancho:leaderboard:{mode}:{po.geoloc["country"]["acronym"]}',
                po.id,
            )

        if "restricted" in po.__dict__:
            del po.restricted  # wipe cached_property

        log_msg = f"{ao} restricted {po} for: {reason}."

        log(log_msg, Ansi.LRED)

        if webhook_url := settings.DISCORD_AUDIT_LOG_WEBHOOK:
            webhook = Webhook(webhook_url, content=log_msg)
            await webhook.post(app.state.services.http)

        if po.online:
            # log the user out if they're offline, this
            # will simply relog them and refresh their app.state
            po.logout()

        embed = discord.Embed(
            title="User restricted!",
            description=f"Successfully restricted `{po}`\n"
                        f"Reason: `{reason}`",
            color=Colors.GREEN,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text=f"This action has been logged.")
        await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(Restricts(bot))
