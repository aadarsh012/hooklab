# HookLab

A short-form hook and script pre-flight analyzer for the **fitness** niche. Uses RAG, agent orchestration, and applied ML on embeddings to score, critique, and rewrite video openers.

## Setup

```bash
# Clone and enter the repo
git clone <repo-url> && cd hooklab

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your Gemini and Groq API keys

# Verify providers are working
python scripts/test_providers.py
```
