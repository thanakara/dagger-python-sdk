from pathlib import Path
from typing import Annotated

import dagger
from dagger import DefaultPath, Doc, Ignore, dag, function, object_type

BACKEND_DIR = Path("src") / "dagger_python_sdk" / "backend"

SourceDir = Annotated[
    dagger.Directory,
    DefaultPath("/"),
    Doc("project source directory"),
    Ignore([".venv", "**/__pycache__", "**/*.pyc", ".git", ".pytest_cache"]),
]


@object_type
class Basics:
    @function
    def base(
        self,
        source: SourceDir,
    ) -> dagger.Container:
        """Shared Python base with uv and dependencies installed"""

        uv_cache = dag.cache_volume("uv-cache")
        venv_cache = dag.cache_volume("venv-cache")

        return (
            dag.container()
            .from_("python:3.12-slim")
            .with_exec(["pip", "install", "uv"])
            .with_directory(
                path="/app",
                source=source,
            )
            .with_workdir("/app")
            .with_mounted_cache("/root/.cache/uv", uv_cache)
            .with_mounted_cache("/app/.venv", venv_cache)
            .with_exec(["uv", "sync"])
        )

    @function
    def fastapi_server(
        self,
        source: SourceDir,
    ) -> dagger.Service:
        """
        Build and serve the FastAPI application as a Dagger Service.

        ```bash
        dagger call fastapi-server up --ports 8000:8000
        ```
        """
        return (
            self.base(source=source)
            .with_exposed_port(8000)
            .as_service(
                args=[
                    "uv",
                    "run",
                    "fastapi",
                    "run",
                    BACKEND_DIR.joinpath("app.py").as_posix(),
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8000",
                ],
            )
        )
