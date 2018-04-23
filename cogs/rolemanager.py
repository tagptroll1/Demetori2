import discord
from discord.ext import commands


class RoleManager:
    """Cog for role management related commands"""
    
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(RoleManager(bot))
