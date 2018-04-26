import discord
from discord.ext import commands
import asyncio
import asyncpg
import datetime

class Database:
    """Cog for handling database related commands"""
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.has_role("Officer")
    async def clear_absence(self, ctx, member:discord.Member=None):
        """Give it a user to clear all his absence, or no user to clear everything"""
        if member:
            query = f"DELETE FROM absence WHERE userid = {member.id}"
        else:
            query = "DELETE FROM absence"
        connection = await self.bot.db.acquire()
        async with connection.transaction():
            await connection.execute(query)
        
        if member:
            await ctx.send(f"Deleted all absence from {member.display_name}")
        else:
            await ctx.send("Deleted all absence from database")
        await self.bot.db.release(connection)

    @commands.group(invoke_without_command=True, case_insensitive=True)
    async def insert(self, ctx):
        pass

    @commands.command(name="absence")
    @commands.has_role("Member")
    async def insert_absence(self, ctx, *,reason):
        """Add an absence to the data base with your ID, reason and timestamp"""

        today = datetime.datetime.today().strftime("%d/%m")
        query = "INSERT INTO absence(userid, excuse) VALUES ($1, $2);"
        connection = await self.bot.db.acquire()
        async with connection.transaction():
            await connection.execute(query, ctx.author.id, f"{today} : {reason}")
        await ctx.author.send("Your absence has been registered! Don't forget to message an officer about it")
        await self.bot.db.release(connection)

    @commands.group(invoke_without_command=True, case_insensitive=True)
    @commands.has_role("Member")
    async def update(self, ctx):
        pass

    @update.command(name="gear")
    @commands.has_role("Member")
    async def update_gear(self, ctx, member: discord.Member, ap: int, aap: int, dp: int, level: int, c_class, url=None):
        """Required: @Member, Ap, AAP, DP, Level, Class
        Optional: Url for gear pic"""
        if ap < 100 or ap > 300:
            await ctx.send(f"Not a valid AP: {ap}")
            return

        if aap < 100 or aap > 300:
            await ctx.send(f"Not a valid AAP: {aap}")
            return

        if dp < 100 or dp > 500:
            await ctx.send(f"Not a valid DP: {dp}")
            return

        if level < 56 or level > 63:
            await ctx.send(f"Not a valid Level: {level}")
            return
        classes = ("Warrior", "Ranger", "Sorceress", "Berserker", "Valkyrie", "Wizard", "Witch",
                    "Tamer", "Maehwa", "Musa", "Ninja", "Kunoichi", "Darkknight", "Striker", "Mystic")
        if c_class.title() not in classes:
            await ctx.send(f"Not a valid class, list over valid classes are:\n{classes}")
            return

        query = "SELECT * FROM members WHERE id = $1;"
        if await self.bot.db.fetchrow(query, member.id):
            update = """UPDATE members 
            SET ap = $1, aap = $2, dp = $3, level = $4, class = $5, gearpic = $6
            WHERE id = $7;"""
            await self.bot.db.execute(update, ap, aap, dp, level, c_class, url, member.id)
            await ctx.send(f"{member.display_name} was updated in the database!")
        else:
            insert = """INSERT INTO members(id, guild_id, ap, aap, dp, level, class, gearpic)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8);"""
            connection = await self.bot.db.acquire()
            async with connection.transaction():
                await connection.execute(insert, member.id, ctx.guild.id, ap, aap, dp, level, c_class.title(), url)
            await ctx.send(f"{member.display_name} was added to the database!")
            await self.bot.db.release(connection)

    @commands.group(invoke_without_command=True, case_insensitive=True)
    @commands.has_role("Member")
    async def get(self, ctx):
        pass

    @get.group(name="member")
    @commands.has_role("Officer")
    async def get_user(self, ctx, member:discord.Member=None):
        query = "SELECT * FROM absence WHERE userid = $1;"
        if not member:
            member = ctx.author
        fetched = await self.bot.db.fetch(query, member.id)
        absence_list = ""
        for row in fetched:
            absence_list += f"{row['excuse'][5:]} - {member.display_name} {row['excuse'][5:]}\n"
        absenceembed = discord.Embed()
        absenceembed.set_author(name=member.display_name, icon_url=member.avatar_url)
        absenceembed.description = absence_list
        await ctx.author.send(embed=absenceembed)

    @get.group(name="all")
    @commands.has_role("Officer")
    async def get_all(self, ctx):
        query = "SELECT * FROM absence ORDER BY userid, excuse"
        fetched = await self.bot.db.fetch(query)
        absence_list = ""
        for row in fetched:
            member = discord.utils.get(ctx.guild.members, id=row["userid"])
            absence_list += f"{row['excuse'][:5]} - {member.display_name}: {row['excuse'][6:]}\n"
        absenceembed = discord.Embed()
        absenceembed.title="All absence"
        absenceembed.description = absence_list
        await ctx.author.send(embed=absenceembed)


    @get.command(name="gear")
    @commands.has_role("Member")
    async def get_gear(self, ctx, member:discord.Member=None):
        query = "SELECT * FROM members WHERE id = $1;"
        if member == None:
            member = ctx.author
        # This returns a asyncpg.Record object, which is similar to a dict
        row = await self.bot.db.fetchrow(query, member.id)

        userembed = discord.Embed()
        userembed.set_author(name=member.display_name, icon_url=member.avatar_url)
        userembed.colour = discord.Color.green()
        gear_stats = f"""
__AP__:    {row["ap"]}
__AAP__: {row["aap"]}
__DP__:    {row["dp"]} 
__Lvl__:    {row["level"]}
__Class__: {row["class"]}
        """
        userembed.add_field(name="Stats:", value=gear_stats, inline=False)
        if row["gearpic"]:
            try:
                userembed.set_image(url=row["gearpic"])
            except Exception:
                pass

        await ctx.send(embed=userembed)

def setup(bot):
    bot.add_cog(Database(bot))
