import os
from dotenv import load_dotenv

load_dotenv()

# Niche
NICHE = "fitness"

# LLM provider keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Scoring dimensions for hook evaluation
SCORING_DIMENSIONS = [
    "specificity",
    "curiosity_gap",
    "clarity_of_payoff",
    "concreteness",
]
