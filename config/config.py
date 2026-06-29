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
    "fitness tips shorts",
    "gym motivation shorts"
    # "workout tips",
    # "weight loss tips shorts",
    # "muscle building tips",
    # "home workout shorts",
    # "fitness transformation",
    # "gym tips for beginners",
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
CHROMA_PERSIST_DIR: Optional[str] = None  # None = in-memory, set to "chroma_db/" for persistence
DEFAULT_TOP_K = 3
