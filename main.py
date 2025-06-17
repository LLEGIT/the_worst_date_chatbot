import discord
import asyncio
import os
from dotenv import load_dotenv
import generate_character
from ask_question import RedFlagGame

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

user_states = {}


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    user_id = str(message.author.id)
    if message.content.startswith('!startdate'):
        await message.channel.send(
            "Bienvenue au jeu du pire date, je vais te poser une série de 5 questions, et si tes réponses me conviennent nous pourrons envisager un second rendez vous. Es-tu prêt ?"
        )
        user_states[user_id] = {'stage': 'await_ready'}
    elif user_id in user_states and user_states[user_id]['stage'] == 'await_ready' and message.content.strip().lower() in ["oui", "non", "prêt", "pas prêt"]:
        await message.channel.send("Génération du personnage...")
        character, image_url = await generate_character.generate_character()
        await message.channel.send(character)
        await message.channel.send(image_url)
        user_states[user_id]['stage'] = 'in_game'
        user_states[user_id]['game'] = RedFlagGame()
        user_states[user_id]['question_idx'] = 0
        user_states[user_id]['redflags'] = 0
        user_states[user_id]['history'] = []
        # Ask first question
        question = await user_states[user_id]['game'].get_question()
        user_states[user_id]['current_question'] = question
        await message.channel.send(f"Q1: {question}\n(Réponds par 'oui' ou 'non')")
    elif user_id in user_states and user_states[user_id].get('stage') == 'in_game':
        answer = message.content.strip().lower()
        if answer not in ["oui", "non"]:
            await message.channel.send("Merci de répondre par 'oui' ou 'non'.")
            return
        game = user_states[user_id]['game']
        question = user_states[user_id]['current_question']
        is_redflag = await game.judge_answer(question, answer)
        user_states[user_id]['history'].append((question, answer, is_redflag))
        if is_redflag:
            user_states[user_id]['redflags'] += 1
            await message.channel.send("🚩 Red flag!")
        else:
            await message.channel.send("✅ Réponse acceptée!")
        if user_states[user_id]['redflags'] >= 2:
            await message.channel.send("Tu as eu 2 red flags, la partie est terminée !")
            del user_states[user_id]
            return
        user_states[user_id]['question_idx'] += 1
        if user_states[user_id]['question_idx'] >= 5:
            await message.channel.send("Bravo, tu as survécu au pire date ! Nous allons pouvoir nous découvrir plus profondément.")
            del user_states[user_id]
            return
        # Next question
        next_question = await game.get_question()
        user_states[user_id]['current_question'] = next_question
        await message.channel.send(f"Q{user_states[user_id]['question_idx']+1}: {next_question}\n(Réponds par 'oui' ou 'non')")

if __name__ == "__main__":
    bot.run(TOKEN)
