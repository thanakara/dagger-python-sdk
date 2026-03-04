import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s]:\n%(message)s",
    handlers=[logging.StreamHandler(stream=sys.stdout)],
)


def get_posts(filepath: Path | str) -> None:
    """Gets all posts from JSON file"""
    if filepath.exists():
        with filepath.open("r") as f_:
            posts = json.load(f_)
        logging.info(json.dumps(posts, indent=3))
    else:
        logging.error("File Not Found")


def main():
    """_main_execution_pyproject_script"""
    filepath = Path("src") / "data" / "posts.json"
    get_posts(filepath)


if __name__ == "__main__":
    main()
