from __future__ import annotations

import discord
from moai.constants.colors import Colors

__all__ = ("Embeds")

class Embeds():
    def __init__(self, bot):
        self.bot = bot
    
    def error(self, message, error):
        embed = discord.Embed(title="Error", description=error, color=0xFF0000)
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        embed.set_footer(text="Moai")
        return embed
