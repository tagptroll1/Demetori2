import discord
import datetime

class CustomizableNodewar:
    def __init__(self, bot, ctx):
        self.embed_settings ={
            "title": "Nodewars information",
            "description": f"{ctx.guild.name}'s nodewar information",
            "url": "https://goo.gl/rP2XXd",
            "color": discord.Color.teal(),
            "timestamp": datetime.datetime.today(),
            "thumbnail": "https://www.com",
            "footer": { "text":"",
                        "url":"https://www.com"},
            "image": "https://www.com",
            "author": { "name": "",
                        "url": "https://www.com"},
            "fields": []
            }

        self.msg = None
        self.embed = discord.Embed()
        self.bot = bot
        self.ctx = ctx
        self.timestamp = True


    async def display(self, **params):
        get_items = ["<:meal:437454613646671876> -Food buffs",
                     "<:villabuff:437454613592014849> -Villa buffs",
                     "<:elixir:437454613373779979> -Elixirs",
                     "<:alchemystone:437454613373779968> -Alchemy stone",
                     "<:medical:437454612988166156> -Medical kit",
                     "<:polishedstone:437454613055275030> -Polished stone"]

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
                self.embed_settings["author"]["name"] = params["author"].pop("name")
                self.embed_settings["author"]["url"] = params["author"].pop("url")
                try:
                    self.embed.set_author(name=self.embed_settings["author"]["name"],
                                  url=self.embed_settings["author"]["url"])
                except Exception:
                    pass

            if params.get("footer"):
                self.embed_settings["footer"]["text"] = params["footer"].pop("text")
                self.embed_settings["footer"]["url"] = params["footer"].pop("url")
                try:
                    self.embed.set_footer(text=self.embed_settings["footer"]["text"],
                                    icon_url=self.embed_settings["footer"]["url"])
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
                        name=field[0], value=field[1], inline=field[2])

            self.embed.add_field(name="<:TeamSpeakicon:437440261702811661> Team Speak server",
                                value="*Ts3.buffbot.org*\n*buff*", inline=True)

            self.embed.add_field(name="\u200b", value="\u200b", inline=False)
            
            self.embed.add_field(name="<:list:437456406921347093> Don't forget:",
                                value='\n'.join(get_items), inline=True)
                                

        #--------
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
            self.embed_settings["author"]["name"] = kwargs["author"].pop("name")
            self.embed_settings["author"]["url"] = kwargs["author"].pop("url")
            try:
                self.embed.set_author(name=self.embed_settings["author"]["name"],
                              icon_url=self.embed_settings["author"]["url"])
            except Exception:
                pass

        if kwargs.get("footer"):
                self.embed_settings["footer"]["text"] = kwargs["footer"].pop("text")
                self.embed_settings["footer"]["url"] = kwargs["footer"].pop(
                    "url")
                try:
                    self.embed.set_footer(text=self.embed_settings["footer"]["text"],
                                      icon_url=self.embed_settings["footer"]["url"])
                except Exception:
                    pass

        if kwargs.get("image"):
            try:
                self.embed.set_image(url=kwargs.pop("image"))
            except Exception:
                pass

        if kwargs.get("fields"):
            for field in kwargs.pop("fields"):
                await self.add_field(field[0], field[1], inline=field[2])

        return await self.msg.edit(embed=self.embed)

            
    async def change_url(self, url):
        await self.edit_param(**{"url":url})

    async def change_title(self, title):
        await self.edit_param(**{"title": title})

    async def change_thumbnail(self, url):
        await self.edit_param(**{"thumbnail": url})

    async def change_author(self, name, url):
        await self.edit_param(**{"author":{
            "name":name,
            "url":url}
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

    async def add_field(self, title, field, inline=True):
        embed = self.msg.embeds[0]
        embed.add_field(name=title, value=field, inline=inline)
        await self.msg.edit(embed=embed)

    async def remove_field(self, index):
        embed = self.msg.embeds[0]
        embed.remove_field(index=index)
        await self.msg.edit(embed=embed)

    async def clear_fields(self):
        embed = self.msg.embeds[0]
        embed.clear_fields()
        await self.msg.edit(embed=embed)
