import json
import asyncio
import contextlib

from pathlib import Path

import httpx


class DatabaseSeeder:
    USERS_URL = "http://localhost:8000/api/users"
    POSTS_URL = "http://localhost:8000/api/posts"

    def __init__(self, json_files_path: Path = Path("src") / "data") -> None:
        self.users_json_path = json_files_path / "users.json"
        self.posts_json_path = json_files_path / "posts.json"

        for path in (self.users_json_path, self.posts_json_path):
            if not path.exists():
                raise FileNotFoundError(f"Required data file not found: {path}")

        self._load_json()

    def _load_json(self) -> None:
        """Load users and posts from their respective JSON files."""
        with contextlib.ExitStack() as stack:
            users_f, posts_f = [
                stack.enter_context(path.open("r"))
                for path in (self.users_json_path, self.posts_json_path)
            ]
            self.users: list[dict] = json.load(users_f)
            self.posts: list[dict] = json.load(posts_f)

    async def _post_item(
        self, client: httpx.AsyncClient, url: str, item: dict, label: str
    ) -> None:
        """POST a single item to the given URL."""
        response = await client.post(url, json=item)
        response.raise_for_status()

    async def _post_items(
        self, client: httpx.AsyncClient, url: str, items: list[dict], label: str
    ) -> None:
        """POST all items concurrently to the given URL."""
        tasks = [self._post_item(client, url, item, label) for item in items]
        await asyncio.gather(*tasks)

    async def seed(self) -> None:
        """Seed the database with users and posts."""
        async with httpx.AsyncClient() as client:
            await self._post_items(client, self.USERS_URL, self.users, "user")
            await self._post_items(client, self.POSTS_URL, self.posts, "post")
