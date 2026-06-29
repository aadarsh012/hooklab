"""
Walking skeleton: embed hooks, retrieve nearest to a query,
have Gemini say one sentence about it.

Proves the full embed -> retrieve -> generate pipe works end-to-end.

Usage:
    python scripts/skeleton.py
    python scripts/skeleton.py "best arm exercises"
"""

import json
import sys

sys.path.insert(0, ".")

from embeddings.generate import generate_hook_analysis
from embeddings.store import HookVectorStore


def main():
    train_path = "data/processed/train.jsonl"
    query = sys.argv[1] if len(sys.argv) > 1 else "how to lose belly fat fast"

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

    # 2. Embed and store
    store = HookVectorStore()
    store.embed_and_store(hooks)

    # 3. Retrieve
    print(f"\nQuery: '{query}'")
    results = store.retrieve(query)

    print(f"\nTop {len(results)} nearest hooks:")
    for i, r in enumerate(results, 1):
        print(f"  {i}. [{r.label}] (dist={r.distance:.4f}) {r.hook_text}")

    # 4. Generate analysis
    nearest = results[0]
    try:
        analysis = generate_hook_analysis(nearest.hook_text, query)
        print(f"\nGemini says: {analysis}")
    except RuntimeError as e:
        print(f"\nWARNING: {e}")
        print("Walking skeleton complete (without LLM).")
        return

    print("\n--- Walking skeleton complete ---")


if __name__ == "__main__":
    main()
