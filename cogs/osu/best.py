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
        size:str="basic", over:int=None, page:int=None):
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

        #* First, check if 'over' was specified
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
                return await ctx.send(embed=Errors.number_range(10, None))

            # Query sql for info about that
            counts = await app.state.services.database.fetch_val(
                "SELECT COUNT(s.id) FROM scores s "
                "LEFT JOIN maps m ON s.map_md5 = m.md5 "
                "WHERE s.pp >= :over AND m.mode = :mode "
                "AND s.userid = :id AND s.grade!='f' AND m.status=2",
                {"over": over, "mode": mode, "id": user['id']}
            )
            return await ctx.send(
                f"[{user['name']}](https://{settings.DOMAIN}/u/{user['id']}) "
                f"has **{counts}** scores over **{over}pp** in osu!{variables.mode2strfull[int(mode)]}."
            )

        #* If 'page' was specified, check if it's an integer
        if page is not None:
            # page must be an integer
            if not isinstance(page, int):
                try:
                    page = int(page)
                except ValueError:
                    return await ctx.send(embed=Errors.not_int("page"))

        else:
            # If page = None, set it to 1
            page = 1

        #* Make embed head
        embed = discord.Embed(
            title=f"In osu!{variables.mode2strfull[int(mode)]}",
            color=ctx.author.color
        )
        embed.set_thumbnail(url=f"https://a.{settings.DOMAIN}/{user['id']}")

        #! Basic page embed
        if size == "basic":
            # In this case page number must be between 1 and 20
            if page < 1 or page > 20:
                return await ctx.send(embed=Errors.number_range(1, 20))
            offset = (page-1)*5
            # scores/page = 5
            limit = 5

            #* Get scores
            scores = await app.state.services.database.fetch_all(
                "SELECT s.id scoreid, s.score, s.pp, s.acc, s.max_combo score_max_combo, "
                "s.mods, s.n300, s.n100, s.n50, s.nmiss, s.ngeki, s.nkatu, s.grade, "
                "s.play_time, m.artist, m.title, m.version, m.creator, m.diff, m.id, m.max_combo "
                "FROM scores s LEFT JOIN maps m ON s.map_md5 = m.md5 "
                "WHERE s.userid=:id AND s.status=2 AND m.status in (2,3) AND s.mode=:mode "
                "ORDER BY s.pp DESC LIMIT :limit OFFSET :offset",
                {"id": user['id'], "mode": mode, "offset": offset, "limit": limit}
            )
            # No scores found
            if not scores:
                return await ctx.send(embed=Errors.noScores(variables.mode2strfull[int(mode)]))

            # Convert to dicts
            scores = [dict(score) for score in scores]

            embed.set_author(
                name=f"{user['name']}'s #{offset+1}-#{offset+5} Best scores in osu!{variables.mode2strfull[int(mode)]}",
                icon_url=f"https://{settings.DOMAIN}/static/images/flags/{user['country'].upper()}.png",
                url=f"https://{settings.DOMAIN}/u/{user['id']}/{mode}"
            )

            #* Iterate over scores
            for i in range (5):
                el:dict = scores[i]

                # Mania is specific gamemode :trolley:
                if mode == 3:
                    try:
                        ratio = f" ▸ {round(el['ngeki']/el['n300'], 3)} **: 1**"
                    except ZeroDivisionError:
                        ratio = " ▸ 0 **: 1**"
                    max_combo = f"▸ {el['score_max_combo']}x"
                else:
                    ratio = ""
                    max_combo = f"▸ {el['score_max_combo']}x/**{el['max_combo']}x**"

                judgements = " ▸ {}".format(
                    utils.formatJudgements(
                        mode, el['n300'], el['n100'], el['n50'], el['nmiss'], el['nkatu'], el['ngeki']
                ))

                #* Add score to embed
                embed.add_field(
                    name=f"{i+1+offset}. {el['artist']} - {el['title']} [{el['version']}] {utils.mods2str(el['mods'])}",
                    value=f"[Score link](https://{settings.DOMAIN}/score/{el['scoreid']})\n"
                    f"▸ {variables.grade2emoji[el['grade']]} ▸ **Score:** {el['score']:,} ▸ **PP**: {round(el['pp'], 2)} ▸ **ACC**: {round(el['acc'], 2)}%\n"
                    f"{max_combo}{judgements}{ratio}\n",
                    inline=False
                )

        #! Full size embed
        elif size == "full":
            # In this case page number must be between 1 and 100
            if page < 1 or page > 100:
                return await ctx.send(embed=Errors.number_range(1, 100))
            offset = page-1
            # scores/page = 1
            limit = 1

            #* Get score
            score = await app.state.services.database.fetch_one(
                "SELECT s.id scoreid, s.score, s.pp, s.acc, s.max_combo score_max_combo, "
                "s.mods, s.n300, s.n100, s.n50, s.nmiss, s.ngeki, s.nkatu, s.grade, "
                "s.play_time, m.artist, m.title, m.version, m.creator, m.diff, m.id, "
                "m.max_combo, m.hp, m.od, m.cs, m.ar, m.bpm, m.diff, m.total_length "
                "FROM scores s LEFT JOIN maps m ON s.map_md5 = m.md5 "
                "WHERE s.userid=:id AND s.status=2 AND m.status in (2,3) AND s.mode=:mode "
                "ORDER BY s.pp DESC LIMIT 1 OFFSET :offset",
                {"id": user['id'], "mode": mode, "offset": offset}
            )
            # No scores found
            if not score:
                return await ctx.send(embed=Errors.noScores(variables.mode2strfull[int(mode)]))
            else:
                score = dict(score)

            if mode == 3:
                max_combo = f"▸ {score['score_max_combo']}x"
                map_stats  = f"▸ **Keys:** {int(score['cs'])} ▸ **HP:** {score['hp']} ▸ **OD:** {score['od']}"
                try:
                    ratio = f" ▸ {round(score['ngeki']/score['n300'], 3)} **: 1**"
                except ZeroDivisionError:
                    ratio = " ▸ 0 **: 1**"
            else:
                max_combo = f"▸ {score['score_max_combo']}x/**{score['max_combo']}x**"
                ratio = ""
                if int(mode) in (0,4,8):
                    map_stats = f"▸ **HP:** {score['hp']} ▸ **AR:** {score['ar']} ▸ **CS:** {score['cs']} ▸ **OD:** {score['od']}"
                elif int(mode) in (1,5):
                    map_stats  = f"▸ **HP:** {score['hp']} ▸ **OD:** {score['od']}"
                elif int(mode) in (2,6):
                    map_stats = f"▸ **HP:** {score['hp']} ▸ **AR:** {score['ar']} ▸ **CS:** {score['cs']} ▸ **OD:** {score['od']}"

            embed.set_author(
                name=f"{user['name']}'s #{offset+1} Best score.",
                icon_url=f"https://{settings.DOMAIN}/static/images/flags/{user['country'].upper()}.png",
                url=f"https://{settings.DOMAIN}/u/{user['id']}/{mode}"
            )
            embed.add_field(
                name=f"{score['artist']} - {score['title']} [{score['version']}] {utils.mods2str(score['mods'])}",
                value=f"[Score link](https://{settings.DOMAIN}/score/{score['scoreid']})\n"
            )
            embed.add_field(
                name="Score Info",
                value=f"▸ {variables.grade2emoji[score['grade']]} ▸ **PP**: {round(score['pp'], 2)} ▸ **ACC**: {round(score['acc'], 2)}%\n"
                f"▸ **Score:** {score['score']:,} ▸ **Combo:** {max_combo}\n"
                f"▸ {utils.formatJudgements(mode, score['n300'], score['n100'], score['n50'], score['nmiss'], score['nkatu'], score['ngeki'])}"
                f" ▸ **Ratio:** {ratio}"
                f"\n▸ **Date Played:** <t:{int(datetime.datetime.timestamp(score['play_time']))}:R>",
                inline=False
            )
            embed.add_field(
                name="Map Info",
                value=f"{map_stats}\n▸ **Stars** {round(score['diff'], 2)} ⭐ ▸ **BPM:** {int(round(score['bpm'], 0))} ▸ "
                f"**Length:** {score['total_length']}",
                inline=False
            )

        embed.set_footer(
            text=await utils.formatStatus(user['name'], user['latest_activity']),
            icon_url=config.ICON_LINK
        )


        return await ctx.send(embed=embed)
def setup(bot: commands.Bot):
    bot.add_cog(Best(bot))
