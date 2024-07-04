import dataclasses
import re
from types import NoneType
from typing import Any, get_args, get_origin
from collections.abc import Iterable
import google.cloud.dlp_v2 as dlp

from .config import SHARED_CONFIG


# Convert the project id into a full resource id.
parent = f"projects/{SHARED_CONFIG.google_cloud_project}/locations/global"
_key_sep = "."
_regex_safe_key_sep = rf"\{_key_sep}"

REDACTABLE = "redactable"


def _redactable_field_matchers_kernel(t: Any, prefix: str = "", redact_patterns: list[str] | None = None) -> list[str]:
    if redact_patterns is None:
        redact_patterns = []
    origin = get_origin(t)
    args = get_args(t)
    chained_prefix = rf"{prefix}{_regex_safe_key_sep}" if prefix else ""

    if origin is list:
        # scan element type(s)
        for element_type in args:
            _redactable_field_matchers_kernel(
                t=element_type,
                prefix=rf"{chained_prefix}[0-9]+",
                redact_patterns=redact_patterns,
            )
    elif origin is dict:
        # scan value type(s)
        if len(args) >= 2:
            #      args[0] args[1]
            # dict[str,    str]
            _redactable_field_matchers_kernel(
                t=args[1],
                prefix=rf'{chained_prefix}".*?(?="{_regex_safe_key_sep})"',
                redact_patterns=redact_patterns,
            )
    elif args:
        # handle Unioned types individually
        for utype in args:
            _redactable_field_matchers_kernel(utype, prefix, redact_patterns)
    elif dataclasses.is_dataclass(t):
        # extract sub fields
        redactable_fields = [f for f in dataclasses.fields(t) if f.metadata.get(REDACTABLE, False)]
        for field in redactable_fields:
            _redactable_field_matchers_kernel(
                t=field.type,
                prefix=rf"{chained_prefix}{field.name}",
                redact_patterns=redact_patterns,
            )
    elif t is not NoneType:
        # non-None primitive type; we've reached end of a field path
        redact_patterns.append(prefix)

    return redact_patterns


def _redactable_fields_matchers(t: Any) -> list[str]:
    """List of all redactable fields, including member objects',
    defined as regex paths. A redactable field being one that
    is assigned with the `{REDACTABLE: True}` metadata in the
    dataclass field definition.

    Parameters:
        `t`: a type class. as returned from `type()`, or a class name

    e.g.
    ```
    class Mammal(Redactable):
        genus: Genus | None = dataclasses.field(metadata={REDACTABLE: True})
        quantitiy: int
        num_legs : int = dataclasses.field(metadata={REDACTABLE: True})

    class Canis(Genus, Redactable):
        common_names: list[str] = dataclasses.field(metadata={REDACTABLE: True})
        is_good: bool = True

    redactable_fields_matchers(Mammal)
    ->
    [
        r"genus\\.common_names\\.[0-9]+",
        r"num_legs",
    ]
    ```
    """
    return _redactable_field_matchers_kernel(t)


def _asdict(o: Any) -> dict[str, Any]:
    """Convert `o` to dict, stopping after the root
    level. Expects `o` to be a dataclass instance.

    This is a simplified version of `dataclasses.asdict`
    that doesn't recursively dictify all member objects.
    (This is desirable so we can differentiate between
    dict members and class object members later on.)"""
    return {f.name: getattr(o, f.name) for f in dataclasses.fields(o)}


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
    if not dataclasses.is_dataclass(obj):
        return flat

    # (prefix, key/index, value)
    items: list[tuple[str, Any, Any]] = [("", k, v) for k, v in _asdict(obj).items()]
    while items:
        prefix, key, val = items.pop(0)
        if isinstance(val, (bool, int, float, str, NoneType)):
            flat[f"{prefix}{key}"] = val
        elif isinstance(val, list):
            # extract all list items using index as key
            items.extend([(f"{prefix}{key}{_key_sep}", i, v) for i, v in enumerate(val)])
        else:
            # flatten object into key/value pairs
            if not isinstance(val, dict):
                items.extend([(f"{prefix}{key}{_key_sep}", k, v) for k, v in _asdict(val).items()])
            else:
                items.extend([(f"{prefix}{key}{_key_sep}", f'"{k}"', v) for k, v in val.items()])

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

        # custom str split to not split on _key_sep characters between quotes
        path_segments = []
        in_quote = False
        seg_builder = []
        for i, char in enumerate(key_path):
            if char == _key_sep and not in_quote:
                path_segments.append("".join(seg_builder))
                seg_builder = []
                continue
            if char == '"' and len(seg_builder) == 0:
                in_quote = True
            if char == '"' and (i + 1 >= len(key_path) or key_path[i + 1] == _key_sep):
                in_quote = False

            seg_builder.append(char)
        path_segments.append("".join(seg_builder))

        obj_drill = obj
        for i in range(len(path_segments)):
            key = path_segments[i].strip('"')
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


def _headers_to_redact(atom_type: Any, flat_keys: Iterable[str]) -> list[str]:
    """From a collection of keys of a flattened Atom/dataclass, return
    the subset of those keys that should be redacted, as defined in the
    `atom_type` dataclass field metadata."""
    # extract headers we want redacted from current flat atoms
    redactable_header_matchers = _redactable_fields_matchers(atom_type)
    return [header for header in flat_keys if any(re.match(pat, header) for pat in redactable_header_matchers)]


async def redact_atoms(atoms: list[Any]) -> None:
    """Uses the Data Loss Prevention API to deidentify sensitive data in a
    list of Atoms. Alters the list `atoms` in place.

    NOTE: 3000 redactions limit?
    https://cloud.google.com/sensitive-data-protection/docs/deidentify-sensitive-data#findings-limit
    """
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

    headers_to_redact = [
        dlp.FieldId(name=header) for header in _headers_to_redact(type(atoms[0]), flat_atoms[0].keys())
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
