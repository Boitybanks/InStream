from __future__ import annotations

from sqlalchemy import Engine

from instream_shared.errors import ConfigError

from instream_destinations.base import DestinationConnector
from instream_destinations.csv_destination import CSVDestination
from instream_destinations.stubs import (
    DynamicsDestination,
    ExcelDestination,
    GoogleSheetsDestination,
    SalesforceDestination,
    SAPDestination,
    SharePointDestination,
)

_STUBS = {
    "excel": ExcelDestination,
    "sharepoint": SharePointDestination,
    "salesforce": SalesforceDestination,
    "sap": SAPDestination,
    "dynamics": DynamicsDestination,
    "google_sheets": GoogleSheetsDestination,
}


def get_destination(destination_type: str, config: dict, *, engine: Engine | None = None) -> DestinationConnector:
    if destination_type == "csv":
        return CSVDestination(config["path"])
    if destination_type == "postgres":
        from instream_destinations.postgres_destination import PostgresDestination

        if engine is None:
            raise ConfigError("postgres destination requires an `engine`")
        return PostgresDestination(engine, config["table_name"])
    stub_cls = _STUBS.get(destination_type)
    if stub_cls is not None:
        return stub_cls()
    raise ConfigError(f"Unknown destination_type: {destination_type!r}")
