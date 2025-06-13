import discord
import asyncio
import os
from dotenv import load_dotenv
import generate_character

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
            "Bienvenue au jeu du pire date, je vais te poser une série de 5 questions, et si tes réponses me conviennent nous pourrons envisager un second rendez vous. Es-tu prêt ?"
        )
    elif message.content.strip().lower() in ["oui", "non", "prêt", "pas prêt"]:
        await message.channel.send("Génération du personnage...")
        character, image_url = await generate_character.generate_character()
        await message.channel.send(character)
        await message.channel.send(image_url)

if __name__ == "__main__":
    bot.run(TOKEN)
