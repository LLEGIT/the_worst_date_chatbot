import discord
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('!startdate'):
        await message.channel.send(
            "Bienvenue au jeu du pire date, je vais te poser une série de 5 questions, et si tes réponses me conviennent nous pourrons envisager un second rendez vous"
        )

if __name__ == "__main__":
    bot.run(TOKEN)
