"""
Walking skeleton: retrieve from persistent Chroma, generate LLM analysis.

Proves the full retrieve -> generate pipe works end-to-end.
Run 'python scripts/embed.py' first to populate the store.

Usage:
    python scripts/skeleton.py
    python scripts/skeleton.py "best arm exercises"
"""

import sys

sys.path.insert(0, ".")

from embeddings.generate import generate_hook_analysis
from embeddings.store import HookVectorStore


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "how to lose belly fat fast"

    # 1. Load from persistent store
    store = HookVectorStore()
    collection_count = store.collection.count()

    if collection_count == 0:
        print("ERROR: No hooks in Chroma. Run 'python scripts/embed.py' first.")
        return

    print(f"Loaded {collection_count} hooks from persistent store")

    # 2. Retrieve
    print(f"\nQuery: '{query}'")
    results = store.retrieve(query)

    print(f"\nTop {len(results)} nearest hooks:")
    for i, r in enumerate(results, 1):
        print(f"  {i}. [{r.label}] (dist={r.distance:.4f}) {r.hook_text}")

    # 3. Generate analysis
    nearest = results[0]
    try:
        analysis = generate_hook_analysis(nearest.hook_text, query)
        print(f"\nLLM says: {analysis}")
    except RuntimeError as e:
        print(f"\nWARNING: {e}")
        print("Walking skeleton complete (without LLM).")
        return

    print("\n--- Walking skeleton complete ---")


if __name__ == "__main__":
    main()
