"""Smoke test: verify Gemini and Groq API keys are working."""

import sys

sys.path.insert(0, ".")

from config.config import GEMINI_API_KEY, GROQ_API_KEY


def test_gemini():
    import google.generativeai as genai

    if not GEMINI_API_KEY:
        print("[GEMINI] SKIP — GEMINI_API_KEY not set")
        return False

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content("Say 'hello' in one word.")
    print(f"[GEMINI] OK — {response.text.strip()}")
    return True


def test_groq():
    from groq import Groq

    if not GROQ_API_KEY:
        print("[GROQ]   SKIP — GROQ_API_KEY not set")
        return False

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say 'hello' in one word."}],
        max_tokens=10,
    )
    print(f"[GROQ]   OK — {response.choices[0].message.content.strip()}")
    return True


if __name__ == "__main__":
    print("Testing LLM providers...\n")
    results = []

    for name, test_fn in [("Gemini", test_gemini), ("Groq", test_groq)]:
        try:
            results.append(test_fn())
        except Exception as e:
            print(f"[{name.upper()}] FAIL — {e}")
            results.append(False)

    print()
    if all(results):
        print("All providers working!")
    else:
        print("Some providers failed or were skipped. Check your .env file.")
