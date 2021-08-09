import math
import os
import certifi
import discord # pip install discord.py
from datetime import datetime, timedelta
from discord.ext import commands
import requests # pip install requests
from PIL import Image # pip install pillow
import imagehash
import pymongo # pip install pymongo[srv]
from dotenv import load_dotenv

load_dotenv(".env")
client = pymongo.MongoClient(os.environ.get("MONGO_URL"), tlsCAFile=certifi.where())

database = client["AntiRaidBots"]
records = database["Records"]

class AutoModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, fakeMember: discord.Member):
        member = commands.Bot.get_user(self.bot, id = fakeMember.id)
        guild: discord.Guild = fakeMember.guild
        settings = records.find_one({"_id": guild.id})
        channel: discord.TextChannel = discord.utils.get(guild.channels, name = "gift-bot-logs")
        master = records.find_one({"_id": "master"})
        last30Days = False
        if(((datetime.utcnow() - member.created_at).total_seconds() // 86400) < 30):
            last30Days = True
        last14Days = False
        if(((datetime.utcnow() - member.created_at).total_seconds() // 86400) < 14):
            last14Days = True
        timeSinceCreation = math.trunc((datetime.utcnow() - member.created_at).total_seconds() // 86400)
        embed = discord.Embed(description = f"- __Account made in the last 30 days:__ {last30Days}\n- __Less than 14 days between creation and joining the server:__ {last14Days}\n" +
        f"- __Days since creation:__ {timeSinceCreation}\n**Registered**: {member.created_at}")
        embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"ID: {member.id}")
        if(str(member.id) in settings["whitelist"]):
            await channel.send(embed = embed)
        else:
            alertRole: discord.Role = discord.utils.get(channel.guild.roles, name="RAID ALERT")
            #Temp, shorten this in future
            trigger = False
            for name in master["phishingNames"]:
                if name in member.display_name.lower():
                    trigger = True
            if(trigger):
                admin = settings["guildAdmin"]
                await channel.send(f"{alertRole.mention} - phishing bot detected and kicked. If this was an error, please unban the account and send them a message.", embed = embed)
                await member.send(f"You have been kicked from the {guild.name} server due to a blacklisted name. If you think this is an error, please DM { admin }.")
                await channel.guild.kick(member)
                records.update_one({"_id": guild.id}, { "$push": { "botlist": member.id }})
            elif(last30Days and member.avatar is None):
                await channel.send(f"{alertRole.mention}  - Account made in the last 30 days with a default profile picture has been kicked.", embed = embed)
                await member.send(f"In an effort to stop bots from entering the {guild.name} Discord, we are kicking all accounts " +
                "made in the last 30 days with a default profile picture.\nPlease change your profile picture to something that isn't the default " +
                f"image and re join the server at {await channel.create_invite()} in 5 minutes.\n\n*Thank you for understanding and sorry for the hassle!*")
                await channel.guild.kick(member)
                records.update_one({"_id": guild.id}, { "$push": { "botlist": member.id }})  
            else:
                r = requests.get(member.avatar_url, stream=True)
                r.raw.decode_content = True
                image = Image.open(r.raw)
                userHash = imagehash.average_hash(image) 
                cutoff = 10
                badProfilePic = False
                for storedHashStr in master["imageHashes"]:
                    storedHash = imagehash.hex_to_hash(storedHashStr)
                    if storedHash - userHash < cutoff:
                        badProfilePic = True
                        
                if(badProfilePic):
                    await channel.send(f"{alertRole.mention}  - Account has a blacklisted profile picture and was kicked.", embed = embed)
                    await member.send(f"In an effort to stop bots from entering the {guild.name} Discord, we are kicking all accounts " +
                    f"that have a blacklisted logo. Please change your profile picture re join the server at {await channel.create_invite()} in 5 minutes.\n\n*Thank you for understanding and sorry for the hassle!*")
                    await channel.guild.kick(member)
                    records.update_one({"_id": guild.id}, { "$push": { "botlist": member.id }}) 
                else:
                    await channel.send(embed = embed)

    

def setup(bot):
    bot.add_cog(AutoModeration(bot))
