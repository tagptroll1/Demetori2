import discord
from discord.ext import commands

class Everyone:
    """Cogs for everyone to use"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        param = {"title": "A Black desert online discord bot",
                 "description": """
Used for announcing nodewars, storing members gear, 
tracking absence from nodewars and other fun commands
for everyone to use!""",
                 "url":"https://www.github.com/tagptroll1/demetori2",
                 "color": discord.Color.blue(),
                 }
        embed = discord.Embed(**param)
        embed.set_footer(text="Not to be distributed without permission",
                         icon_url="https://cdn.discordapp.com/emojis/437440834150072331.png?v=1")
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_author(name="Created by Chibli#0001", url="https://www.github.com/tagptroll1",
                         icon_url="http://www.icons101.com/icons/92/Custom_Round_Yosemite_Icons_by_Paulo_Ruberto/128/FileBot.png")
        embed.add_field(name="Don't forget to use the ?help command", value="\u200b")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Everyone(bot))
