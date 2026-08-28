from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from src.api.config import get_settings
from src.api.infrastructure.migrations import run_migrations

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

if "sqlite" in settings.database_url:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass

def init_db() -> None:
    import src.api.infrastructure.models
    Base.metadata.create_all(bind=engine)

    with engine.connect() as connection:
        run_migrations(connection)

    from src.api.infrastructure.models import User
    with SessionLocal() as db:
        admin_exists = db.query(User).filter(User.username == "admin").first()
        if not admin_exists:
            default_admin = User(
                username="admin",
                password_hash="$2b$12$vOm/819ShmsYJ35.YXWX4u77lezA8NGCdiE0GMcuyw2lR/9qpFX.C",
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            db.add(default_admin)
            db.commit()
            print("Default admin user created.")

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
