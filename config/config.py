import os

from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# Niche
NICHE = "fitness"

# LLM provider keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# YouTube Data API
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Collection settings
SEARCH_QUERIES = [
    # General fitness
    "fitness tips shorts",
    "gym motivation shorts",
    "workout tips",
    "home workout shorts",
    "gym tips for beginners",
    # Weight & body
    "weight loss tips shorts",
    "lose belly fat shorts",
    "body transformation shorts",
    "fitness transformation",
    "fat burning workout shorts",
    # Muscle building
    "muscle building tips",
    "how to build muscle shorts",
    "arm workout shorts",
    "chest workout shorts",
    "leg day shorts",
    # Nutrition
    "protein shake recipe shorts",
    "meal prep fitness shorts",
    "what I eat in a day fitness",
    "diet tips shorts",
    # Specific exercises
    "push up challenge shorts",
    "abs workout shorts",
    "stretching routine shorts",
    "calisthenics shorts",
    "running tips shorts",
]
MAX_RESULTS_PER_QUERY = 50
TARGET_HOOK_COUNT = 400

# Scoring dimensions for hook evaluation
SCORING_DIMENSIONS = [
    "specificity",
    "curiosity_gap",
    "clarity_of_payoff",
    "concreteness",
]

# Embedding & retrieval settings
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHROMA_COLLECTION_NAME = "hooklab_hooks"
CHROMA_PERSIST_DIR: Optional[str] = "chroma_db/"
DEFAULT_TOP_K = 3
