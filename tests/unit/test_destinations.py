import csv
import uuid

from instream_destinations import CSVDestination


def test_csv_destination_writes_header_and_rows(tmp_path):
    path = tmp_path / "out.csv"
    destination = CSVDestination(str(path))
    destination.write({"a": "1", "b": "2"})
    destination.write({"a": "3", "b": "4"})

    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows == [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]
    assert destination.test_connection() is True


def test_postgres_destination_writes_jsonb_row():
    from sqlalchemy import create_engine

    from instream_destinations.postgres_destination import PostgresDestination
    from instream_db.session import DATABASE_URL

    engine = create_engine(DATABASE_URL)
    table_name = f"test_destination_{uuid.uuid4().hex[:8]}"
    destination = PostgresDestination(engine, table_name)
    assert destination.test_connection() is True

    destination.write({"hello": "world"})

    from sqlalchemy import text

    with engine.begin() as conn:
        row = conn.execute(text(f'SELECT payload FROM "{table_name}"')).fetchone()
        assert row[0] == {"hello": "world"}
        conn.execute(text(f'DROP TABLE "{table_name}"'))
