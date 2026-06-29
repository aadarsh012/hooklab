"""LLM generation wrapper for hook analysis. Tries Gemini first, falls back to Groq."""

import logging

from config.config import GEMINI_API_KEY, GROQ_API_KEY
from config.system_prompt import HOOK_EXPERT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.0-flash"
GROQ_MODEL = "llama-3.1-8b-instant"

ANALYSIS_PROMPT_TEMPLATE = (
    'Analyze this fitness hook: "{hook_text}"\n'
    'The user searched for: "{query}"\n\n'
    "Score it on the 4 dimensions (specificity, curiosity gap, clarity of payoff, "
    "concreteness) and explain in 2-3 sentences why it works or doesn't work as an opener."
)


def _generate_with_gemini(prompt: str) -> str:
    from google import genai
    from google.genai.types import GenerateContentConfig

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=GenerateContentConfig(
            system_instruction=HOOK_EXPERT_SYSTEM_PROMPT,
        ),
    )
    text = response.text
    return text.strip() if text else ""


def _generate_with_groq(prompt: str) -> str:
    from groq import Groq

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": HOOK_EXPERT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content
    return content.strip() if content else ""


def generate_hook_analysis(hook_text: str, query: str) -> str:
    """Generate a one-sentence hook analysis. Tries Gemini, falls back to Groq.

    Args:
        hook_text: The hook to analyze.
        query: The original user query (for context).

    Returns:
        The LLM's one-sentence analysis.

    Raises:
        RuntimeError: If neither API key is set.
    """
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(hook_text=hook_text, query=query)

    if GEMINI_API_KEY:
        try:
            return _generate_with_gemini(prompt)
        except Exception as e:
            logger.warning(f"Gemini failed ({e}), falling back to Groq")

    if GROQ_API_KEY:
        return _generate_with_groq(prompt)

    raise RuntimeError(
        "No LLM API key set. Add GEMINI_API_KEY or GROQ_API_KEY to your .env file."
    )
