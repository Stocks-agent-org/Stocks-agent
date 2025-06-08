import discord
from discord.ext import tasks, commands
import datetime

TOKEN = "TVOJ_TOKEN"
USER_ID = 123456789012345678 

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Prijavljen kot {bot.user}")
    daily_message.start()

@tasks.loop(hours=24)
async def daily_message():
    user = await bot.fetch_user(USER_ID)
    if user:
        danes = datetime.datetime.now().strftime("%d.%m.%Y")
        podatki = f"📈 Delnice"
        await user.send(podatki)

# Pošlje takoj po zagonu, nato vsakih 24h
@daily_message.before_loop
async def before():
    await bot.wait_until_ready()

bot.run(TOKEN)