import logging
import sys
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s]:\n%(message)s",
    handlers=[logging.StreamHandler(stream=sys.stdout)],
)


def load_csv(filepath: Path | str) -> None:
    """Loads CSV file with sample data"""
    if filepath.exists():
        logging.info("Data Found: ")
        df = pd.read_csv(filepath)
        logging.info(df.head())
    else:
        logging.error("File Not Found")


if __name__ == "__main__":
    filepath = Path("src") / "data" / "sample.csv"
    load_csv(filepath)
