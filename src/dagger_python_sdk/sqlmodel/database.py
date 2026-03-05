from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DB_URL = "sqlite:///./src/data/dag.db"

engine = create_engine(
    SQLALCHEMY_DB_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency function that provides sessions to routes"""

    with SessionLocal() as db:
        yield db
