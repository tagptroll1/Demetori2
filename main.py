import os
import sys
import traceback
import datetime

import discord
from discord.ext import commands
import asyncpg
import asyncio

import constants as var

async def run():
    desc = """  Demetori life simplifier
                made by Professor"""

    # NOTE: 127.0.0.1 is the loopback address. If your db is running on the same machine as the code, this address will work
    credentials = {"user": var.DBUSER, "password": var.DBPASS,
                   "database": "demetori2", "host": "127.0.0.1"}
    db = await asyncpg.create_pool(**credentials)

    # Example create table code, you'll probably change it to suit you
    await db.execute("""CREATE TABLE IF NOT EXISTS guilds(
        id bigint PRIMARY KEY, 
        guild_name text);""")

    await db.execute("""CREATE TABLE IF NOT EXISTS members(
        id bigint PRIMARY KEY, 
        guild_id bigint, 
        ap INTEGER, 
        aap INTEGER, 
        dp INTEGER, 
        level INTEGER, 
        class text, 
        gearpic text);""")

    # Old absence db
    #await db.execute("""CREATE TABLE IF NOT EXISTS absence(
    #    id SERIAL PRIMARY KEY, 
    #    date date, 
    #    userid bigint, 
    #    excuse bytea);""")
    
    await db.execute("""CREATE TABLE IF NOT EXISTS absence(
        id SERIAL PRIMARY KEY,
        posted date,
        userid bigint,
        guildid bigint,
        excuse bytea,
        absentfrom date,
        absentto date);""")



    bot_param = {"description": desc,
                "db": db,
                "activity": discord.Game(name="with Professor"),
                "manager": "Bot Manager"}
    bot = Bot(**bot_param)

    try:
        await bot.start(var.BOT_TOKEN)
    except KeyboardInterrupt:
        # Make sure to do these steps if you use a command to exit the bot
        await db.close()
        await bot.logout()

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            description=kwargs.pop("description"),
            case_insensitive=True,
            activity=kwargs.pop("activity"),
            command_prefix=["?", "demetori", "Demetori"]
        )

        self.db = kwargs.pop("db")
        self.start_time = None
        self.app_info = None
        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())
        self.manager_role = kwargs.pop("manager")

    async def track_start(self):
        """
        Waits for the bot to connect to discord and then records the time.
        Can be used to work out uptime.
        """
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    async def create_bot_manager(self, guild):
        role_settings = {"name": self.manager_role,
                        "permissions": discord.Permissions.all(),
                        "hoist": False,
                        "mentionable": False,
                        "color": discord.Colour.from_rgb(0, 0, 1)}
        await guild.create_role(**role_settings)

    async def load_all_extensions(self):
        """
        Attempts to load all cogs
        """
        await self.wait_until_ready()
        await asyncio.sleep(1)

        cogs = ["cogs.member",
                "cogs.officer",
                "cogs.rolemanager",
                "cogs.database",
                "cogs.everyone",
                "cogs.nodewar"]

        for extension in cogs:
            try:
                self.load_extension(extension)
                print(f'loaded {extension}')
            except Exception as e:
                error = f'{extension}\n {type(e).__name__} : {e}'
                print(f'failed to load extension {error}')
        print('-' * 10)

        for guild in self.guilds:
            if not discord.utils.get(guild.roles, name=self.manager_role):
                await self.create_bot_manager(guild)

        print(f"\nUsername: {self.user}\nID: {self.user.id}")

    async def on_ready(self):
        """
        This event is called every time the bot connects or resumes connection.
        """
        print('-' * 10)
        self.app_info = await self.application_info()
        print(f'Logged in as: {self.user.name}\n'
              f'Using discord.py version: {discord.__version__}\n'
              f'Owner: {self.app_info.owner}\n')
        print('-' * 10)

    async def on_message(self, msg):
        if msg.author.bot:
            return  # ignore all bots
        await self.process_commands(msg)


if __name__ == "__main__":
    os.system("CLS")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())



