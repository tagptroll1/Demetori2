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
            #print(self.stored_embeds[id].content)
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
    @commands.has_role("Officer")
    async def nodewars(self, ctx):
        """Creates a blank nodewar embed with teamspeak, and few other presets
        
        This embed is fully editable"""

        await ctx.message.delete()
        nw_box = CustomizableNodewar(self.bot, ctx)
        self.stored_embeds[ctx.channel.id] = nw_box
        await nw_box.display()

    @commands.command()
    @commands.has_role("Officer")
    async def set_embed(self, ctx, id:int):
        """Sets which embed is in focus"""
        
        await ctx.message.delete()
        copy = await ctx.channel.get_message(id)
        settings = copy.embeds[0].to_dict()
        nw_box = CustomizableNodewar(self.bot, ctx, set_embed=copy)
        await nw_box.edit_param(**settings)
        self.stored_embeds[ctx.channel.id] = nw_box

##------------------EDIT-----
    @commands.group(invoke_without_command=True, case_insensitive=True)
    @commands.has_role("Officer")
    async def edit(self, ctx):
        """Parent command for editing embed"""
        pass

    @edit.command(name="url")
    @commands.has_role("Officer")
    async def edit_url(self, ctx, *, url):
        """Sub-Command for editing url of embed, url applies to thumbnail and title
        
        ?edit url <url>
        url: Sets urls in embed to this, silently ignores invalid urls"""

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
    @commands.has_role("Officer")
    async def edit_title(self, ctx, *, title):
        """Sub-Command for editing title of embed
        
        ?edit title <title>
        title: Sets title to this"""

        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.change_title(title)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

    @edit.command(name="description")
    @commands.has_role("Officer")
    async def edit_description(self, ctx, *, desc):
        """Sub-Command for editing description in embed
        
        ?edit description <text>
        text: Changed embed description to this"""

        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.change_description(desc)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

    @edit.command(name="thumbnail")
    @commands.has_role("Officer")
    async def edit_thumbnail(self, ctx, *, url):
        """Sub-Command for editing thumbnail in embed
        
        ?edit thumbnail <url>
        url: A valid url of an image, silently excepts invalid urls"""

        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.change_thumbnail(url)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

    @edit.command(name="image")
    @commands.has_role("Officer")
    async def edit_image(self, ctx, *, url):
        """Sub-Command for editing image in embed

        ?edit image <url>
        url: A valid url of an image, silently excepts invalid urls"""

        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.change_image(url)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

    @edit.command(name="author")
    @commands.has_role("Officer")
    async def edit_author(self, ctx, *, authorname):
        """Sub-Command for editing author in embed
        
        ?edit author <author>
        author: Name of an author to add"""

        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.change_author(authorname, ctx.guild.icon_url)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

##-------------------TOGGLE----------
    @commands.group(invoke_without_command=True, case_insensitive=True)
    @commands.has_role("Officer")
    async def toggle(self, ctx):
        """Parent command for toggling in embed"""
        pass

    @toggle.command(name="timestamp")
    @commands.has_role("Officer")
    async def toggle_timestamp(self, ctx):
        """Sub-Command for toggeling timestamps
        
        ?toggle timestamp"""

        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.toggle_timestamp()
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

##---------------------ADD-----------
    @commands.group(invoke_without_command=True, case_insensitive=True)
    @commands.has_role("Officer")
    async def add(self, ctx):
        """Parent command for adding to embed"""
        pass

    @add.command(name="field")
    @commands.has_role("Officer")
    async def add_field(self, ctx, title, *, field):
        """Sub-Command for adding a field to embed

        ?add field <title> <text>
        title: The title of the field added
        text : The text appearing under the title"""

        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.add_field(title, field, send=True)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

##-------------REMOVE-----------
    @commands.group(invoke_without_command=True, case_insensitive=True)
    @commands.has_role("Officer")
    async def remove(self, ctx):
        """Parent command for removing in embed"""
        pass

    @remove.command(name="field") 
    @commands.has_role("Officer")
    async def remove_field(self, ctx, index:int):
        """Sub-Command for deleting a field in embed
        
        ?remove field <id>
        id: index of field to be removed starting at 1 from upper left"""

        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.remove_field(id)
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

    @remove.command(name="image")
    @commands.has_role("Officer")
    async def remove_image(self, ctx):
        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.change_image(discord.Embed.Empty)

##--------------CLEAR-----------
    @commands.command(name="field")
    @commands.has_role("Officer")
    async def clear_fields(self, ctx):
        """Sub-Command for clearing all fields in embed
        
        ?clear field"""

        await ctx.message.delete()
        embed = self.has_embed(ctx.channel.id)
        if embed:
            await embed.clear_fields()
        else:
            await ctx.send("No embed stored for this channel to edit", delete_after=10)

    @commands.group(invoke_without_command=True)
    @commands.has_role("Officer")
    async def preset(self, ctx):
        """Parent command for creating pre-made nodewar embeds"""
        pass

    @preset.command()
    @commands.has_role("Officer")
    async def nodewar(self, ctx):
        """Sub-Command for creating a preset embed for mandatory NW
        
        ?preset mandatory"""

        param = {
                "title": f"{ctx.guild.name}s Nodewars information",
                "description": "-------------------------------------",
                "color": discord.Color.red(),
                "footer": {
                    "text": f"Created by {ctx.author.display_name}",
                    "icon_url": ctx.author.avatar_url
                },
                 "author": {
                    "name": self.get_CET(),
                    "icon_url": ctx.guild.icon_url}
                 }
        await ctx.message.delete()
        nw_box = CustomizableNodewar(self.bot, ctx)
        self.stored_embeds[ctx.channel.id] = nw_box
        absent_str = "*if you're absent!*".center(27)
        await nw_box.add_field("<:__:437440834150072331> Nodewar absence",
                               f"**You are expected to attend!\n...\tOR DEATH!\n**\n{'*#absence_channel if you cant attend*'.center(27)} \n{absent_str}",
                               inline=True)
        await nw_box.add_teamspeak()
        await nw_box.add_field("\u200b","\u200b",inline=False)
        await nw_box.add_items()
        await nw_box.display(**param)

  

def setup(bot):
    bot.add_cog(Nodewar(bot))
