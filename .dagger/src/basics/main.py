from pathlib import Path
from typing import Annotated

import dagger
from dagger import DefaultPath, Doc, dag, function, object_type

BACKEND_DIR = Path("src") / "dagger_python_sdk" / "backend"


@object_type
class Basics:
    @function
    def base(self) -> dagger.Container:
        """Shared Debian base with apt cache and common tools"""
        apt_cache = dag.cache_volume("apt-cache")
        return (
            dag.container()
            .from_("debian:bookworm-slim")
            .with_mounted_cache("/var/cache/apt/archives", apt_cache)
            .with_exec(["apt-get", "update"])
            .with_exec(["apt-get", "install", "--yes", "git", "jq"])
        )

    @function
    async def run_script(
        self,
        source: Annotated[
            dagger.Directory, DefaultPath("/"), Doc("repo root containing scripts")
        ],
    ) -> str:
        """Run scripts/dagger-simple from the worktree"""
        return await (
            dag.container()
            .from_("alpine:3.19")
            .with_exec(["apk", "add", "bash", "dos2unix"])
            .with_directory("/source", source)
            .with_workdir("/source")
            .with_exec(["dos2unix", "scripts/dagger-simple"])
            .with_exec(["scripts/dagger-simple"])
            .stdout()
        )

    @function
    def fastapi_server(
        self,
        source: Annotated[
            dagger.Directory, DefaultPath("/"), Doc("project source directory")
        ],
    ) -> dagger.Service:
        """
        Build and serve the FastAPI application as a Dagger Service.

        ```bash
        dagger call fastapi-server up --ports 8000:8000
        ```
        """
        return (
            dag.container()
            .from_("python:3.12-slim")
            .with_exec(["pip", "install", "uv"])
            .with_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["uv", "sync"])
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
