import dagger
from dagger import dag, function, object_type


@object_type
class Basics:
    @function
    async def run_script(self, worktree: dagger.Directory) -> str:
        """Run scripts from ../scripts"""
        return await (
            dag.container()
            .from_("alpine:latest")
            .with_exec(["apk", "add", "bash"])
            .with_directory("/worktree", worktree)
            .with_workdir("/worktree")
            .with_exec(["scripts/dagger-simple"])
            .stdout()
        )

    @function
    def env(self) -> dagger.Container:
        """Checkout CACHE technique (try multiple times)"""
        apt_cache = dag.cache_volume("apt-cache")
        return (
            dag.container()
            .from_("debian:latest")
            .with_mounted_cache("/var/cache/apt/archives", apt_cache)
            .with_exec(["apt-get", "update"])
            .with_exec(["apt-get", "install", "--yes", "mariadb-server", "jq"])
        )

    @function
    def fastapi_server(self, source: dagger.Directory) -> dagger.Service:
        """
        Build and serve the FastAPI application as a Dagger Service.

        ```bash
        dagger call fastapi-server --source . up --ports 8000:800
        ```
        """

        BACKEND_DIR = "src/dagger_python_sdk/backend"

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
                    "{}/app.py".format(BACKEND_DIR),
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8000",
                ]
            )
        )
