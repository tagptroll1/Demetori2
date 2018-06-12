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

    @commands.command()
    @commands.guild_only()
    @commands.has_role("Officer")
    async def kick(self, ctx, member:discord.Member, reason=None):
        try:
            await ctx.guild.kick(member, reason=reason)
        except discord.Forbidden:
            await ctx.send(f"I do not have permissions to kick {member.name}")
        except discord.HTTPException as e:
            await ctx.send(f"Something went wrong trying to kick {member.name}")
            await ctx.send(f"```{e}```")
        else:
            await ctx.send(f"{member.name} has been succesfully kicked.")

    @commands.command()
    @commands.guild_only()
    @commands.has_role("Officer")
    async def ban(self, ctx, member: discord.Member, reason=None):
        try:
            await ctx.guild.ban(member, reason=reason)
        except discord.Forbidden:
            await ctx.send(f"I do not have permissions to ban {member.name}")
        except discord.HTTPException as e:
            await ctx.send(f"Something went wrong trying to ban {member.name}")
            await ctx.send(f"```{e}```")
        else:
            await ctx.send(f"{member.name} has been succesfully banned.")

    @commands.command()
    @commands.guild_only()
    @commands.has_role("Officer")
    async def banlist(self, ctx):
        ban_list = await ctx.guild.bans()

        msg = ",\n".join(f"{x.user}; banned for \"{x.reason}\"" for x in ban_list)
        await ctx.send(msg)

    @commands.command()
    @commands.guild_only()
    @commands.has_role("Officer")
    async def unban(self, ctx, member:discord.User):
        try:
            await ctx.guild.unban(member)
        except discord.Forbidden:
            await ctx.send(f"I do not have permissions to unban {member.name}")
        except discord.HTTPException as e:
            await ctx.send(f"Something went wrong unbanning {member.name}")
            await ctx.send(f"```{e}```")
        else:
            await ctx.send(f"{member.name} has been unbanned!")


    async def create_role(self, ctx, **role_param):
        """Utility method to create a role"""
        try:
            await ctx.guild.add_roles(reason="Created by Demetori bot", **role_param)
        except discord.Forbidden:
            await ctx.send("I do not have permission to create this mission role, aborting job.")
            return
        except discord.HTTPException as e:
            await ctx.send("Something went wrong.. aborting job.  (Feel free to try again)")
            await ctx.send(f"```{e}```")
        else:
            await ctx.send(f"There was no role named {role_param['name']} here, but I made it for you! :)")

    async def add_role_member(self, ctx, member, role):
        """Utility method to add a role to a member"""
        try:
            await member.add_roles(role)
        except discord.Forbidden:
            await ctx.send("I do not have permissions to add this role")
        except discord.HTTPException as e:
            await ctx.send("An error occurred while pruning members")
            await ctx.send(f"```{e}```")
        else:
            await ctx.send(f"Added {role.name} role to {member.display_name}")

    @commands.command()
    @commands.guild_only()
    @commands.has_role("Officer")
    async def trial(self, ctx, member:discord.Member):
        trial_role = discord.utils.get(ctx.guild.roles, name="Trial")
        if not trial_role:
            role_param = {
                "name": "Trial",
                "color": 0x25d678,
                "mentionable": True
            }
            await self.create_role(ctx, **role_param)

        trial_role = discord.utils.get(ctx.guild.roles, name="Trial")
        await self.add_role_member(ctx, member, trial_role)

    @commands.command()
    @commands.guild_only()
    @commands.has_role("Officer")
    async def arena(self, ctx, member: discord.Member):
        arena_role = discord.utils.get(
            ctx.guild.roles, name="Awaiting arena trial")
        if not arena_role:
            role_param = {
                "name": "Awaiting arena trial",
                "color": 0x8495a5,
                "mentionable": True
            }
            await self.create_role(ctx, **role_param)

        arena_role = discord.utils.get(
            ctx.guild.roles, name="Awaiting arena trial")
        await self.add_role_member(ctx, member, arena_role)

    @commands.command()
    @commands.guild_only()
    @commands.has_role("Officer")
    async def member(self, ctx, member: discord.Member):
        member_role = discord.utils.get(
            ctx.guild.roles, name="Member")
        if not member_role:
            role_param = {
                "name": "Member",
                "color": 0x4c9ad6,
                "mentionable": True
            }
            await self.create_role(ctx, **role_param)

        member_role = discord.utils.get(
            ctx.guild.roles, name="Member")
        await self.add_role_member(ctx, member, member_role)

        trial_role = discord.utils.get(ctx.guild.roles, name="Trial") 
        arena_role = discord.utils.get(ctx.guild.roles, name="Awaiting arena trial")
        await member.remove_roles(*[trial_role, arena_role])
    #
    @commands.command()
    @commands.guild_only()
    @commands.has_role("Officer")
    async def estimate_prune(self, ctx, days:int):
        estimated = await ctx.guild.estimate_pruned_members(days=days)
        await ctx.send(f"The amount of users whos been inactive for {days} days, without any roles are {estimated}")

    @commands.command()
    @commands.guild_only()
    @commands.has_role("Officer")
    async def prune_inacitve(self, ctx, days: int):
        await ctx.send("Are you sure? (\"yes\", \"no\")")

        def check(m):
            if m.author is not ctx.author:
                return False
            return m.content.lower() in ("yes", "y", "ye", "no", "n")

        try:
            msg = self.bot.wait_for("message", check=check, timeout=20)
        except asyncio.TimeoutError:
            return
        
        if msg.content in ("yes", "y", "ye"):
            try:
                kicked = await ctx.guild.prune_inacitve(days)
            except discord.Forbidden:
                await ctx.send("Bot does not have permission to kick!")
            except discord.HTTPException as e:
                await ctx.send("An error occurred while pruning members")
                await ctx.send(f"```{e}```")
            else:
                await ctx.send(f"Users inactive for the last {days} days and without any roles has been kicked. Count: {kicked}")

def setup(bot):
    bot.add_cog(Officer(bot))
