from __future__ import annotations

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, cog_ext

import datetime

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

class Recent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #! Score command !#
    @cog_ext.cog_slash(
        name = "recent",
        description = "Shows user's recent score(s)",
        options = CommandOptions.RECENT
    )
    async def recent(self, ctx: SlashContext, user:str=None, mode:str=None, number:int=1):
        #* Get author privileges
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

        # Number must be an integer
        try:
            number = int(number)
        except ValueError:
            return await ctx.send(embed=Errors.number_range(1,10))
        # Number must be between 1 and 10
        if number > 10 or number < 1:
            return await ctx.send(embed=Errors.number_range(1, 10))

        #* Get score
        score = await app.state.services.database.fetch_one(
            "SELECT s.id scoreid, s.score, s.pp, s.acc, s.max_combo, s.mods, "
            "s.n300, s.n100, s.n50, s.nmiss, s.ngeki, s.nkatu, s.grade, "
            "s.play_time, m.id mapid, m.set_id, m.artist, m.title, "
            "m.version, m.creator, m.total_length, m.diff, "
            "m.max_combo map_max_combo, m.bpm, m.hp, m.cs, m.ar, m.od "
            "FROM scores s LEFT JOIN maps m ON s.map_md5 = m.md5 "
            "WHERE s.userid = :id AND s.mode = :mode "
            "ORDER BY s.id DESC LIMIT 1 OFFSET :offset",
            {"id": user['id'], "mode": mode, "offset": int(number)-1}
        )
        if score:
            score = dict(score)
        else:
            return await ctx.send(embed=Errors.noScores(variables.mode2strfull[int(mode)]))

        #! Reassign variables

        #* Defaults
        # Max Combo
        max_combo = f"{score['max_combo']}x/**{score['map_max_combo']}x**"
        # Ratio (Osu mania only)
        ratio = ""

        #* Total length
        if score['total_length'] < 3600:
            score['total_length'] = str(datetime.timedelta(seconds=score['total_length']))[3:]
        else:
            score['total_length'] = str(datetime.timedelta(seconds=score['total_length']))


        #* Mode specific text generation
        # Std
        if int(mode) in (0,4,8):
            judgements = f"[{score['n300']}/{score['n100']}/{score['n50']}/{score['nmiss']}]"
            map_stats = f"▸ **HP:** {score['hp']} ▸ **AR:** {score['ar']} ▸ **CS:** {score['cs']} ▸ **OD:** {score['od']}"

        # Mania
        elif int(mode) == 3:
            judgements = f"[{score['nkatu']}/{score['n300']}/{score['ngeki']}/{score['n100']}/{score['n50']}/{score['nmiss']}]"
            map_stats  = f"▸ **Keys:** {int(score['cs'])} ▸ **HP:** {score['hp']} ▸ **OD:** {score['od']}"
            max_combo = f"{score['max_combo']}x"

            try:
                ratio = f" ▸ **Ratio:** {round(score['ngeki']/score['n300'], 3)} **: 1**"
            except ZeroDivisionError:
                ratio = f" ▸ **Ratio:** 0 **: 1**"
        # Taiko
        elif int(mode) in (1,5):
            judgements = f"[{score['n300']}/{score['n50']}/{score['nmiss']}]"
            map_stats  = f"▸ **HP:** {score['hp']} ▸ **OD:** {score['od']}"

        # Catch
        elif int(mode) in (2,6):
            judgements = f"[{score['n300']}/{score['n100']}/{score['nkatu']}/{score['nmiss']}]"
            map_stats = f"▸ **HP:** {score['hp']} ▸ **AR:** {score['ar']} ▸ **CS:** {score['cs']} ▸ **OD:** {score['od']}"


        #! Generate embed
        embed = discord.Embed(
            title=f"In osu!{variables.mode2strfull[int(mode)]}",
            description=f"[{score['artist']} - {score['title']} [{score['version']}] by {score['creator']}]"
                        f"(https://{settings.DOMAIN}/b/{score['mapid']}) {utils.mods2str(score['mods'])}",
            color=ctx.author.color,
        )
        embed.set_author(
            name="{}Most recent score for {}".format("" if number == 1 else f"#{number} ", user['name']),
            url=f"https://{settings.DOMAIN}/score/{score['scoreid']}",
            icon_url=f'https://{settings.DOMAIN}/static/images/flags/{user["country"].upper()}.png'
        )
        embed.set_thumbnail(url=f'https://a.{settings.DOMAIN}/{user["id"]}')

        embed.add_field(
            name="Score Info",
            value=""
            f"▸ {variables.grade2emoji[score['grade']]} ▸ **Max Combo:** {max_combo} ▸ "
            f"**PP:** {round(score['pp'], 2):,} ▸ **Acc:** {round(score['acc']):,}%\n"
            f"▸ **Score:** {score['score']:,} ▸ {judgements} {ratio}\n"
            f"▸ **Date Played:** <t:{int(datetime.datetime.timestamp(score['play_time']))}:R>",
            inline=False
        )
        embed.add_field(
            name="Map Info",
            value=f"{map_stats}\n▸ **Stars** {round(score['diff'], 2)} ⭐ ▸ **BPM:** {score['bpm']} ▸ "
            f"**Length:** {score['total_length']}",
            inline=False
        )
        embed.set_footer(
            text=await utils.formatStatus(user['name'], user['latest_activity']),
            icon_url=config.ICON_LINK
        )
        return await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Recent(bot))