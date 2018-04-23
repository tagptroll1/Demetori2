import discord
from discord.ext import commands
import asyncio
import asyncpg


class Database:
    """Cog for handling database related commands"""
    def __init__(self, bot):
        self.bot = bot
    
    # Example commands, don't use them
    @commands.command()
    async def query(self, ctx):
        query = "SELECT * FROM demetori WHERE id = $1;"

        # This returns a asyncpg.Record object, which is similar to a dict
        row = await self.bot.db.fetchrow(query, ctx.author.id)
        await ctx.send(f"{row['id']}: {row['data']}")

    @commands.command()
    async def insert(self, ctx, *, new_data: str):
        connection = await self.bot.db.acquire()
        query = "INSERT INTO demetori(userid, data) VALUES ($1, $2)"
        await connection.execute(query, ctx.author.id, new_data)
        await self.bot.db.release(connection)
        await ctx.send(f"NEW:\n{ctx.author.id}: {new_data}")

    @commands.command()
    async def update(self, ctx, *, new_data: str):
        # Once the code exits the transaction block, changes made in the block are committed to the db

        connection = await self.bot.db.acquire()
        async with connection.transaction():
            query = "UPDATE demetori SET data = $1 WHERE id = $2"
            await self.bot.db.execute(query, new_data, ctx.author.id)
        await self.bot.db.release(connection)

        await ctx.send(f"NEW:\n{ctx.author.id}: {new_data}")

def setup(bot):
    bot.add_cog(Database(bot))
