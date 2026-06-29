"""
Sanity-check retrieval quality on 10 diverse fitness queries.
Run after embedding: python scripts/test_retrieval.py
"""

import sys

sys.path.insert(0, ".")

from embeddings.store import HookVectorStore

QUERIES = [
    "how to lose belly fat fast",
    "build muscle without gym",
    "morning workout routine for beginners",
    "best protein shake recipe",
    "how to get six pack abs",
    "cardio vs weight training",
    "stretch routine after workout",
    "meal prep for muscle gain",
    "home exercises no equipment",
    "fitness motivation tips",
]


def main():
    store = HookVectorStore()
    collection_count = store.collection.count()

    if collection_count == 0:
        print("ERROR: No hooks in Chroma. Run 'python scripts/embed.py' first.")
        return

    print(f"Collection has {collection_count} hooks\n")
    print("=" * 80)

    for query in QUERIES:
        print(f"\nQuery: '{query}'")
        print("-" * 60)
        results = store.retrieve(query)

        if not results:
            print("  No results found.")
            continue

        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r.label}] (dist={r.distance:.4f}) {r.hook_text}")

    print("\n" + "=" * 80)
    print("Review: Do the results make semantic sense for each query?")


if __name__ == "__main__":
    main()
