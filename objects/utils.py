from __future__ import annotations
from time import time

import discord
from discord.ext import commands

import datetime
import timeago

import app.state.services
import app.state.sessions
from app import settings
from app.constants.mods import Mods
from app.constants.privileges import Privileges
from app.objects.player import Player

import moai.botconfig as config
from moai.constants.colors import Colors
from moai.constants import variables
from moai.objects.errors import Errors

async def get_user(ctx: commands.Context, user:str=None):
    # Define default self_exec
    self_exec = False

    # If user wasn't specified
    if not user:
        self_exec = True
        user = await app.state.services.database.fetch_one(
            "SELECT id, name, priv, country, discord_id, "
            "creation_time, latest_activity, preferred_mode "
            "FROM users WHERE discord_id = :id",
            {"id": ctx.author.id}
        )
        if not user:
            return {"error": True, 'embed': await Errors.user_not_found(self_exec=self_exec)}
        else:
            return {"user": dict(user), "self_exec": self_exec}
    # User was mentioned
    elif user.startswith("<@!") and user.endswith(">"):
        user = int(user[3:-1])
        if user == ctx.author.id:
            self_exec = True
        user = await app.state.services.database.fetch_one(
            "SELECT id, name, priv, country, discord_id, "
            "creation_time, latest_activity, preferred_mode "
            "FROM users WHERE discord_id = :id",
            {"id": user}
        )
        if not user:
            return {"error": True, 'embed': await Errors.user_not_found(self_exec=self_exec)}
        else:
            return {"user": dict(user), "self_exec": self_exec}
    # User arg is username (str)
    else:
        user = await app.state.services.database.fetch_one(
            "SELECT id, name, priv, country, discord_id, "
            "creation_time, latest_activity, preferred_mode "
            "FROM users WHERE name = :name",
            {"name": user}
        )
        if not user:
            return {"error": True, 'embed': await Errors.user_not_found(self_exec=False)}
        else:
            user = dict(user)
            if user['discord_id'] == ctx.author.id:
                self_exec = True
            return {"user": user, "self_exec": self_exec}

async def priv2str(priv:int, formatter:str="", separator:str=" "):
    """Convert privilege integer to string."""

    f = formatter
    s = separator
    out = ""
    priv_list = [
        el.name.capitalize() for el in Privileges if priv & el and bin(el).count("1") == 1
    ][::-1]
    for el in priv_list:
        out += f"{f}{el}{f}{s}"

    return out[:-len(s)]

async def formatStatus(username:str, last_seen:int):
    """Format player status."""

    #* Check if player is online
    player: Player = app.state.sessions.players.get(name=username)

    #* Player is not online
    if not player:
        return "{} is 🔴 Offline, last seen {}.".format(
            username, timeago.format(last_seen, datetime.datetime.utcnow())
        )
    #* Player is online
    else:
        text = variables.statuses[player.status.action.value]

        mods = f" +{Mods(player.status.mods)!r}" if player.status.mods else ""
        if "NC" in mods:
            mods = mods.replace("DT", "")

        return "{} is 🟢 Online at {} | {}".format(
            player.name,
            config.SERVER_NAME_S,
            text.format(player.status.info_text, mods)
        )


