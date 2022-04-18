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

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #! Profile command !#
    @cog_ext.cog_slash(
        name="profile",
        description="Check user profile in specified mode.",
        options=CommandOptions.PROFILE
    )
    async def _profile(self, ctx: SlashContext, user:str=None, mode:str=None, size:str="basic"):
        """Get user profile in specified mode."""

        # Get author Player object
        author_priv = await app.state.services.database.fetch_val(
            "SELECT priv FROM users WHERE discord_id = :id",
            {"id": ctx.author.id}
        )
        # Check if author is restricted
        if author_priv and not author_priv & 1:
            return await ctx.send(embed=await Errors.privileges())

        #* Get user
        user = await utils.get_user(ctx, user)
        if 'error' in user:
            return await ctx.send(embed=user['embed'])
        else:
            # Assign user to variables
            self_exec = user['self_exec']
            user = user['user']

        #* Privilege checks
        if not user['priv'] & 1:
            if author_priv < 8192:
                return await ctx.send(embed=await Errors.privileges())
            elif ctx.channel_id != Channels.ADMIN_CHAT:
                return await ctx.send(embed=await Errors.AdminChat_only())

        #* If mode not specified, assign user's preferred
        if mode is None:
            mode = user['preferred_mode']

        #* Get user stats
        stats = dict(await app.state.services.database.fetch_one(
            "SELECT * FROM stats WHERE id=:id AND mode=:mode",
            {"id": user['id'], "mode": mode}
        ))
        # Player object
        player: Player = await app.state.sessions.players.from_cache_or_sql(id=user['id'])
        rank_global = await player.get_global_rank(variables.mode2obj[int(mode)])
        rank_country = await player.get_country_rank(variables.mode2obj[int(mode)])

        #* Reassign variables
        # Convert playtime to hours
        stats['playtime'] = int(round(stats['playtime'] / 3600, 0))

        #* Create embed
        embed = discord.Embed(
            title=f"In osu!{variables.mode2strfull[int(mode)]}",
            color=ctx.author.color,
        )
        embed.set_author(
            name=f"{user['name']}'s profile",
            icon_url=f"https://{settings.DOMAIN}/static/images/flags/{user['country'].upper()}.png",
            url=f"https://{settings.DOMAIN}/u/{user['id']}"
        )
        # Basic size
        if size=="basic":
            # Add stats
            embed.add_field(
                name="Stats",
                value=""
                f"▸ **Rank:** #{rank_global} (#{rank_country}{user['country'].upper()})\n"
                f"▸ **PP:** {stats['pp']:,}pp ▸ **Acc:** {round(stats['acc'], 2)}%\n"
                f"▸ **Playcount:** {stats['plays']:,} ({stats['playtime']:,} hours)\n"
                f"▸ **Total Score:** {stats['tscore']:,} ▸ **Ranked Score:** {stats['rscore']:,}\n"
                f"▸ **Ranks:** {Emojis.XH} `{stats['xh_count']:,}`"
                f"{Emojis.X} `{stats['x_count']:,}`"
                f"{Emojis.SH} `{stats['sh_count']:,}`"
                f"{Emojis.S} `{stats['s_count']:,}`"
                f"{Emojis.A} `{stats['a_count']:,}`",
                inline=False
            )
        else:
            # Get variables
            priv_list = await utils.priv2str(user['priv'], separator=' ▸ ')
            if not user['priv'] & 1:
                priv_list = f"**RESTRICTED** ▸ {priv_list}"
            if user['id'] in config.OWNERS_OSU:
                priv_list = f"Owner ▸ {priv_list}"

            user['creation_time'] = datetime.datetime.fromtimestamp(
                user['creation_time']
            ).strftime('%Y-%m-%d %H:%M:%S')

            # Add stats
            embed.add_field(
                name="Stats",
                value=""
                f"▸ **Rank:** #{rank_global} (#{rank_country}{user['country'].upper()})\n"
                f"▸ **PP:** {stats['pp']:,}pp ▸ **Acc:** {round(stats['acc'], 2)}%\n"
                f"▸ **Playcount:** {stats['plays']:,} ({stats['playtime']:,} hours)\n"
                f"▸ **Total Score:** {stats['tscore']:,} ▸ **Ranked Score:** {stats['rscore']:,}\n"
                f"▸ **Max Combo:** {stats['max_combo']:,}\n"
                f"▸ **Total Hits:** {stats['total_hits']:,}\n"
                f"▸ **Replay Views:** {stats['replay_views']:,}\n"
                f"▸ **Ranks:** {Emojis.XH} `{stats['xh_count']:,}`"
                f"{Emojis.X} `{stats['x_count']:,}`"
                f"{Emojis.SH} `{stats['sh_count']:,}`"
                f"{Emojis.S} `{stats['s_count']:,}`"
                f"{Emojis.A} `{stats['a_count']:,}`",
                inline=False
            )
            embed.add_field(
                name="User Info",
                value=""
                f"▸ **Joined: ** {user['creation_time']}\n"
                f"▸ **User ID**: {user['id']}",
                inline=False
            )
            embed.add_field(
                name="Privileges",
                value=priv_list,
                inline=False
            )

        embed.set_footer(
            text=await utils.formatStatus(user['name'], user['latest_activity']),
            icon_url=config.ICON_LINK
        )
        embed.set_thumbnail(
            url=f"https://a.{settings.DOMAIN}/{user['id']}"
        )

        return await ctx.send(embed=embed)

    @commands.command(name="test")
    async def test(self, ctx: commands.Context, priv:int=3):
        await ctx.send(await utils.priv2str(priv))
def setup(bot: commands.Bot):
    bot.add_cog(Profile(bot))
