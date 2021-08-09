import os
import certifi
import discord
from discord.ext import commands
import pymongo
from dotenv import load_dotenv

load_dotenv(".env")

client = pymongo.MongoClient(os.environ.get("MONGO_URL"), tlsCAFile=certifi.where())

database = client["AntiRaidBots"]
records = database["Records"]

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #region high only commands
    #region cog stuff
    @commands.is_owner()
    @commands.command(hidden=True)
    async def load(self, ctx: commands.Context, *, cog: str):
        try:
            self.bot.load_extension("cogs." + cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def unload(self, ctx: commands.Context, *, cog: str):
        try:
            self.bot.unload_extension("cogs." + cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.is_owner()    
    @commands.command(hidden=True)
    async def reload(self, ctx: commands.Context, *, cog: str):
        try:
            self.bot.unload_extension("cogs." + cog)
            self.bot.load_extension("cogs." + cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')
    
    #endregion
    @commands.is_owner()
    @commands.command()
    async def addhash(self, ctx, hash):
        records.update_one({"_id": "master"}, { "$push": { "imageHashes": hash }})    
        await ctx.reply("Image hash added")

    @commands.is_owner()
    @commands.command()
    async def removehash(self, ctx, hash):
        records.update_one({"_id": "master"}, { "$pull": { "imageHashes": hash }})    
        await ctx.reply("Image hash removed")


    @commands.is_owner()
    @commands.command()
    async def addphishing(self, ctx, phishingName):
        records.update_one({"_id": "master"}, { "$push": { "phishingNames": phishingName }})    
        await ctx.reply("Phishing name added")

    @commands.is_owner()
    @commands.command()
    async def removephishing(self, ctx, phishingName):
        records.update_one({"_id": "master"}, { "$pull": { "phishingNames": phishingName }})    
        await ctx.reply("Phishing name removed")
    #endregion

    @commands.has_guild_permissions(administrator=True)
    @commands.command()
    async def whitelist (self, ctx: commands.Context, userID):
        records.update_one({"_id": ctx.guild.id}, { "$push": { "whitelist": userID }})    
        await ctx.reply("User whitelisted")
    
    @commands.has_guild_permissions(administrator=True)
    @commands.command()
    async def unwhitelist (self, ctx: commands.Context, userID):
        records.update_one({"_id": ctx.guild.id}, { "$pull": { "whitelist": userID }})    
        await ctx.reply("User unwhitelisted")
    
    @commands.has_guild_permissions(administrator=True)
    @commands.command()
    async def updateadmin(self, ctx: commands.Context, user: discord.Member):
        records.update_one({"_id": ctx.guild.id}, { "$pull": { "guildAdmin": user }})
        



def setup(bot):
    bot.add_cog(AdminCommands(bot))
