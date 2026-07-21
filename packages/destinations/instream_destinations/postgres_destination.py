from __future__ import annotations

import json

from sqlalchemy import Engine, text


class PostgresDestination:
    """Reference destination: writes each record as a JSONB row into a
    per-destination table. Pack-specific column mapping (`mappings/*.yaml`)
    can layer a typed table on top of this later without changing the
    interface."""

    def __init__(self, engine: Engine, table_name: str) -> None:
        self._engine = engine
        self._table_name = table_name
        self._ensure_table()

    def _ensure_table(self) -> None:
        with self._engine.begin() as conn:
            conn.execute(
                text(
                    f'CREATE TABLE IF NOT EXISTS "{self._table_name}" ('
                    "id SERIAL PRIMARY KEY, payload JSONB NOT NULL, "
                    "written_at TIMESTAMPTZ NOT NULL DEFAULT now())"
                )
            )

    def write(self, record: dict) -> None:
        with self._engine.begin() as conn:
            conn.execute(
                text(f'INSERT INTO "{self._table_name}" (payload) VALUES (CAST(:payload AS JSONB))'),
                {"payload": json.dumps(record)},
            )

    def test_connection(self) -> bool:
        with self._engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
