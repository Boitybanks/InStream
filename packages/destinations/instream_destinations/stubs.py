from __future__ import annotations

from instream_shared.errors import UnsupportedProviderError


class _UnimplementedDestination:
    destination_name = "unimplemented"

    def write(self, record: dict) -> None:
        raise UnsupportedProviderError(f"{self.destination_name} destination is not wired up yet")

    def test_connection(self) -> bool:
        raise UnsupportedProviderError(f"{self.destination_name} destination is not wired up yet")


class ExcelDestination(_UnimplementedDestination):
    destination_name = "excel"


class SharePointDestination(_UnimplementedDestination):
    destination_name = "sharepoint"


class SalesforceDestination(_UnimplementedDestination):
    destination_name = "salesforce"


class SAPDestination(_UnimplementedDestination):
    destination_name = "sap"


class DynamicsDestination(_UnimplementedDestination):
    destination_name = "dynamics"


class GoogleSheetsDestination(_UnimplementedDestination):
    destination_name = "google_sheets"
