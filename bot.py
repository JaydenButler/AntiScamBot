from datetime import datetime, timedelta
import os
import discord
import logging
from discord.ext import commands, tasks
import pymongo
import certifi
from dotenv import load_dotenv

load_dotenv(".env")


intents = discord.Intents.default()
intents.members = True


initial_extensions = ['cogs.auto_moderation', 'cogs.admin_commands']

bot = commands.Bot(command_prefix='!', intents=intents)

client = pymongo.MongoClient(os.environ.get("MONGO_URL"), tlsCAFile=certifi.where())

database = client["AntiRaidBots"]
records = database["Records"]

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)
        print("loaded " + extension)

@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    print(f'Successfully logged in and booted!')
    await bot.change_presence(activity=discord.Game(name=f"Protecting {len(bot.guilds)} servers"))

@bot.event
async def on_guild_join(guild: discord.Guild):
    await bot.change_presence(activity=discord.Game(name=f"Protecting {len(bot.guilds)} servers"))
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }
    channel = await guild.create_text_channel(name="gift-bot-logs", overwrites=overwrites)
    await guild.create_role(name="RAID ALERT")
    data = {
        "_id": guild.id,
        "whitelist": [],
        "botlist": [],
        "guildAdmin": "a server administrator"
    }
    records.insert_one(data)
    embed = discord.Embed(title="Anti Raid Bot Information", colour=discord.Colour(0x86ff00), description="Hi there! Thank you for adding me to your server.\n\nMy one and only goal is to stop the bots. They suck.\n\n If you have any suggestions, please DM my creater High#1234. ``` ```\n\n", timestamp=datetime.utcfromtimestamp(1628497873))
    embed.set_footer(text="If you have any questions, please DM High#1234")
    embed.add_field(inline=False, name="**My Commands**", value="**`!whitelist userID`** - Whitelists a user to your server \n\n**`!unwhitelist userID`** - Unwhitelists a user from your server\n\n**`!updateadmin @User`** - Updates the main server admin that user's are told to message in the case of questions or issues ``` ```")
    embed.add_field(inline=False, name="**F.A.Q**", value="Q. Do I have false positives?\nA. Unfortunately, yes I do. If someone has 'rl' in their name at all, it will kick them. I hope to fix this in the future. If you see this happen, just whitelist the user and they will be able to join.\n\nQ. Can I make suggestions for logo or names to add to the blacklist?\n" + 
    "A. Yes you can! Just let High know and he'll add it to the list. (Please ensure all requests are related to botting and not a singular person)\n\nQ. Can I give others an invite for the Anti Raid Bot?\nA. For the time being, please don't give out my link to anyone. Instead, please get them to DM High for a link while we iron out any kinks that may arise in the near future.\n\n" + 
    "Q. Can I change the name of this channel or the raid alerts role?\nA. No. Please don't change the name of the raid alerts role or this channel. Feel free to edit permissions though!``` ```Thanks for reading, thank you for making our community safer for everyone! ")
    await channel.send(embed=embed)
    
    

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot.run(os.environ.get("BOT_TOKEN"), bot=True, reconnect=True)
