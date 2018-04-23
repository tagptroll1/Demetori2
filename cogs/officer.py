import discord
from discord.ext import commands


class Officer:
    """Cog for officer related commands"""

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Officer(bot))
