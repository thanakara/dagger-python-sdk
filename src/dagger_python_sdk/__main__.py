import sys
import logging

from pathlib import Path

from omegaconf import OmegaConf

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s]:\n%(message)s",
    handlers=[logging.StreamHandler(stream=sys.stdout)],
)


def get_posts(filepath: Path | str) -> None:
    """Gets all posts from JSON file"""
    if filepath.exists():
        posts = OmegaConf.load(filepath)
        logging.info(OmegaConf.to_yaml(posts))
    else:
        logging.error("File Not Found")


def main():
    """_main_execution_pyproject_script"""
    filepath = Path("src") / "data" / "posts.json"
    get_posts(filepath)


if __name__ == "__main__":
    main()
