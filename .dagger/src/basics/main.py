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
    def fastapi(self) -> dagger.Container:
        pass
