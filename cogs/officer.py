import discord
from discord.ext import commands
import asyncio

class Officer:
    """Cog for officer related commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_role("Officer")
    async def announce(self, ctx, *, text):
        """Creates a sleek looking embed for announcements"""
        await ctx.message.delete()
        embed = discord.Embed(title="Announcement")
        embed.description = text
        embed.colour = discord.Colour.red()
        await ctx.send(embed=embed)

    @announce.group(name="green", invoke_without_command=True)
    @commands.guild_only()
    @commands.has_role("Officer")
    async def green_announce(self, ctx, *, text):
        """Creates a sleek looking embed for announcements, THATS GREEN!"""
        await ctx.message.delete()
        embed = discord.Embed(title="Announcement")
        embed.description = text
        embed.colour = discord.Colour.green()
        await ctx.send(embed=embed)

    @green_announce.command(name="title")
    @commands.guild_only()
    @commands.has_role("Officer")
    async def green_announce_title(self, ctx, *, text):
        """Creates a sleek looking embed for announcements, THATS GREEN! with custom title"""
        await ctx.message.delete()
        await ctx.send("Respond with a title for the announcement! *(15 sec time)*", delete_after=15)

        def pred(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for("message", check=pred, timeout=15.0)
        except asyncio.TimeoutError:
            await ctx.send("Using default title...", delete_after=5)
            title = "Announcement"
        else:
            title = msg.content
        await msg.delete()

        embed = discord.Embed(title=title)
        embed.description = text
        embed.colour = discord.Colour.green()
        await ctx.send(embed=embed)

    @announce.command(name="title")
    @commands.guild_only()
    @commands.has_role("Officer")
    async def announce_title(self, ctx, *, text):
        """Creates a sleek looking embed for announcements, THATS GREEN! with custom title"""
        await ctx.message.delete()
        await ctx.send("Respond with a title for the announcement! *(15 sec time)*", delete_after=15)

        def pred(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for("message", check=pred, timeout=15.0)
        except asyncio.TimeoutError:
            await ctx.send("Using default title...", delete_after=5)
            title = "Announcement"
        else:
            title = msg.content
        await msg.delete()

        embed = discord.Embed(title=title)
        embed.description = text
        embed.colour = discord.Colour.red()
        await ctx.send(embed=embed)

    @commands.command(hidden=False)
    @commands.guild_only()
    @commands.has_role("Officer")
    async def msg_all(self, ctx, *, message):
        """Sends a message to every member that is NOT excused"""
        guild_members = ctx.guild.members

        for member in guild_members:
            if not discord.utils.get(ctx.guild.roles, name="Excused"):
                try:
                    await member.send(message)
                except Exception:
                    await ctx.send(f"{member} has blocked the bot!")

    @commands.command(aliases=["msg"], hidden=False)
    @commands.guild_only()
    @commands.has_role("Officer")
    async def msg_member(self, ctx, *, users:discord.Member):
        """Msg one or multiple members, do ?msg [list of members seperated by a space], 
        wait for the bot to respond then give a message to send"""

        await ctx.send("Respond with a message to send to these users")

        def pred(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel

        msg = await self.bot.wait_for('message', check=pred)
        msg = msg.content

        for user in users:
            try:
                await user.send(msg)
            except Exception:
                await ctx.send(f"{user.display_name} has blocked the bot")

    @commands.group(invoke_without_command=True)
    @commands.has_role("Officer")
    async def clear(self, ctx, number:int):
        """Deletes x amount of messages"""
        async with ctx.channel.typing():
            async for message in ctx.channel.history(limit=number):
                await message.delete()
        await ctx.send("Done!", delete_after=5)

    @clear.command(name="all")
    @commands.has_role("Officer")
    async def clear_all(self, ctx):
        """Deletes all messages in a channel (up to 1000)"""
        async with ctx.channel.typing():
            async for message in ctx.channel.history(limit=1000):
                await message.delete()
        await ctx.send("Done!", delete_after=5)

    @clear.command(name="notpinned")
    @commands.has_role("Officer")
    async def clear_notpinned(self, ctx):
        async with ctx.channel.typing():
            async for message in ctx.channel.history(limit=1000):
                if not message.pinned:
                    await message.delete()
        await ctx.send("Done!", delete_after=5)

    @clear.command(name="except")
    @commands.has_role("Officer")
    async def clear_except(self, ctx, *members:discord.Member):
        async with ctx.channel.typing():
            async for message in ctx.channel.history(limit=1000):
                if message.author not in members:
                    await message.delete()
        await ctx.send("Done!", delete_after=5)

    @clear.command(name="only")
    @commands.has_role("Officer")
    async def clear_only(self, ctx, *members:discord.Member):
        async with ctx.channel.typing():
            async for message in ctx.channel.history(limit=1000):
                if message.author in members:
                    await message.delete()
        await ctx.send("Done!", delete_after=5)

    @commands.command(hidden=False, name="optin")
    @commands.guild_only()
    @commands.has_role("Officer")
    async def opt_in(self, ctx):
        opt_in = discord.utils.get(ctx.guild.roles, name="Opt-in")
        if not opt_in:
            opt_in = await ctx.guild.create_role(name="Opt-in")

        if not discord.utils.get(ctx.author.roles, name="Opt-in"):
            await ctx.author.add_roles(opt_in)
            await ctx.send("You've opted in for absence pings")

def setup(bot):
    bot.add_cog(Officer(bot))
