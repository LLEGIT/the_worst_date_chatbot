import aiohttp
import asyncio
import json
import os
from dotenv import load_dotenv
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")


class RedFlagGame:
    def __init__(self, model="gemma3:1b"):
        self.model = model
        self.redflags = 0
        self.max_redflags = 2
        self.max_questions = 5
        self.questions_asked = 0
        self.history = []

    async def ask_llm(self, prompt):
        payload = {"model": self.model, "prompt": prompt}
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
                return "".join(responses).strip()

    async def get_question(self):
        prompt = (
            "Génère une question fermée pour un jeu de rencontre amoureuse. "
            "La question doit avoir deux choix possibles : oui ou non. "
            "Ne donne que la question, pas de commentaire ni d'explication."
        )
        return await self.ask_llm(prompt)

    async def judge_answer(self, question, answer):
        prompt = (
            f"Dans le contexte d'un jeu de rencontre amoureuse, voici la question : '{question}'. "
            f"Le joueur a répondu : '{answer}'. "
            "Est-ce une réponse redflag (mauvais signe pour la relation) ? Réponds uniquement par 'redflag' ou 'ok'."
        )
        result = await self.ask_llm(prompt)
        return 'redflag' in result.lower()

    async def play(self):
        print("Bienvenue au jeu du pire date ! Réponds par 'oui' ou 'non'.")
        while self.questions_asked < self.max_questions and self.redflags < self.max_redflags:
            question = await self.get_question()
            self.questions_asked += 1
            print(f"Q{self.questions_asked}: {question}")
            answer = input("(oui/non): ").strip().lower()
            while answer not in ["oui", "non"]:
                answer = input(
                    "Merci de répondre par 'oui' ou 'non' : ").strip().lower()
            is_redflag = await self.judge_answer(question, answer)
            self.history.append((question, answer, is_redflag))
            if is_redflag:
                self.redflags += 1
                print("🚩 Red flag!")
            else:
                print("✅ Réponse acceptée!")
            if self.redflags >= self.max_redflags:
                print("Tu as eu 2 red flags, la partie est terminée !")
                break
        if self.redflags < self.max_redflags:
            print("Bravo, tu as survécu au pire date !")


if __name__ == "__main__":
    game = RedFlagGame()
    asyncio.run(game.play())
