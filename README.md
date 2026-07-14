# HookLab

AI-powered short-form video hook analyzer for the fitness niche. Scores, critiques, and rewrites video openers using RAG, agentic orchestration, and ML classifiers trained on real YouTube Shorts data.

**[Try it live](https://hooklab-blond.vercel.app/)**

## What it does

Paste a hook and get back:

- **Strength score** (0-100) from a Gradient Boosting classifier trained on embeddings
- **Dimension breakdown** across specificity, curiosity gap, clarity of payoff, and concreteness
- **Persona reactions** from simulated viewers (beginner, skeptic, creator) with watch/scroll verdicts
- **AI rewrites** targeting the weakest dimension, with projected score improvements
- **Similar hooks** retrieved via semantic search from a curated dataset of high-performing Shorts

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────────┐
│  Next.js UI  │────▶│  FastAPI Backend                             │
│  (Vercel)    │◀────│  (Railway)                                   │
└─────────────┘     │                                              │
                    │  ┌─────────────────────────────────────────┐  │
                    │  │  LangGraph Pipeline                     │  │
                    │  │                                         │  │
                    │  │  ┌───────────┐  ┌───────────────────┐   │  │
                    │  │  │ Scorer    │  │ Retriever (RAG)   │   │  │
                    │  │  │ Node      │  │ ChromaDB + embeds │   │  │
                    │  │  └───────────┘  └───────────────────┘   │  │
                    │  │  ┌───────────┐  ┌───────────────────┐   │  │
                    │  │  │ Persona   │  │ Rewriter          │   │  │
                    │  │  │ Simulator │  │ Node              │   │  │
                    │  │  └───────────┘  └───────────────────┘   │  │
                    │  └─────────────────────────────────────────┘  │
                    └──────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | FastAPI, uvicorn |
| Orchestration | LangGraph (StateGraph, parallel nodes) |
| LLMs | Groq (Llama 3.1), Google Gemini |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Store | ChromaDB |
| ML Classifier | scikit-learn (Gradient Boosting) |
| Data Source | YouTube Data API v3 |

## Project Structure

```
hooklab/
├── agents/           # LangGraph nodes (scorer, retriever, persona, rewriter)
├── app/              # FastAPI app and routes
├── config/           # Configuration and system prompts
├── data/             # Raw and processed hook datasets
├── embeddings/       # Embedding generation and ChromaDB store
├── eval/             # Evaluation harness and reports
├── frontend/         # Next.js frontend
├── ingestion/        # YouTube data collection pipeline
├── scoring/          # ML classifier training and inference
└── scripts/          # CLI scripts for training, eval, and testing
```

## Local Development

### Backend

```bash
git clone https://github.com/aadarsh012/hooklab.git && cd hooklab

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Add GROQ_API_KEY and GEMINI_API_KEY

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Data Pipeline

```bash
# Collect hooks from YouTube Shorts
python scripts/collect.py

# Generate embeddings and store in ChromaDB
python scripts/embed.py

# Train the classifier
python scripts/train_scorer.py

# Run evaluation harness
python scripts/run_eval.py
```

## Evaluation

The eval harness validates the pipeline across three axes:

- **ML accuracy** — classifier vs. majority-class and length-heuristic baselines
- **LLM-as-judge** — blind A/B comparison of original vs. rewritten hooks
- **Classifier upgrade rate** — percentage of rewrites that flip from weak to strong

Reports are generated as Markdown in `eval/REPORT.md`.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for Llama 3.1 |
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `YOUTUBE_API_KEY` | For collection | YouTube Data API v3 key |
| `CORS_ORIGINS` | Production | Comma-separated allowed origins |
| `NEXT_PUBLIC_API_URL` | Frontend | Backend URL for API calls |
