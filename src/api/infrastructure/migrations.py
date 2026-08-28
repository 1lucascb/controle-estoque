from pathlib import Path
import re

from sqlalchemy import Connection, text


_MIGRATION_PATTERN = re.compile(r"^migration(\d+)\.sql$")
_DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def _migration_files() -> list[tuple[int, Path]]:
    migrations = []
    for path in _DATA_DIR.glob("migration*.sql"):
        match = _MIGRATION_PATTERN.match(path.name)
        if match:
            migrations.append((int(match.group(1)), path))
    return sorted(migrations)


def _execute_script(connection: Connection, sql: str) -> None:
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            connection.exec_driver_sql(statement)


def run_migrations(connection: Connection) -> None:
    connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
    connection.commit()
    try:
        with connection.begin():
            _apply_migrations(connection)
    finally:
        connection.exec_driver_sql("PRAGMA foreign_keys=ON")
        connection.commit()


def _apply_migrations(connection: Connection) -> None:
    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )

    applied_versions = {
        row.version
        for row in connection.execute(text("SELECT version FROM schema_migrations"))
    }

    for version, path in _migration_files():
        if version in applied_versions:
            continue

        print("Executing migration script:", path, version)
        sql = path.read_text(encoding="utf-8")
        _execute_script(connection, sql)
        connection.execute(
            text("INSERT INTO schema_migrations (version) VALUES (:version)"),
            {"version": version},
        )

