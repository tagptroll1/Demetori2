import aiohttp
import asyncio
import json

import discord
from discord.ext import commands


class Twitch():
    def __init__(self, bot):
        self.bot = bot
        self.twitch_data = self.get_twitch_data()

    def get_twitch_data(self):
        with open("twitch.json") as data:
            return json.load(data)

    async def get_channel_json(self, nick):
        params = {
            "client_id":self.twitch_data["client_id"]
        }
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.twitch.tv/kraken/channels/{nick}", params=params) as r:
                return await r.json()

        # Desired result to fetch
        # https://api.twitch.tv/kraken/channels/CHANNEL_NAME?client_id=CLIENTS_ID

    @commands.command()
    async def shoutout(self, ctx, nick):
        data = await self.get_channel_json(nick)
        if data.get("error"):
            await ctx.send(f"{data['status']}: {data['error']}")
        nick = data["display_name"]

        embed = discord.Embed(colour=discord.Colour.purple())
        embed.title = f"Please make sure to follow and subscribe to {nick}!"
        embed.description = f"Description about {nick}s twitch channel!"
        embed.url = data["url"]
        embed.add_field(name="Last observed title",value=data["status"])
        embed.add_field(name="Last observed game", value=data["game"])
        embed.add_field(name="Followers", value=str(data["followers"]))
        embed.add_field(name="Total views", value=str(data["views"]))
        embed.set_thumbnail(url=data["logo"])

        embed.set_footer(text=f"{nick} joined twitch at {data['created_at']}")

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Twitch(bot))


