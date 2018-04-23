import datetime
import time
import pytz

import discord
from discord.ext import commands
from cogs.embeds.CustomizableNodewar import CustomizableNodewar

class Nodewar:
    """Cog for nodewar related commands"""

    def __init__(self, bot):
        self.bot = bot
        self.stored_embeds = {}

    def has_embed(self, id):
        try:
            return self.stored_embeds[id]
        except KeyError:
            return None

    def get_CET(self):
        fmt = "%A %d/%m"
        utc = pytz.timezone('UTC')
        now = utc.localize(datetime.datetime.utcnow())
        oslo = pytz.timezone('Europe/Oslo')
        tomorrow = now.astimezone(oslo) + datetime.timedelta(days=1)
        return tomorrow.strftime(fmt)
        
    @commands.command()
    async def nodewars(self, ctx):
        await ctx.message.delete()
        nw_box = CustomizableNodewar(self.bot, ctx)
        self.stored_embeds[ctx.channel.id] = nw_box
        await nw_box.display()

    @commands.command()
    async def set_embed(self, ctx, id:int):
        await ctx.message.delete()
        self.stored_embeds[ctx.channel.id] = await ctx.channel.get_message(id)

##------------------EDIT-----
    @commands.group(invoke_without_command=True)
    async def edit(self, ctx):
        pass

    @edit.command(name="url")
    async def edit_url(self, ctx, *, url):
        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            try:
                await embed.change_url(url)
            except discord.HTTPException:
                await ctx.send(f"{url} is not a well formed URL", delete_after=10)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

    @edit.command(name="title")
    async def edit_title(self, ctx, *, title):
        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.change_title(title)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

    @edit.command(name="description")
    async def edit_description(self, ctx, *, desc):
        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.change_description(desc)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

    @edit.command(name="thumbnail")
    async def edit_thumbnail(self, ctx, *, url):
        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.change_thumbnail(url)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

    @edit.command(name="image")
    async def edit_image(self, ctx, *, url):
        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.change_image(url)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

    @edit.command(name="author")
    async def edit_author(self, ctx, *, authorname):
        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.change_author(authorname, ctx.guild.icon_url)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

##-------------------TOGGLE----------
    @commands.group(invoke_without_command=True)
    async def toggle(self, ctx):
        pass

    @toggle.command(name="timestamp")
    async def toggle_timestamp(self, ctx):
        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.toggle_timestamp()
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

##---------------------ADD-----------
    @commands.group(invoke_without_command=True)
    async def add(self, ctx):
        pass

    @add.command(name="field")
    async def add_field(self, ctx, title, *, field):
        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.add_field(title, field)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

##-------------REMOVE-----------
    @commands.group(invoke_without_command=True)
    async def remove(self, ctx):
        pass

    @remove.command(name="field")    
    async def remove_field(self, ctx, index:int):
        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.remove_field(id)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

##--------------CLEAR-----------
    @commands.group(invoke_without_command=True)
    async def clear(self, ctx):
        pass

    @clear.command(name="field")
    async def clear_fields(self, ctx):
        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.clear_fields()
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

    @commands.group(invoke_without_command=True)
    async def preset(self, ctx):
        pass

    @preset.command()
    async def mandatory(self, ctx):
        param = {
                "title": "Nodewars information",
                "description": f"{ctx.guild.name}'s mandatory nodewar information",
                "color": discord.Color.red(),
                "footer": {
                    "text": f"Created by {ctx.author.display_name}",
                    "url": ctx.author.avatar_url
                },
                 "author": {
                    "name": self.get_CET(),
                    "url": ctx.guild.icon_url},
                "fields": [("<:__:437440834150072331> Mandatory Nodewar", "*Contact an officer \nif you're absent!*", True)]
                 }
        await ctx.message.delete()
        nw_box = CustomizableNodewar(self.bot, ctx)
        self.stored_embeds[ctx.channel.id] = nw_box
        await nw_box.display(**param)

    @preset.command()
    async def optional(self, ctx):
        param = {
                "title": "Nodewars information",
                "description": f"{ctx.guild.name}'s optional nodewar information",
                "color": discord.Color.green(),
                "footer":{
                    "text":f"Created by {ctx.author.display_name}",
                    "url": ctx.author.avatar_url
                },
                "author": {
                    "name": self.get_CET(),
                    "url": ctx.guild.icon_url},
                "fields": [("<:__:437441228821233666> Optional Nodewar", "*Count as half of \na mandatory nodewar.*", True)]
            }
        await ctx.message.delete()
        nw_box = CustomizableNodewar(self.bot, ctx)
        self.stored_embeds[ctx.channel.id] = nw_box
        await nw_box.display(**param)


def setup(bot):
    bot.add_cog(Nodewar(bot))
