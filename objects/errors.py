from __future__ import annotations

import discord

from moai.constants.colors import Colors
from moai.botconfig import SERVER_NAME_L, SERVER_NAME_S, ICON_LINK
from moai.constants.channels import Channels

__all__ = ('Errors')

class Errors:
    """Class representing errors of the bot."""

    #* Default error
    def default(text:str) -> discord.Embed:
        embed = discord.Embed(
            title="Error!",
            description=text,
            color=Colors.RED
        )
        embed.set_footer(
            text=f"{SERVER_NAME_L}.xyz",
            icon_url=ICON_LINK
        )
        return embed
    # Missing privileges error
    def privileges() -> discord.Embed:
        embed =  discord.Embed(
            title="Error!",
            description="You don't have permissions to use this command, maybe your account isn't linked?.",
            color=Colors.RED
        )
        embed.set_footer(
            text=f"{SERVER_NAME_L}.xyz",
            icon_url=ICON_LINK
        )

    def user_not_found(self_exec:bool=False, short:bool=False) -> discord.Embed:
        if short==True:
            embed = discord.Embed(
                title="Error!",
                description=f"User not found.",
                color=Colors.RED
            )
        elif self_exec==True:
            embed = discord.Embed(
                title="Error!",
                description=f"You don't have a {SERVER_NAME_S} account linked to your discord account yet.\n"
                             "You can do that on our website in settings page, or just use your name in command.",
                color=Colors.RED
            )
        else:
            embed = discord.Embed(
                title="Error!",
                description=f"User not found, maybe their account isn't linked?",
                color=Colors.RED
            )

        # Set footer
        embed.set_footer(
            text=f"{SERVER_NAME_L}.xyz",
            icon_url=ICON_LINK
        )
        return embed

    def AdminChat_only() -> discord.Embed:
        embed = discord.Embed(
            title="Error!",
            description=f"Try again in <#{Channels.ADMIN_CHAT}>.",
            color=Colors.RED
        )
        embed.set_footer(
            text=f"{SERVER_NAME_L}.xyz",
            icon_url=ICON_LINK
        )
        return embed

    def noScores(mode:str):
        embed = discord.Embed(
            title="Error!",
            description=f"No scores found in osu!{mode}.",
            color=Colors.RED
        )
        embed.set_footer(
            text=f"{SERVER_NAME_L}.xyz",
            icon_url=ICON_LINK
        )
        return embed

    def number_range(min:int, max:int) -> discord.Embed:
        if min == None:
            text=f"Number must be under {max}."
        elif max == None:
            text=f"Number must be over {min}."
        elif min == None and max == None:
            raise ValueError("min and max cannot be both None")
        else:
            text=f"Number must be between {min} and {max}."

        embed = discord.Embed(
            title="Error!",
            description=text,
            color=Colors.RED
        )
        embed.set_footer(
            text=f"{SERVER_NAME_L}.xyz",
            icon_url=ICON_LINK
        )
        return embed

    def not_int(arg_name:str) -> discord.Embed:
        embed = discord.Embed(
            title="Error!",
            description=f"`{arg_name}` argument must be an integer.",
            color=Colors.RED
        )
        embed.set_footer(
            text=f"{SERVER_NAME_L}.xyz",
            icon_url=ICON_LINK
        )
        return embed

    def notLinked() -> discord.Embed:
        """If user account is not linked"""
        embed = discord.Embed(
            title="Error!",
            description=f"Your account is not linked to {SERVER_NAME_S} yet.\n"
                         "You can do that on our website in settings page.",
            color=Colors.RED
        )
        embed.set_footer(
            text=f"{SERVER_NAME_L}.xyz",
            icon_url=ICON_LINK
        )
        return embed




