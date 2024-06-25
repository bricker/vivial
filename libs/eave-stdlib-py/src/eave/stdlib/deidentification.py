import dataclasses
from typing import Any
import google.cloud.dlp_v2 as dlp

from .config import SHARED_CONFIG

client = dlp.DlpServiceAsyncClient()

# Convert the project id into a full resource id.
parent = f"projects/{SHARED_CONFIG.google_cloud_project}/locations/global"
_key_sep = "."


def _flatten_to_dict(obj: Any) -> dict[str, str | bool | int | float]:
    flat = {}
    # (prefix, key/index, value)
    items: list[tuple[str, Any, Any]] = [("", k, v) for k, v in dataclasses.asdict(obj).items()]
    while items:
        prefix, key, val = items.pop(0)
        if val is None or isinstance(val, (bool, int, float, str)):
            flat[f"{prefix}{key}"] = val
        elif isinstance(val, list):
            # extract all list items using index as key
            items.extend([(f"{prefix}{key}{_key_sep}", i, v) for i, v in enumerate(val)])
        else:
            # flatten object into key/value pairs
            d = val
            if not isinstance(d, dict):
                d = dataclasses.asdict(val)
            items.extend([(f"{prefix}{key}{_key_sep}", k, v) for k, v in d.items()])

    return flat


def _write_flat_data_to_object(data: dict[str, Any], obj: Any) -> None:
    pass


async def redact_atoms(
    atoms: list[
        Any
    ],  # TODO: we probs need ref to og type inorder to unflatten? or do we just write back to og obj w/ flat as mapping?
) -> None:
    # TODO: update docs
    """Uses the Data Loss Prevention API to deidentify sensitive data in a


    NOTE: 3000 redactions limit?
    https://cloud.google.com/sensitive-data-protection/docs/deidentify-sensitive-data#findings-limit
    """

    if len(atoms) == 0:
        return

    # flatten atom dict
    flat_atoms = [_flatten_to_dict(atom) for atom in atoms]

    # map to dlp types
    # TODO: will empty lists, or None values fuck w/ the keys present for each entry?
    all_columns_str = flat_atoms[0].keys()
    dlp_rows = []
    for flat_atom in flat_atoms:
        row_values = []
        for col_key in all_columns_str:
            val = flat_atom[col_key]
            if isinstance(val, bool):
                row_values.append(dlp.Value(boolean_value=val))
            elif isinstance(val, int):
                row_values.append(dlp.Value(integer_value=val))
            elif isinstance(val, float):
                row_values.append(dlp.Value(float_value=val))
            else:
                row_values.append(dlp.Value(string_value=str(val)))

        dlp_rows.append(dlp.Table.Row(values=row_values))

    response = await client.deidentify_content(
        request=dlp.DeidentifyContentRequest(
            parent=parent,
            deidentify_config=dlp.DeidentifyConfig(
                record_transformations=dlp.RecordTransformations(
                    field_transformations=[
                        dlp.FieldTransformation(
                            fields=[
                                # TODO: fields to senseor
                            ],
                            info_type_transformations=dlp.InfoTypeTransformations(
                                transformations=[
                                    dlp.InfoTypeTransformations.InfoTypeTransformation(
                                        info_types=[],  # NOTE: empty list defaults to all info types
                                        primitive_transformation=dlp.PrimitiveTransformation(
                                            replace_with_info_type_config=dlp.ReplaceWithInfoTypeConfig()
                                        ),
                                    )
                                ]
                            ),
                        )
                    ],
                )
            ),
            item=dlp.ContentItem(
                table=dlp.Table(
                    headers=[dlp.FieldId(name=col_name) for col_name in all_columns_str],
                    rows=dlp_rows,
                )
            ),
        )
    )

    # TODO: gotta convert back to atoms
    print(response.item)
    for i in range(len(atoms)):
        _write_flat_data_to_object(response.item.table.rows[i], atoms[i])


async def redact_str(
    data: str,
) -> str:
    """Uses the Data Loss Prevention API to deidentify sensitive data in a
    string by redacting matched input values.
    Returns the input `data` with any sensistive info found replaced with the name
    of the data found.

    e.g. "my ssn is [US_SOCIAL_SECURITY_NUMBER]"
    """
    response = await client.deidentify_content(
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
