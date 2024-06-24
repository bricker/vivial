import dataclasses
from typing import TypeVar, Any
import google.cloud.dlp_v2 as dlp

from .config import SHARED_CONFIG
from abc import abstractmethod
from google.cloud.bigquery import SchemaField, SqlTypeNames

client = dlp.DlpServiceClient()

# Convert the project id into a full resource id.
parent = f"projects/{SHARED_CONFIG.google_cloud_project}/locations/global"

def redact(
    rows: list[Any],
) -> str:
    # TODO: update docs
    """Uses the Data Loss Prevention API to deidentify sensitive data in a
    string by redacting matched input values.
    Returns the input `data` with any sensistive info found replaced with '*****'.
    """

    if len(rows) == 0:
        return ""

    fields = [dlp.FieldId(name=field) for field in dataclasses.asdict(rows[0]).keys()]
    formatted_rows = [dlp.Table.Row(values=[dlp.Value(string_value=str(v)) for v in dataclasses.asdict(row).values()]) for row in rows]

    response = client.deidentify_content(
        request=dlp.DeidentifyContentRequest(
            parent=parent,
            deidentify_config=dlp.DeidentifyConfig(
                record_transformations=dlp.RecordTransformations(
                    field_transformations=[
                        dlp.FieldTransformation(
                            fields=fields,
                            info_type_transformations=dlp.InfoTypeTransformations(
                                transformations=[
                                    dlp.InfoTypeTransformations.InfoTypeTransformation(
                                        info_types=[], # NOTE: empty list defaults to all info types
                                        primitive_transformation=dlp.PrimitiveTransformation(
                                            replace_with_info_type_config=dlp.ReplaceWithInfoTypeConfig()
                                        )
                                    )
                                ]
                            )
                        )
                    ],
                )
            ),
            # item=dlp.ContentItem(value=data),
            item=dlp.ContentItem(
                table=dlp.Table( # TODO: convert atom datatype to Table
                    headers=fields,
                    rows=formatted_rows,
                )
            )
        )
    )

    # TODO: gotta convert back to atoms
    return response.item.value

def redact_str(
    data: str,
) -> str:
    """Uses the Data Loss Prevention API to deidentify sensitive data in a
    string by redacting matched input values.
    Returns the input `data` with any sensistive info found replaced with the name
    of the data found.

    e.g. "my ssn is [US_SOCIAL_SECURITY_NUMBER]"
    """
    response = client.deidentify_content(
        request=dlp.DeidentifyContentRequest(
            parent=parent,
            deidentify_config=dlp.DeidentifyConfig(
                info_type_transformations=dlp.InfoTypeTransformations(
                    transformations=[
                        dlp.InfoTypeTransformations.InfoTypeTransformation(
                            primitive_transformation=dlp.PrimitiveTransformation(
                                replace_with_info_type_config=dlp.ReplaceWithInfoTypeConfig()
                            )
                        )
                    ]
                )
            ),
            item=dlp.ContentItem(value=data),
        )
    )

    return response.item.value

