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

        await ctx.message.delete()
        if member:
            query = f"DELETE FROM absence WHERE userid = {member.id}"
        else:
            query = "DELETE FROM absence"
        connection = await self.bot.db.acquire()
        async with connection.transaction():
            await connection.execute(query)
        
        if member:
            await ctx.send(f"Deleted all absence from {member.display_name}", delete_after=5)
        else:
            await ctx.send("Deleted all absence from database", delete_after=5)
        await self.bot.db.release(connection)

    @commands.group(invoke_without_command=True, case_insensitive=True)
    async def insert(self, ctx):
        pass

    @commands.command(name="absence")
    @commands.has_role("Member")
    async def insert_absence(self, ctx, *,reason):
        """Add an absence to the data base with your ID, reason and timestamp"""

        await ctx.message.delete()
        today = datetime.date.today()
        query = "INSERT INTO absence(userid, date, excuse) VALUES ($1, $2, $3);"
        connection = await self.bot.db.acquire()
        async with connection.transaction():
            await connection.execute(query, ctx.author.id, today, reason)
        await ctx.send("Your absence has been registered!", delete_after=5)
        await self.bot.db.release(connection)

        opt_in = discord.utils.get(ctx.guild.roles, name="Opt-in")
        if opt_in:
            for member in opt_in.members:
                await member.send(f"{ctx.author.display_name} has added an absence: {reason}")

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
        await ctx.message.delete()

        timestamp = datetime.date.today()
        query = """SELECT * FROM absence 
        WHERE date = $1 
        ORDER BY date, userid;"""
        fetched = await self.bot.db.fetch(query, timestamp)
        absence_list = ""
        for row in fetched:
            member = discord.utils.get(ctx.guild.members, id=row["userid"])
            absence_list += f"{row['date'].strftime('%A %d-%m')} - {member.display_name}: {row['excuse']}\n"
        absenceembed = discord.Embed()
        absenceembed.title = f"All absence logged today"
        absenceembed.description = absence_list if fetched else "No absence logged"
        await ctx.author.send(embed=absenceembed)

    @get.group(name="member")
    @commands.has_role("Officer")
    async def get_user(self, ctx, member:discord.Member=None):
        query = "SELECT * FROM absence WHERE userid = $1;"
        if not member:
            member = ctx.author
        fetched = await self.bot.db.fetch(query, member.id)
        absence_list = ""
        for row in fetched:
            absence_list += f"{row['date'].strftime('%A %d-%m')} - {member.display_name} {row['excuse']}\n"
        absenceembed = discord.Embed()
        absenceembed.set_author(name=member.display_name, icon_url=member.avatar_url)
        absenceembed.description = absence_list
        await ctx.author.send(embed=absenceembed)

    @get.group(name="all")
    @commands.has_role("Officer")
    async def get_all(self, ctx):
        
        await ctx.message.delete()
        query = "SELECT * FROM absence ORDER BY date, userid;"
        fetched = await self.bot.db.fetch(query)
        absence_list = ""
        for row in fetched:
            member = discord.utils.get(ctx.guild.members, id=row["userid"])
            absence_list += f"{row['date'].strftime('%A %d-%m')} - {member.display_name}: {row['excuse']}\n"
        absenceembed = discord.Embed()
        absenceembed.title="All absence"
        absenceembed.description = absence_list if fetched else "No absence logged"
        await ctx.author.send(embed=absenceembed)

    @get.group(name="after")
    @commands.has_role("Officer")
    async def get_after(self, ctx, delta):
        await ctx.message.delete()
        if not(len(delta) == 10 and delta[2] == "-" and delta[5]== "-"):
            await ctx.send("Wrong format for date, valid format is: 'dd-mm-yyyy'")
            return

        timestamp = datetime.datetime.strptime(delta, "%d-%m-%Y")
        query = """SELECT * FROM absence 
        WHERE date >= $1 
        ORDER BY date, userid;"""
        fetched = await self.bot.db.fetch(query, timestamp)
        absence_list = ""
        for row in fetched:
            member = discord.utils.get(ctx.guild.members, id=row["userid"])
            absence_list += f"{row['date'].strftime('%A %d-%m')} - {member.display_name}: {row['excuse']}\n"
        absenceembed = discord.Embed()
        absenceembed.title = f"All absence after {delta}"
        absenceembed.description = absence_list if fetched else "No absence logged"
        await ctx.author.send(embed=absenceembed)

    @get.group(name="before")
    @commands.has_role("Officer")
    async def get_before(self, ctx, delta):
        await ctx.message.delete()
        if not(len(delta) == 10 and delta[2] == "-" and delta[5] == "-"):
            await ctx.send("Wrong format for date, valid format is: 'dd-mm-yyyy'")
            return

        timestamp = datetime.datetime.strptime(delta, "%d-%m-%Y")
        query = """SELECT * FROM absence 
        WHERE date <= $1 
        ORDER BY date, userid;"""
        fetched = await self.bot.db.fetch(query, timestamp)
        absence_list = ""
        for row in fetched:
            member = discord.utils.get(ctx.guild.members, id=row["userid"])
            absence_list += f"{row['date'].strftime('%A %d-%m')} - {member.display_name}: {row['excuse']}\n"
        absenceembed = discord.Embed()
        absenceembed.title = f"All absence before {delta}"
        absenceembed.description = absence_list if fetched else "No absence logged"
        await ctx.author.send(embed=absenceembed)
        
    @get.group(name="between")
    @commands.has_role("Officer")
    async def get_between(self, ctx, first, last):
        await ctx.message.delete()
        if not(len(first) == 10 and first[2] == "-" and first[5] == "-"):
            await ctx.send("Wrong format for first date, valid format is: 'dd-mm-yyyy'")
            return

        if not(len(last) == 10 and last[2] == "-" and last[5] == "-"):
            await ctx.send("Wrong format for last date, valid format is: 'dd-mm-yyyy'")
            return

        date1 = datetime.datetime.strptime(first, "%d-%m-%Y")
        date2 = datetime.datetime.strptime(last, "%d-%m-%Y")
        query = """SELECT * FROM absence 
        WHERE date BETWEEN 
        $1 AND $2 
        ORDER BY date, userid;"""
        fetched = await self.bot.db.fetch(query, date1, date2)
        absence_list = ""
        for row in fetched:
            member = discord.utils.get(ctx.guild.members, id=row["userid"])
            absence_list += f"{row['date'].strftime('%A %d-%m')} - {member.display_name}: {row['excuse']}\n"
        absenceembed = discord.Embed()
        absenceembed.title = f"All absence between {first} and {last}"
        absenceembed.description = absence_list if fetched else "No absence logged"
        await ctx.author.send(embed=absenceembed)

    @get.command(name="gear")
    @commands.has_role("Member")
    async def get_gear(self, ctx, member:discord.Member=None):
        query = "SELECT * FROM members WHERE id = $1;"
        if member == None:
            member = ctx.author

        row = await self.bot.db.fetchrow(query, member.id)

        userembed = discord.Embed()
        if row["gearpic"] and row["gearpic"].startswith("http"):
            userembed.set_author(name=member.display_name, icon_url=member.avatar_url , url=row["gearpic"])
        else:
            userembed.set_author(name=member.display_name, icon_url=member.avatar_url)

        if int(row["level"]) >= 61:
            userembed.colour = discord.Color.green()
        elif int(row["level"]) == 60:
            userembed.colour = discord.Color.orange()
        elif int(row["level"]) <= 59:
            userembed.colour = discord.Color.red()

        renown = ((int(row["ap"]) + int(row["aap"])) // 2) + int(row["dp"])
        renown_s = f"*Renown score {renown}*"# if not row["gearpic"] else f"*Renown score {renown}* \t [[Gear Link]({row['gearpic']})]"
        userembed.add_field(name=f"Level {row['level']} {row['class']}", value=renown_s, inline=False)
        userembed.add_field(name="AP", value=row['ap'], inline=True)
        userembed.add_field(name="Awakening AP", value=row['aap'], inline=True)
        userembed.add_field(name="DP", value=row['dp'], inline=True)
        userembed.set_footer(text="Click members username for a picture of gear, if available")
        await ctx.send(embed=userembed)

def setup(bot):
    bot.add_cog(Database(bot))
