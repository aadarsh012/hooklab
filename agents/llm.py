"""Generalized LLM caller with Gemini/Groq fallback."""

import logging

from config.config import GEMINI_API_KEY, GROQ_API_KEY

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.0-flash"
GROQ_MODEL = "llama-3.1-8b-instant"


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Call an LLM with system + user prompts. Tries Gemini, falls back to Groq.

    Args:
        system_prompt: The system instruction (role/expertise context).
        user_prompt: The user's specific request.

    Returns:
        The LLM's text response.

    Raises:
        RuntimeError: If neither API key is set.
    """
    if GEMINI_API_KEY:
        try:
            return _call_gemini(system_prompt, user_prompt)
        except Exception as e:
            logger.warning("Gemini failed (%s), falling back to Groq", e)

    if GROQ_API_KEY:
        return _call_groq(system_prompt, user_prompt)

    raise RuntimeError(
        "No LLM API key set. Add GEMINI_API_KEY or GROQ_API_KEY to your .env file."
    )


def _call_gemini(system_prompt: str, user_prompt: str) -> str:
    from google import genai
    from google.genai.types import GenerateContentConfig

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_prompt,
        config=GenerateContentConfig(
            system_instruction=system_prompt,
        ),
    )
    text = response.text
    return text.strip() if text else ""


def _call_groq(system_prompt: str, user_prompt: str) -> str:
    from groq import Groq

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = response.choices[0].message.content
    return content.strip() if content else ""
