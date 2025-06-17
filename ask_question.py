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

    async def generate_values(self):
        prompt = (
            "Génère une liste de 2 valeurs fondamentales (principes de vie, convictions, priorités) pour une femme fictive dans le contexte d'une rencontre amoureuse. "
            "Retourne uniquement la liste, chaque valeur sur une ligne, sans commentaire ni explication."
        )
        values_text = await self.ask_llm(prompt)
        return [v.strip('-• ').strip() for v in values_text.split('\n') if v.strip()]

    async def judge_answer(self, question, answer):
        # Compare the answer to the persona's values
        if not hasattr(self, 'persona_values'):
            self.persona_values = await self.generate_values()

        prompt = (
            f"Voici la liste des valeurs fondamentales de la personne : {self.persona_values}. "
            f"Question : '{question}'. Réponse du joueur : '{answer}'. "
            "Si la réponse du joueur va à l'encontre d'une de ces valeurs, réponds uniquement par 'redflag'. Sinon, réponds 'ok'. Sois tolérant, n'attribue un redflag que si la réponse est vraiment incompatible avec les valeurs listées."
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
