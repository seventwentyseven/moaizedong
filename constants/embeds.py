from discord import Embed

class Errors:
    # Class for calling error embeds
    # above class is only used for organization
    # and it's not an object

    @staticmethod
    def no_user_found() -> Embed:
        # Returns an embed for when a user is not found
        embed = Embed(
            title="User not found",
            description="The user you entered was not found. Please try again.",
            color=0xFF0000,
        )
        return embed
