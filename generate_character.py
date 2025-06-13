import aiohttp
import asyncio
import json
import os
import random
from dotenv import load_dotenv
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")


async def generate_character():
    prompt = (
        "Génère une phrase de présentation d'une femme fictive en français, en suivant ce schéma : "
        "'Salut, moi c'est *prenom*, j'ai *age* et je vis à *ville*, es tu prêt à me date ou veux tu laisser ta chance s'envoler ?' "
        "Le prénom, l'âge et la ville doivent être aléatoires. Retourne seulement la phrase, ne rajoute pas de commentaire ou d'explication. Ne redonne pas le même prénom, âge ou ville que précédemment. "
    )
    payload = {
        "model": "gemma3:1b",
        "prompt": prompt
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_URL, json=payload) as resp:
            text = await resp.text()
            responses = []
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if "response" in data:
                        responses.append(data["response"])
                except Exception:
                    continue
            character_text = "".join(responses).strip()
    # Generate a random image URL
    img_num = random.randint(1, 99)
    image_url = f"https://randomuser.me/api/portraits/women/{img_num}.jpg"
    return character_text, image_url
