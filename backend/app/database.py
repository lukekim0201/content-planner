from sqlmodel import create_engine, Session
from app.config import DATABASE_URL

# SQLite needs this connect_arg when used from multiple threads (TestClient,
# uvicorn's threadpool, etc). Postgres ignores it because the kwarg is only
# passed when the URL is sqlite.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """Convenience for local/dev use (SQLite). In Postgres, use Alembic
    migrations instead — see alembic/versions/."""
    from sqlmodel import SQLModel
    import app.models  # noqa: F401 register models on the metadata

    SQLModel.metadata.create_all(engine)
