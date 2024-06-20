from enum import StrEnum


class BigQueryFieldMode(StrEnum):
    REQUIRED = "REQUIRED"
    NULLABLE = "NULLABLE"
    REPEATED = "REPEATED"
