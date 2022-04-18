from app.constants.gamemodes import GameMode

mode2strfull = {
    0: "Standard",
    1: "Taiko",
    2: "Catch",
    3: "Mania",
    4: "Standard + RX",
    5: "Taiko + RX",
    6: "Catch + RX",
    8: "Standard + AP",
}

mode2obj = {
    0: GameMode.VANILLA_OSU,
    1: GameMode.VANILLA_TAIKO,
    2: GameMode.VANILLA_CATCH,
    3: GameMode.VANILLA_MANIA,

    4: GameMode.RELAX_OSU,
    5: GameMode.RELAX_TAIKO,
    6: GameMode.RELAX_CATCH,
    7: GameMode.RELAX_MANIA, # unused

    8: GameMode.AUTOPILOT_OSU,
    9: GameMode.AUTOPILOT_TAIKO, # unused
    10: GameMode.AUTOPILOT_CATCH, # unused
    11: GameMode.AUTOPILOT_MANIA, # unused
}

statuses = {
    0: 'Idle: 🔍 Song Select',
    1: '🌙 AFK',
    2: 'Playing: 🎶 {info_text} +MODS',
    3: 'Editing: 🔨 {info_text}',
    4: 'Modding: 🔨 {info_text}',
    5: 'In Multiplayer: Song Select',
    6: 'Watching: 👓 {info_text}',
    # 7 not used
    8: 'Testing: 🎾 {info_text}',
    9: 'Submitting: 🧼 {info_text}',
    # 10 paused, never used
    11: 'Idle: 🏢 In multiplayer lobby',
    12: 'In Multiplayer: Playing 🌍 {info_text} 🎶',
    13: 'Idle: 🔍 Searching for beatmaps in osu!direct'
}