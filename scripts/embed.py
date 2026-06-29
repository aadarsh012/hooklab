"""
Embed the full training corpus and store in persistent Chroma.

Usage: python scripts/embed.py
"""

import json
import logging
import sys

sys.path.insert(0, ".")

from embeddings.store import HookVectorStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

TRAIN_PATH = "data/processed/train.jsonl"


def main():
    # Load all training hooks
    hooks = []
    with open(TRAIN_PATH) as f:
        for line in f:
            hooks.append(json.loads(line))

    if not hooks:
        logger.error("No hooks found in %s. Run the collection pipeline first.", TRAIN_PATH)
        return

    logger.info("Loaded %d hooks from %s", len(hooks), TRAIN_PATH)

    # Embed and store
    store = HookVectorStore()
    count = store.embed_and_store(hooks)

    # Print collection stats
    collection_count = store.collection.count()
    logger.info("Embedding complete. %d hooks embedded, %d total in collection.", count, collection_count)


if __name__ == "__main__":
    main()
