"""
HookLab data collection pipeline.

Usage:
    python scripts/collect.py                     # full pipeline
    python scripts/collect.py --step collect       # only collect from YouTube
    python scripts/collect.py --step clean         # only clean raw data
    python scripts/collect.py --step label         # only label cleaned data
    python scripts/collect.py --step split         # only split into train/test
    python scripts/collect.py --import-csv path    # import manual CSV
"""

import argparse
import logging
import sys

sys.path.insert(0, ".")

from ingestion.collector import collect_hooks
from ingestion.cleaner import clean_hooks
from ingestion.labeler import label_hooks
from ingestion.manual import import_manual_csv
from ingestion.splitter import split_dataset

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="HookLab data collection pipeline")
    parser.add_argument(
        "--step",
        choices=["collect", "clean", "label", "split", "all"],
        default="all",
        help="Which pipeline step to run (default: all)",
    )
    parser.add_argument(
        "--import-csv",
        type=str,
        help="Path to manual CSV file to import",
    )
    parser.add_argument(
        "--label-strategy",
        choices=["median", "tercile"],
        default="median",
        help="Labeling strategy (default: median)",
    )
    args = parser.parse_args()

    if args.import_csv:
        logger.info(f"Importing manual CSV: {args.import_csv}")
        hooks = import_manual_csv(args.import_csv)
        logger.info(f"Imported {len(hooks)} hooks")
        return

    steps = {
        "collect": lambda: collect_hooks(),
        "clean": lambda: clean_hooks(),
        "label": lambda: label_hooks(strategy=args.label_strategy),
        "split": lambda: split_dataset(),
    }

    if args.step == "all":
        for name, fn in steps.items():
            logger.info(f"--- Running step: {name} ---")
            fn()
    else:
        logger.info(f"--- Running step: {args.step} ---")
        steps[args.step]()

    logger.info("--- Pipeline complete ---")


if __name__ == "__main__":
    main()
