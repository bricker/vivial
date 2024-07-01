import dataclasses
import re
from typing import Any, get_args
import google.cloud.dlp_v2 as dlp

from .config import SHARED_CONFIG, EaveEnvironment


# Convert the project id into a full resource id.
parent = f"projects/{SHARED_CONFIG.google_cloud_project}/locations/global"
_key_sep = "."
_regex_safe_key_sep = fr"\{_key_sep}"


def redactable(*args, **kwargs) -> Any:
    redact_meta = {"redactable": True}
    if "metadata" in kwargs:
        kwargs["metadata"].update(redact_meta)
        return dataclasses.field(*args, **kwargs)
    return dataclasses.field(*args, **kwargs, metadata=redact_meta)


class Redactable:
    @classmethod
    def redactable_fields_matchers(cls) -> list[str]:
        """List of all redactable fields, including member objects',
        defined as regex paths. A redactable field being one that
        is assigned with the `redactable()` dataclass field definition.

        e.g.
        ```
        class Mammal(Redactable):
            genus: Genus | None = redactable()
            quantitiy: int
            num_legs : int = redactable(default=4)

        class Canis(Genus, Redactable):
            common_names: list[str] = redactable()
            is_good: bool = True

        Mammal.redactable_fields_matchers()
        ->
        [
            r"genus\.common_names\.[0-9]+",
            r"num_legs",
        ]
        ```
        """
        redact_patterns = []
        if not dataclasses.is_dataclass(cls):
            return redact_patterns
        # TODO: tests
        redactable_fields = [f for f in dataclasses.fields(cls) if f.metadata.get("redactable", False)]
        for field in redactable_fields:
            # field: list[str | Redactable | None] | None
            # [list[..], None]
            typing.get_origin . get_args()
            # [str, Redactable, None]
            typing.get_args()
            # extract sub fields
            if issubclass(field.type, Redactable):
                redact_patterns = [
                    *redact_patterns,
                    # escape _key_sep since it's a dot rn
                    *[rf"{field.name}{_regex_safe_key_sep}{sub_pat}" for sub_pat in field.type.redactable_fields_matchers()],
                ]
            elif isinstance(field.type, list):
                # handle indexes
                if issubclass(get_args(field.type)[0], Redactable):
                    redact_patterns = [
                        *redact_patterns,
                        # escape _key_sep since it's a dot rn
                        *[rf"{field.name}{_regex_safe_key_sep}[0-9]+"],  # TODO: reccurse tack on things if any
                    ]
                else:
                    redact_patterns.append(rf"{field.name}{_regex_safe_key_sep}[0-9]+")
            elif isinstance(field.type, dict):
                redact_patterns = [
                    *redact_patterns,
                    *[rf'{field.name}{_regex_safe_key_sep}".*?(?="{_regex_safe_key_sep})"'],  # TODO: recurse tack on things if any
                ]
            else:
                redact_patterns.append(field.name)

        return redact_patterns


def _flatten_to_dict(obj: Any) -> dict[str, str | bool | int | float]:
    """
    Convert an object and any nested fields to a flat dict where
    keys describe the path of field reference to reach the value.

    e.g.
    Mammal(genus=Canis(common_names=["dog","wolf"]), quantity=10000)
    ->
    {
        "genus.common_names.0": "dog",
        "genus.common_names.1": "wolf",
        "quantity": 10000
    }
    """
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


def _ensure_uniform_keys(flattened_objs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not flattened_objs:
        return []

    all_keys = set().union(*(d.keys() for d in flattened_objs))
    # re-write all flat objs, adding None value for keys original obj didnt have
    return [{key: d.get(key, None) for key in all_keys} for d in flattened_objs]


def _write_flat_data_to_object(data: dict[str, Any], obj: Any) -> None:
    """Writes input `data` to the provided `obj` reference, using `data` keys
    as the path to the property to write the dict value to."""
    for key_path, value in data.items():
        # TODO: will censored float/int values get screwed by this check?
        if not value:
            # no value present to write (or key_path may not be valid for this obj)
            continue

        path_segments = key_path.split(_key_sep)
        obj_drill = obj
        for i in range(len(path_segments)):
            key = path_segments[i]
            if isinstance(obj_drill, list):
                # list key must be numeric
                if key.isnumeric():
                    key = int(key)
                else:
                    # TODO: something has gone horribly wrong
                    break

                if i == len(path_segments) - 1:
                    # end of key path; assign value
                    obj_drill[key] = value
                else:
                    obj_drill = obj_drill[key]
            elif isinstance(obj_drill, dict):
                if i == len(path_segments) - 1:
                    # end of key path; assign value
                    obj_drill[key] = value
                else:
                    obj_drill = obj_drill[key]
            else:  # handle class object
                if i == len(path_segments) - 1:
                    # end of key path; assign value
                    setattr(obj_drill, key, value)
                else:
                    obj_drill = getattr(obj_drill, key)


async def redact_atoms(atoms: list[Any]) -> None:
    """Uses the Data Loss Prevention API to deidentify sensitive data in a
    list of Atoms. Alters the list `atoms` in place.

    NOTE: 3000 redactions limit?
    https://cloud.google.com/sensitive-data-protection/docs/deidentify-sensitive-data#findings-limit
    """

    if SHARED_CONFIG.eave_env == EaveEnvironment.test:
        print("skipping redaction...")
        return

    if len(atoms) == 0:
        return

    # flatten atoms into list of uniform dicts, all w/ same keys
    flat_atoms = _ensure_uniform_keys([_flatten_to_dict(atom) for atom in atoms])

    # map to dlp types
    all_columns_str = list(flat_atoms[0].keys())
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
                row_values.append(dlp.Value(string_value=str(val) if val else ""))

        dlp_rows.append(dlp.Table.Row(values=row_values))

    # extract headers we want redacted from current flat atoms
    redactable_header_matchers = type(atoms[0]).redactable_fields_matchers()
    headers_to_redact = [
        header for header in flat_atoms[0].keys() if any(re.match(pat, header) for pat in redactable_header_matchers)
    ]

    client = dlp.DlpServiceAsyncClient()
    response = await client.deidentify_content(
        request=dlp.DeidentifyContentRequest(
            parent=parent,
            deidentify_config=dlp.DeidentifyConfig(
                record_transformations=dlp.RecordTransformations(
                    field_transformations=[
                        dlp.FieldTransformation(
                            fields=headers_to_redact,
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

    # write redacted response data back to original atoms
    for i in range(len(atoms)):
        # convert dlp.Row back to plain dict
        data = {}
        for j in range(len(all_columns_str)):
            v = response.item.table.rows[i].values[j]
            data[all_columns_str[j]] = (
                v.string_value
                or v.integer_value
                or v.float_value
                or v.boolean_value
                # when no other truthy values to write, default to None
                or None
            )
        _write_flat_data_to_object(data, atoms[i])


async def redact_str(
    data: str,
) -> str:
    """Uses the Data Loss Prevention API to deidentify sensitive data in a
    string by redacting matched input values.
    Returns the input `data` with any sensistive info found replaced with the name
    of the data found.

    e.g. "my ssn is [US_SOCIAL_SECURITY_NUMBER]"
    """
    if SHARED_CONFIG.eave_env == EaveEnvironment.test:
        print("skipping redaction...")
        return data

    client = dlp.DlpServiceAsyncClient()

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
