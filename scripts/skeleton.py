"""
Walking skeleton: embed 20 hooks, retrieve nearest to a query,
have Gemini say one sentence about it.

Proves the full embed -> retrieve -> generate pipe works end-to-end.

Usage: python scripts/skeleton.py
"""

import json
import sys

sys.path.insert(0, ".")

import chromadb
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

from config.config import GEMINI_API_KEY


def main():
    train_path = "data/processed/train.jsonl"

    # 1. Load first 20 hooks
    hooks = []
    with open(train_path) as f:
        for i, line in enumerate(f):
            if i >= 20:
                break
            hooks.append(json.loads(line))

    if not hooks:
        print("ERROR: No hooks found in train.jsonl. Run the collection pipeline first.")
        return

    print(f"Loaded {len(hooks)} hooks")

    # 2. Embed with sentence-transformers
    print("Embedding hooks...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [h["hook_text"] for h in hooks]
    embeddings = model.encode(texts)

    # 3. Store in Chroma (in-memory)
    client = chromadb.Client()
    collection = client.create_collection("skeleton_hooks")
    collection.add(
        ids=[h["hook_id"] for h in hooks],
        embeddings=[e.tolist() for e in embeddings],
        documents=texts,
        metadatas=[{"label": h["label"], "engagement_ratio": h["engagement_ratio"]} for h in hooks],
    )
    print(f"Stored {len(hooks)} hooks in Chroma")

    # 4. Query
    query = "how to lose belly fat fast"
    print(f"\nQuery: '{query}'")

    query_embedding = model.encode([query])
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=3,
    )

    print("\nTop 3 nearest hooks:")
    for i in range(len(results["documents"][0])):
        doc = results["documents"][0][i]
        meta = results["metadatas"][0][i]
        dist = results["distances"][0][i]
        print(f"  {i + 1}. [{meta['label']}] (dist={dist:.4f}) {doc}")

    nearest_hook = results["documents"][0][0]

    # 5. Gemini says one sentence
    if not GEMINI_API_KEY:
        print("\nWARNING: GEMINI_API_KEY not set, skipping LLM step.")
        print("\n--- Walking skeleton complete (without LLM) ---")
        return

    genai.configure(api_key=GEMINI_API_KEY)
    llm = genai.GenerativeModel("gemini-2.0-flash")

    prompt = (
        f"You are a short-form video hook analyst specializing in fitness content. "
        f'Given this fitness hook: "{nearest_hook}"\n'
        f"Say one sentence about why it works or doesn't work as an opener."
    )

    response = llm.generate_content(prompt)
    print(f"\nGemini says: {response.text.strip()}")

    print("\n--- Walking skeleton complete ---")


if __name__ == "__main__":
    main()
