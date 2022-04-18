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