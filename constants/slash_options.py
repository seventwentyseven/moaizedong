from __future__ import annotations

from discord_slash.utils.manage_commands import create_choice, create_option

__all__ = ("CommandOptions")

class CommandOptions:
    """Class for managing command options."""

    PROFILE = [
        create_option(
            name="user",
            description="Select user.",
            option_type=3,
            required=False,
        ),
        create_option(
            name="mode",
            description="Select mode.",
            option_type=3,
            required=False,
            choices=[
                create_choice(name="Standard", value="0"),
                create_choice(name="Taiko", value="1"),
                create_choice(name="Catch", value="2"),
                create_choice(name="Mania", value="3"),
                create_choice(name="Standard + RX", value="4"),
                create_choice(name="Taiko + RX", value="5"),
                create_choice(name="Catch + RX", value="6"),
                create_choice(name="Standard + AP", value="8"),
            ]
        ),
        create_option(
            name="size",
            description="Do you want to see all info or only basic",
            option_type=3,
            required=False,
            choices=[
                create_choice(name="Basic", value="basic"),
                create_choice(name="Full", value="full"),
            ]
        ),
    ]
