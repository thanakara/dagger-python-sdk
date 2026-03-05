import asyncio

from dagger_python_sdk.utils import DatabaseSeeder


def main():
    seeder = DatabaseSeeder()
    asyncio.run(seeder.seed())


if __name__ == "__main__":
    main()
