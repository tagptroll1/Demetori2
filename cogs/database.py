import discord
from discord.ext import commands
import asyncio
import asyncpg
import datetime
import constants as var
from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding

class Database:
    """Cog for handling database related commands"""
    def __init__(self, bot):
        self.bot = bot
        self.key = var.ENCRYPT_KEY
        self.aes = AES.new(self.key, AES.MODE_ECB)

    @staticmethod
    def dateify(date):
        format_string = f"%d{date[2]}%m"
        if len(date) == 8:
            format_string += f"{date[5]}%y"
        elif len(date) == 10:
            format_string += f"{date[5]}%Y"
        
        try:
            return datetime.datetime.strptime(date, format_string)
        except ValueError:
            return None




    @commands.command()
    @commands.guild_only()
    @commands.has_role("Officer")
    async def clear_absence(self, ctx, member:discord.Member=None):
        """Give it a user to clear all his absence, or no user to clear everything"""

        await ctx.message.delete()
        if member:
            query = f"DELETE FROM absence WHERE userid = {member.id}"
        else:
            query = "DELETE FROM absence"
            bots_msg = await ctx.send("Are you sure you want to delete all absence?")
            await bots_msg.add_reaction("👍")
            await bots_msg.add_reaction("👎")

            def check(r, u):
                if u != ctx.author:
                    return False
                if str(r) != "👍" and str(r) != "👎":
                    return False
                return True

            try:
                reaction, user = await self.bot.wait_for("reaction_add", 
                        timeout = 30, check=check)
            except asyncio.TimeoutError:
                await bots_msg.delete()
            else:
                if str(reaction) == "👎":
                    await bots_msg.delete()
                    return

        connection = await self.bot.db.acquire()
        async with connection.transaction():
            await connection.execute(query)
        
        if member:
            await ctx.send(f"Deleted all absence from {member.display_name}", delete_after=5)
        else:
            await ctx.send("Deleted all absence from database", delete_after=5)
        await self.bot.db.release(connection)

    @commands.group(invoke_without_command=True, case_insensitive=True)
    @commands.guild_only()
    async def insert(self, ctx):
        pass

    @commands.command(name="absence")
    @commands.guild_only()
    async def insert_absence(self, ctx, date, *,reason):
        """Add an absence to the database with your ID, reason, date and timestamp
        
        We support the following date formats:
            dd/mm/yyyy  |  dd/mm/yy  |  dd/mm
            dd.mm.yyyy  |  dd.mm.yy  |  dd.mm
        To give a date from/to add a `-` between 2 dates without spacing

        Examples of use:
        ?absence 22/03/2018 I got work that day
        ?absence 03/05/18 My dog need to go to the vet
        ?absence 01/05 National day  
        ?absence 10/05/2018-20/05/2018  going away on holidays :)"""

        
        if "-" in date:
            date = date.split("-")
            try:
                absent_from = Database.dateify(date[0])
                absent_to = Database.dateify(date[1])
            except IndexError:
                await ctx.send("Index error, '-' most likely used incorrectly!")
        else:
            date = Database.dateify(date)
            absent_from = date
            absent_to = date

        if date is not None:
            b_reason = Padding.pad(bytes(reason, "utf-8"), 16)
            enc_msg = self.aes.encrypt(b_reason)

            await ctx.message.delete()
            today = datetime.date.today()
            query = """INSERT INTO absence(
                posted, 
                userid, 
                guildid, 
                excuse, 
                absentfrom, 
                absentto) 
                VALUES ($1, $2, $3, $4, $5, $6);"""
            connection = await self.bot.db.acquire()
            async with connection.transaction():
                await connection.execute(query, 
                        today,
                        ctx.author.id,
                        ctx.guild.id,
                        enc_msg,
                        absent_from,
                        absent_to)
            await ctx.send("Your absence has been registered!", delete_after=5)
            await self.bot.db.release(connection)

            opt_in = discord.utils.get(ctx.guild.roles, name="Opt-in")
            if opt_in:
                for member in opt_in.members:
                    await member.send(f"{ctx.author.display_name} has added an absence: {reason}")

        else:
            await ctx.send("""Could not find a date, we support the following date formats:
            ```
    |  dd/mm/yyyy  |  dd/mm/yy  |  dd/mm  |
    |  dd.mm.yyyy  |  dd.mm.yy  |  dd.mm  |
```
To give a date from/to add a `-` between 2 dates without spacing
```
Examples:
22/03/2018
03/05/18
01/04
10/05/2018-20/05/2018```""")
            return

    @commands.command(name="manual_absence")
    @commands.guild_only()
    @commands.has_role("Officer")
    async def insert_absence_manual(self, ctx, member:discord.Member, *, reason):
        """Add an absence to the data based on member tagged, reason and timestamp"""

        b_reason = Padding.pad(bytes(reason, "utf-8"), 16)
        enc_msg = self.aes.encrypt(b_reason)

        await ctx.message.delete()
        today = datetime.date.today()
        query = "INSERT INTO absence(userid, date, excuse) VALUES ($1, $2, $3);"
        connection = await self.bot.db.acquire()
        async with connection.transaction():
            await connection.execute(query, member.id, today, enc_msg)
        await ctx.send("Your absence has been registered!", delete_after=5)
        await self.bot.db.release(connection)

        opt_in = discord.utils.get(ctx.guild.roles, name="Opt-in")
        if opt_in:
            for member in opt_in.members:
                await member.send(f"{ctx.author.display_name} has added an absence: {reason}")

    @commands.group(invoke_without_command=True, case_insensitive=True)
    @commands.guild_only()
    @commands.has_role("Member")
    async def update(self, ctx):
        pass

    @update.command(name="gear")
    @commands.guild_only()
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
    @commands.guild_only()
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
            if member:
                excuse = self.aes.decrypt(row["excuse"])
                excuse = Padding.unpad(excuse, 16).decode("utf-8")
                absence_list += f"{row['date'].strftime('%A %d-%m')} - {member.display_name}: {excuse}\n"
        absenceembed = discord.Embed()
        absenceembed.title = f"All absence logged today"
        absenceembed.description = absence_list if fetched else "No absence logged"
        await ctx.author.send(embed=absenceembed)

    @get.group(name="member")
    @commands.guild_only()
    @commands.has_role("Officer")
    async def get_user(self, ctx, member:discord.Member=None):
        # TODO implement this f"{a[:77]+'...' if len(a) >= 80 else a :<80}"
        query = "SELECT * FROM absence WHERE userid = $1 ORDER BY absentfrom DESC;"
        if not member:
            member = ctx.author
        fetched = await self.bot.db.fetch(query, member.id)
        absence_list = ""
        for row in fetched:
            if member:
                excuse = self.aes.decrypt(row["excuse"])
                excuse = Padding.unpad(excuse, 16).decode("utf-8")
                from_date = row['absentfrom'].strftime("%d/%m")
                to_date = row['absentto'].strftime("%d/%m")
                date = from_date if from_date == to_date else f"{from_date}-{to_date}"
                a_s = f"{date} - {member.display_name}: {excuse}"
                absence_list += f"{a_s[:62]+'...' if len(a_s) >= 65 else a_s :<65}\n"
        absenceembed = discord.Embed()
        absenceembed.set_author(name=member.display_name, icon_url=member.avatar_url)
        absenceembed.description = absence_list[:2000]
        await ctx.author.send(embed=absenceembed)

    @get.group(name="all")
    @commands.guild_only()
    @commands.has_role("Officer")
    async def get_all(self, ctx):
        
        await ctx.message.delete()
        query = "SELECT * FROM absence ORDER BY date, userid;"
        fetched = await self.bot.db.fetch(query)
        absence_list = ""
        for row in fetched:
            member = discord.utils.get(ctx.guild.members, id=row["userid"])
            if member:
                excuse = self.aes.decrypt(row["excuse"])
                excuse = Padding.unpad(excuse, 16).decode("utf-8")
                absence_list += f"{row['date'].strftime('%A %d-%m')} - {member.display_name}: {excuse}\n"
        absenceembed = discord.Embed()
        absenceembed.title="All absence"
        absenceembed.description = absence_list if fetched else "No absence logged"
        await ctx.author.send(embed=absenceembed)

    @get.group(name="after")
    @commands.guild_only()
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
            if member:
                excuse = self.aes.decrypt(row["excuse"])
                excuse = Padding.unpad(excuse, 16).decode("utf-8")
                absence_list += f"{row['date'].strftime('%A %d-%m')} - {member.display_name}: {excuse}\n"
        absenceembed = discord.Embed()
        absenceembed.title = f"All absence after {delta}"
        absenceembed.description = absence_list if fetched else "No absence logged"
        await ctx.author.send(embed=absenceembed)

    @get.group(name="before")
    @commands.guild_only()
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
            if member:
                excuse = self.aes.decrypt(row["excuse"])
                excuse = Padding.unpad(excuse, 16).decode("utf-8")
                absence_list += f"{row['date'].strftime('%A %d-%m')} - {member.display_name}: {excuse}\n"
        absenceembed = discord.Embed()
        absenceembed.title = f"All absence before {delta}"
        absenceembed.description = absence_list if fetched else "No absence logged"
        await ctx.author.send(embed=absenceembed)
        
    @get.group(name="between")
    @commands.guild_only()
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
            if member:
                excuse = self.aes.decrypt(row["excuse"])
                excuse = Padding.unpad(excuse, 16)
                absence_list += f"{row['date'].strftime('%A %d-%m')} - {member.display_name}: {str(excuse)}\n"
        absenceembed = discord.Embed()
        absenceembed.title = f"All absence between {first} and {last}"
        absenceembed.description = absence_list if fetched else "No absence logged"
        await ctx.author.send(embed=absenceembed)

    @get.command(name="gear")
    @commands.guild_only()
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
