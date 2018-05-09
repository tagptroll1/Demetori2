from textwrap import dedent

import discord
from discord.ext import commands
import psutil
import aiohttp
import random


class Everyone:
    """Cog for everyone to use"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def dornier(self, ctx):
        await ctx.send("This does nothing")

    @commands.guild_only()
    @commands.group(invoke_without_command=True, case_insensitive=True)
    async def info(self, ctx):
        param = {"title": "A Black desert online discord bot",
                 "description": dedent("""
                    Used for announcing nodewars, storing members gear, 
                    tracking absence from nodewars and other fun commands
                    for everyone to use!"""),
                 "url": "https://www.github.com/tagptroll1/demetori2",
                 "color": discord.Color.blue(),
                 }

        data = {
            "membercount": len(set(self.bot.get_all_members())),
            "guildcount": len(self.bot.guilds),
            "commandscount": len(self.bot.commands),
            "emojicount": len(self.bot.emojis),
            "cpupercent": psutil.cpu_percent(interval=1),
            "cpucount": psutil.cpu_count(),
            "memorypercent": psutil.virtual_memory().percent
        }
        embed = discord.Embed(**param)
        embed.set_footer(text="Not to be distributed without permission",
                         icon_url="https://cdn.discordapp.com/emojis/437440834150072331.png?v=1")
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_author(name="Created by Chibli#0001", url="https://www.github.com/tagptroll1",
                         icon_url="http://www.icons101.com/icons/92/Custom_Round_Yosemite_Icons_by_Paulo_Ruberto/128/FileBot.png")
        embed.add_field(
            name="__CPU__", value=f"Usage: **{data['cpupercent']:.0f}%**\nCores: **{data['cpucount']}**", inline=True)
        embed.add_field(
            name="__Memory__", value=f"Usage: **{data['memorypercent']:.0f}%**", inline=True)
        embed.add_field(
            name="__Bot info__", value=f"Total members: **{data['membercount']}**\nTotal servers: **{data['guildcount']}**"
            f"\nTotal commands: **{data['commandscount']}**\nTotal emojis: **{data['emojicount']}**", inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name="Donate to keep the bot updated, and live! ᵖˡᵉᵃˢᵉ",
                        value="[Paypal.me](https://paypal.me/tagptroll1)", inline=False)
        await ctx.send(embed=embed)

# TODO Add sub commands for info to get info on member and roles
# for member:
# - joined at
# - created at
# - roles
# - id
# - avatar usually as thumbnail

# for role:
# - colour
# - created at
# - id

    @commands.guild_only()
    @commands.group(invoke_without_command=True)
    async def meme(self, ctx):
        pass

    @commands.guild_only()
    @meme.command(name="chucknorris", aliases=["chuck", "chuck_norris"])
    async def chuck_norris(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://api.chucknorris.io/jokes/random") as r:
                res = await r.json()
                embed = discord.Embed(title="Chuck Norris facts")
                embed.description = res["value"]
                embed.set_thumbnail(url=res["icon_url"])
                embed.url = res["url"]

                await ctx.send(embed=embed)

    @commands.guild_only()
    @meme.command(name="ronswanson", aliases=["ron", "ron_swanson"])
    async def ron_swanson(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://ron-swanson-quotes.herokuapp.com/v2/quotes") as r:
                res = await r.json()
                embed = discord.Embed(title="Ron Swanson quotes")
                embed.description = res[0]
                embed.set_thumbnail(
                    url="http://data.junkee.com/wp-content/uploads/2016/10/Ron-Swanson.jpg")

                await ctx.send(embed=embed)

    @commands.guild_only()
    @meme.command(name="xkcd")
    async def xkcd_meme(self, ctx):
        xkcdid = random.randint(1, 1900)
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://xkcd.com/{xkcdid}/info.0.json") as r:
                res = await r.json()
                embed = discord.Embed(title="XKCD Cartoons")
                embed.description = res["title"]
                embed.set_image(url=res["img"])

                await ctx.send(embed=embed)


    @commands.guild_only()
    @commands.command()
    async def say(self, ctx, *, msg):
        await ctx.message.delete()
        await ctx.send(msg)

    @commands.guild_only()
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

    @commands.guild_only()
    @commands.command()
    async def pong(self, ctx):
        await ctx.send("Ping!")

def setup(bot):
    bot.add_cog(Everyone(bot))
