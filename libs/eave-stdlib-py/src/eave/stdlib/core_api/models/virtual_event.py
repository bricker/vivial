import uuid

from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.core.internal.atoms.shared import BigQueryFieldMode
from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel


class VirtualEventField(BaseResponseModel):
    name: str
    description: str | None
    field_type: SqlTypeNames  # STRING, INTEGER, RECORD, etc.
    mode: BigQueryFieldMode | None  # NULLABLE, REQUIRED, REPEATED
    fields: list["VirtualEventField"] | None = None  # recursive nested fields

    @classmethod
    def from_bq_field(cls, field: SchemaField) -> "VirtualEventField":
        return cls(
            name=field.name,
            description=field.description,
            field_type=field.field_type,
            mode=field.mode,
            fields=[VirtualEventField.from_bq_field(cfield) for cfield in field.fields]
            if field.field_type == SqlTypeNames.RECORD
            else None,
        )


class VirtualEventPeek(BaseResponseModel):
    id: uuid.UUID
    view_id: str
    readable_name: str
    description: str | None


class VirtualEventDetails(BaseResponseModel):
    id: uuid.UUID
    view_id: str
    readable_name: str
    description: str | None
    fields: list[VirtualEventField]


class VirtualEventDetailsQueryInput(BaseInputModel):
    id: uuid.UUID
