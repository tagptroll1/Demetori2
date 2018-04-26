import discord
import datetime

class CustomizableNodewar:
    def __init__(self, bot, ctx, set_embed:discord.Message=None):

        self.embed_settings ={
            "title": "Nodewars information",
            "description": f"{ctx.guild.name}'s nodewar information",
            "type": "rich",
            "url": "https://goo.gl/rP2XXd",
            "color": discord.Color.teal(),
            "timestamp": datetime.datetime.today()
            }
        if set_embed:
            self.msg = set_embed
        else:
            self.msg = ctx.message
        self.embed = discord.Embed()
        self.bot = bot
        self.ctx = ctx
        self.timestamp = True


    async def display(self, **params):
        self.embed.timestamp = self.embed_settings["timestamp"]
        if params: 
            if params.get("title"):
                self.embed_settings["title"] = params.pop("title")
                self.embed.title = self.embed_settings["title"]

            if params.get("description"):
                self.embed_settings["description"] = params.pop("description")
                self.embed.description = self.embed_settings["description"]

            if params.get("url"):
                self.embed_settings["url"] = params.pop("url")
                try:
                    self.embed.url = self.embed_settings["url"]
                except Exception:
                    pass

            if params.get("color"):
                self.embed_settings["color"] = params.pop("color")
                try:
                    self.embed.colour = self.embed_settings["color"]
                except Exception:
                    pass

            if params.get("thumbnail"):
                self.embed_settings["thumbnail"] = params.pop("thumbnail")
                self.embed.set_thumbnail(url=self.embed_settings["thumbnail"])

            if params.get("author"):
                self.embed_settings["author"] = {}
                self.embed_settings["author"]["name"] = params["author"].pop("name", None)
                if params["author"].get("icon_url"):
                    self.embed_settings["author"]["icon_url"] = params["author"].pop("icon_url")
                try:
                    self.embed.set_author(name=self.embed_settings["author"]["name"],
                                  icon_url=self.embed_settings["author"]["icon_url"])
                except Exception:
                    pass

            if params.get("footer"):
                self.embed_settings["footer"] = {}
                self.embed_settings["footer"]["text"] = params["footer"].pop("text", None)
                if params["footer"].get("icon_url"):
                    self.embed_settings["footer"]["icon_url"] = params["footer"].pop("icon_url")
                try:
                    self.embed.set_footer(text=self.embed_settings["footer"]["text"],
                                          icon_url=self.embed_settings["footer"]["icon_url"])
                except Exception:
                    pass

            if params.get("image"):
                try:
                    self.embed.set_image(url=params.pop("image"))
                except Exception:
                    pass

            if params.get("fields"):
                for field in params.pop("fields"):
                    self.embed.add_field(
                        name=field["name"], value=field["value"], inline=field["inline"])
        #--------
        if self.msg is not self.ctx.message:
            self.msg = await self.ctx.message.edit(embed=self.embed)
        else:
            self.msg = await self.ctx.send(embed=self.embed)


    async def add_teamspeak(self, send=False):
        self.embed.add_field(name="<:TeamSpeakicon:437440261702811661> Team Speak server",
                                value="*Ts3.buffbot.org*\n*buff*", inline=True)
        if send:
            self.msg = await self.ctx.send(embed=self.embed)


    async def add_items(self, send=False):
        get_items = ["<:meal:437454613646671876> -Food buffs",
                        "<:villabuff:437454613592014849> -Villa buffs",
                        "<:elixir:437454613373779979> -Elixirs",
                        "<:alchemystone:437454613373779968> -Alchemy stone",
                        "<:medical:437454612988166156> -Medical kit",
                        "<:polishedstone:437454613055275030> -Polished stone"]

        self.embed.add_field(name="<:list:437456406921347093> Don't forget:",
                             value='\n'.join(get_items), inline=True)
        if send:
            self.msg = await self.ctx.send(embed=self.embed)


    async def edit_param(self, **kwargs):
        if not self.embed:
            return

        if kwargs.get("title"):
            self.embed_settings["title"] = kwargs.pop("title")
            self.embed.title = self.embed_settings["title"]

        if kwargs.get("description"):
            self.embed_settings["description"] = kwargs.pop("description")
            self.embed.description = self.embed_settings["description"]

        if kwargs.get("timestamp"):
            self.embed_settings["timestamp"] = kwargs.pop("timestamp")
            try:
                self.embed.timestamp = self.embed_settings["timestamp"]
            except Exception:
                pass

        if kwargs.get("url"):
            self.embed_settings["url"] = kwargs.pop("url")
            try:
                self.embed.url = self.embed_settings["url"]
            except Exception:
                pass

        if kwargs.get("color"):
            self.embed_settings["color"] = kwargs.pop("color")
            try:
                self.embed.colour = self.embed_settings["color"]
            except Exception:
                pass

        if kwargs.get("thumbnail"):
            try:
                self.embed.set_thumbnail(url=kwargs.pop("thumbnail"))
            except Exception:
                pass

        if kwargs.get("author"):
            self.embed_settings["author"] = {}
            if kwargs["author"].get("name"):
                self.embed_settings["author"]["name"] = kwargs["author"].pop(
                    "name", None)
                
            if kwargs["author"].get("icon_url"):
                self.embed_settings["author"]["icon_url"] = kwargs["author"].pop(
                    "icon_url")
 
            try:
                self.embed.set_author(name=self.embed_settings["author"]["name"],
                                      icon_url=self.embed_settings["author"]["icon_url"])
            except Exception:
                pass

        if kwargs.get("footer"):
            self.embed_settings["footer"] = {}
            if kwargs["footer"].get("text"):
                self.embed_settings["footer"]["text"] = kwargs["footer"].pop("text", None)

            if kwargs["footer"].get("icon_url"):
                self.embed_settings["footer"]["icon_url"] = kwargs["footer"].pop(
                    "icon_url")

            try:
                self.embed.set_footer(text=self.embed_settings["footer"]["text"],
                                        icon_url=self.embed_settings["footer"]["icon_url"])
            except Exception:
                pass

        if kwargs.get("image"):
            try:
                self.embed.set_image(url=kwargs.pop("image"))
            except Exception:
                pass

        if kwargs.get("fields"):
            for field in kwargs.pop("fields"):
                await self.add_field(field["name"], field["value"], inline=field["inline"])

        return await self.msg.edit(embed=self.embed)

    async def change_description(self, text):
        await self.edit_param(**{"description": text})

    async def change_url(self, url):
        await self.edit_param(**{"url":url})

    async def change_title(self, title):
        await self.edit_param(**{"title": title})

    async def change_thumbnail(self, url):
        await self.edit_param(**{"thumbnail": url})

    async def change_author(self, name, url):
        await self.edit_param(**{"author":{
            "name":name,
            "icon_url":url}
            })

    async def change_image(self, url):
        await self.edit_param(**{"image": url})

    async def toggle_timestamp(self):
        if self.timestamp:
            self.timestamp = False
            await self.edit_param(**{"timestamp": discord.Embed.Empty})
        else:
            self.timestamp = True
            await self.edit_param(**{"timestamp": datetime.datetime.today()})

    async def add_field(self, title, field, inline=True, send=False):
        self.embed.add_field(name=title, value=field, inline=inline)
        if send:
            await self.msg.edit(embed=self.embed)

    async def remove_field(self, index, send=False):
        self.embed.remove_field(index=index)
        if send:
            await self.msg.edit(embed=self.embed)

    async def clear_fields(self, send=False):
        self.embed.clear_fields()
        if send:
            await self.msg.edit(embed=self.embed)
