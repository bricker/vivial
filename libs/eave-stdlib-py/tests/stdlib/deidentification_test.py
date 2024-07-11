import dataclasses
from typing import Any
import unittest.mock

from eave.stdlib.deidentification import (
    REDACTABLE,
    _flatten_to_dict,
    _headers_to_redact,
    _redactable_fields_matchers,
    _write_flat_data_to_object,
    redact_atoms,
)

from .base import StdlibBaseTestCase


@dataclasses.dataclass
class Spec:
    info: str | None = dataclasses.field(metadata={REDACTABLE: True})


@dataclasses.dataclass
class Basket:
    thread_count: int
    woven_underwater: bool = dataclasses.field(metadata={REDACTABLE: True})
    price: str | None = dataclasses.field(metadata={REDACTABLE: True})
    specs: dict[str, Spec] = dataclasses.field(metadata={REDACTABLE: True})


@dataclasses.dataclass
class WeavingSpider:
    genus: str
    favorite_legs: list[int] | None = dataclasses.field(metadata={REDACTABLE: True})
    name: str = dataclasses.field(metadata={REDACTABLE: True})


@dataclasses.dataclass
class Tool:
    type: str


@dataclasses.dataclass
class BasketWeaver:
    tools: list[Tool]
    name: str = dataclasses.field(metadata={REDACTABLE: True})
    helpers: list[WeavingSpider] | None = dataclasses.field(metadata={REDACTABLE: True})
    latest_work: Basket = dataclasses.field(metadata={REDACTABLE: True})


class DeidentificationTest(StdlibBaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.stop_patch("dlp.deidentify_content")

    def test_object_flattening(self) -> None:
        obj = BasketWeaver(
            tools=[Tool(type="knitting needles"), Tool(type="banana")],
            name="Fred",
            helpers=[
                WeavingSpider(genus="bug", favorite_legs=[4, 9], name="Anji"),
                WeavingSpider(genus="orb weaver", favorite_legs=None, name="Arachne"),
            ],
            latest_work=Basket(
                thread_count=3,
                woven_underwater=True,
                price=None,
                specs={"1": Spec(info="well crafted"), "2": Spec(info=None)},
            ),
        )

        flat = _flatten_to_dict(obj)

        assert flat == {
            "tools.0.type": "knitting needles",
            "tools.1.type": "banana",
            "name": "Fred",
            "helpers.0.genus": "bug",
            "helpers.0.favorite_legs.0": 4,
            "helpers.0.favorite_legs.1": 9,
            "helpers.0.name": "Anji",
            "helpers.1.genus": "orb weaver",
            "helpers.1.favorite_legs": None,
            "helpers.1.name": "Arachne",
            "latest_work.thread_count": 3,
            "latest_work.woven_underwater": True,
            "latest_work.price": None,
            'latest_work.specs."1".info': "well crafted",
            'latest_work.specs."2".info': None,
        }

    def test_flatten_dict_member(self) -> None:
        @dataclasses.dataclass
        class Foo:
            d: dict[str, str]

        f = Foo(d={"test": "object", "looking": "good", 'someth"ing': "janky"})

        assert _flatten_to_dict(f) == {'d."test"': "object", 'd."looking"': "good", 'd."someth"ing"': "janky"}

    def test_object_write_back(self) -> None:
        obj = BasketWeaver(
            tools=[Tool(type="knitting needles"), Tool(type="banana")],
            name="Fred",
            helpers=[
                WeavingSpider(genus="bug", favorite_legs=[4, 9], name="Anji"),
                WeavingSpider(genus="orb weaver", favorite_legs=None, name="Arachne"),
            ],
            latest_work=Basket(
                thread_count=3,
                woven_underwater=True,
                price=None,
                specs={"1": Spec(info="well crafted"), "2": Spec(info=None)},
            ),
        )

        write_data = {
            "tools.0.type": "[REDACT]",
            "tools.1.type": "banana",
            "name": "[NAME]",
            "helpers.0.genus": "bug",
            "helpers.0.favorite_legs.0": 4,
            "helpers.0.favorite_legs.1": 9,
            "helpers.0.name": "Anji",
            "helpers.1.genus": "orb weaver",
            "helpers.1.favorite_legs": None,
            "helpers.1.name": "Arachne",
            "latest_work.thread_count": 3,
            "latest_work.woven_underwater": True,
            "latest_work.price": None,
            'latest_work.specs."1".info': "[CREDIT_CARD]",
            'latest_work.specs."2".info': None,
        }
        _write_flat_data_to_object(
            data=write_data,
            obj=obj,
        )

        flat_modified_obj = _flatten_to_dict(obj)
        assert flat_modified_obj == write_data

    def test_redactable_field_identification(self) -> None:
        assert sorted(_redactable_fields_matchers(Basket)) == sorted(
            [
                r"woven_underwater",
                r"price",
                r'specs\.".*?(?="\.)"\.info',
            ]
        ), "Single object matchers did not match expected"
        assert sorted(_redactable_fields_matchers(BasketWeaver)) == sorted(
            [
                r"name",
                r"latest_work\.woven_underwater",
                r"latest_work\.price",
                r"helpers\.[0-9]+\.favorite_legs\.[0-9]+",
                r"helpers\.[0-9]+\.name",
                r'latest_work\.specs\.".*?(?="\.)"\.info',
            ]
        ), "Nested object and list matchers did not match expected"

    def test_field_flat_path_matchers(self) -> None:
        o = BasketWeaver(
            tools=[Tool(type="knitting needles"), Tool(type="banana")],
            name="Fred",
            helpers=[
                WeavingSpider(genus="bug", favorite_legs=[4, 9], name="Anji"),
                WeavingSpider(genus="orb weaver", favorite_legs=None, name="Arachne"),
            ],
            latest_work=Basket(
                thread_count=3,
                woven_underwater=True,
                price=None,
                specs={"1": Spec(info="well crafted"), "2": Spec(info=None)},
            ),
        )
        assert sorted(_headers_to_redact(atom_type=type(o), flat_keys=_flatten_to_dict(o).keys())) == sorted(
            [
                "name",
                "helpers.0.favorite_legs.0",
                "helpers.0.favorite_legs.1",
                "helpers.0.name",
                "helpers.1.name",
                "latest_work.woven_underwater",
                "latest_work.price",
                'latest_work.specs."1".info',
                'latest_work.specs."2".info',
            ]
        )

    async def test_dlp_integration(self) -> None:
        atoms = [
            BasketWeaver(
                tools=[Tool(type="knitting needles"), Tool(type="drill")],
                name="Fred",
                helpers=[
                    WeavingSpider(genus="bug", favorite_legs=[4, 9], name="Anji"),
                    WeavingSpider(genus="orb weaver", favorite_legs=None, name="Arachne"),
                ],
                latest_work=Basket(
                    thread_count=3,
                    woven_underwater=True,
                    price=None,
                    specs={"ccn": Spec(info="4263982640269299"), "2": Spec(info="10 years old")},
                ),
            ),
            BasketWeaver(
                tools=[],
                name="Samantha",
                helpers=[
                    WeavingSpider(genus="grasshopper", favorite_legs=[], name="Phil"),
                ],
                latest_work=Basket(
                    thread_count=3,
                    woven_underwater=False,
                    price="$10000",
                    specs={"rookie.mistake": Spec(info="poorly crafted")},
                ),
            ),
        ]

        await redact_atoms(atoms)
        updated_flat = [_flatten_to_dict(a) for a in atoms]

        assert updated_flat == [
            {
                "tools.0.type": "knitting needles",
                "tools.1.type": "drill",
                "name": "[PERSON_NAME]",
                "helpers.0.genus": "bug",
                "helpers.0.favorite_legs.0": 4,
                "helpers.0.favorite_legs.1": 9,
                "helpers.0.name": "[PERSON_NAME]",
                "helpers.1.genus": "orb weaver",
                "helpers.1.favorite_legs": None,
                "helpers.1.name": "[LOCATION]",
                "latest_work.thread_count": 3,
                "latest_work.woven_underwater": True,
                "latest_work.price": None,
                'latest_work.specs."ccn".info': "[CREDIT_CARD_NUMBER]",
                'latest_work.specs."2".info': "[AGE]",
            },
            {
                "name": "[PERSON_NAME]",
                "helpers.0.genus": "grasshopper",
                "helpers.0.name": "[PERSON_NAME]",
                "latest_work.thread_count": 3,
                "latest_work.woven_underwater": False,
                "latest_work.price": "$10000",
                'latest_work.specs."rookie.mistake".info': "poorly crafted",
            },
        ]

    def test_handle_key_sep_in_dict_key(self) -> None:
        @dataclasses.dataclass
        class Foo:
            obj: Any

        f = Foo(
            obj={
                "fizz.buzz": "bar",
                "foo.bar": Foo(obj={}),
                "hum.drum": Foo(obj=4),
            }
        )
        flat = _flatten_to_dict(f)

        # alter flat and write back
        flat['obj."fizz.buzz"'] = "bazz"
        flat['obj."foo.bar".obj."some"'] = "thing"
        flat['obj."hum.drum".obj'] = 5
        _write_flat_data_to_object(
            data=flat,
            obj=f,
        )

        assert f.obj["fizz.buzz"] == "bazz", "altered flat data not written back correctly"
        assert f.obj["hum.drum"].obj == 5, "primitive data not written back correctly"
        assert f.obj["foo.bar"].obj["some"] == "thing", "double nested flat data not written back correctly"
