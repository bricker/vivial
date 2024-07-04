import dataclasses
from eave.stdlib.deidentification import (
    REDACTABLE,
    _flatten_to_dict,
    _headers_to_redact,
    _write_flat_data_to_object,
    _redactable_fields_matchers,
    redact_atoms,
)

from eave.core.internal.atoms.models.api_payload_types import CurrentPageProperties, TargetProperties
from eave.core.internal.atoms.controllers.browser_events import BrowserEventAtom
from eave.core.internal.atoms.models.db_record_fields import (
    CurrentPageRecordField,
    MultiScalarTypeKeyValueRecordField,
    TargetRecordField,
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
    def test_object_flattening(self) -> None:
        obj = BrowserEventAtom(
            action="Bryan Cameron Ricker is my name!",
            timestamp=None,
            session=None,
            account=None,
            visitor_id="23d35726-3f73-4041-a724-b788c0b12b97",
            traffic_source=None,
            target=TargetRecordField.from_api_resource(
                TargetProperties.from_api_payload(
                    {
                        "type": "x",
                        "id": "xx",
                        "content": "xxx",
                        "attributes": {},
                    }
                )
            ),
            current_page=CurrentPageRecordField.from_api_resource(
                CurrentPageProperties.from_api_payload(
                    {
                        "url": "https://sensitive_domain.com/your_credit_card_number?ccn=3742-0454-5540-0126",
                        "title": "Your Credit Card Number",
                    }
                )
            ),
            device=None,
            geo=None,
            extra=MultiScalarTypeKeyValueRecordField.list_from_scalar_dict(
                {
                    "password": "sddf89sdfd89dsafh9sd",
                    "ethnicity": "White",
                }
            ),
            client_ip=None,
        )

        result = _flatten_to_dict(obj)

        assert result == {
            "action": "Bryan Cameron Ricker is my name!",
            "timestamp": None,
            "session": None,
            "account": None,
            "visitor_id": "23d35726-3f73-4041-a724-b788c0b12b97",
            "traffic_source": None,
            "target.type": "x",
            "target.id": "xx",
            "target.content": "xxx",
            "target.attributes": None,
            "current_page.url.raw": "https://sensitive_domain.com/your_credit_card_number?ccn=3742-0454-5540-0126",
            "current_page.url.protocol": "https",
            "current_page.url.domain": "sensitive_domain.com",
            "current_page.url.path": "/your_credit_card_number",
            "current_page.url.hash": None,
            "current_page.url.query_params.0.key": "ccn",
            "current_page.url.query_params.0.value": "3742-0454-5540-0126",
            "current_page.title": "Your Credit Card Number",
            "current_page.pageview_id": None,
            "device": None,
            "geo": None,
            "extra.0.key": "password",
            "extra.0.value.string_value": "sddf89sdfd89dsafh9sd",
            "extra.0.value.bool_value": None,
            "extra.0.value.numeric_value": None,
            "extra.1.value.bool_value": None,
            "extra.1.value.numeric_value": None,
            "extra.1.key": "ethnicity",
            "extra.1.value.string_value": "White",
            "client_ip": None,
        }

    def test_flatten_dict_member(self) -> None:
        @dataclasses.dataclass
        class Foo:
            d: dict[str, str]

        f = Foo(d={"test": "object", "looking": "good", 'someth"ing': "janky"})

        assert _flatten_to_dict(f) == {'d."test"': "object", 'd."looking"': "good", 'd."someth"ing"': "janky"}

    def test_object_write_back(self) -> None:
        obj = BrowserEventAtom(
            action="vote for Jeb! Bush",
            timestamp=None,
            session=None,
            account=None,
            visitor_id="23d35726-3f73-4045-a724-b788c0b12b97",
            traffic_source=None,
            target=TargetRecordField.from_api_resource(
                TargetProperties.from_api_payload(
                    {
                        "type": "AB+",
                        "id": "grandmamas health record",
                        "content": "grandma is 79 years old",
                        "attributes": {"conditions": ["type 1 diabetes", "shingles"]},
                    }
                )
            ),
            current_page=CurrentPageRecordField.from_api_resource(
                CurrentPageProperties.from_api_payload(
                    {
                        "url": "https://sensitive_domain.com/your_credit_card_number?ccn=3742-0454-5540-0126",
                        "title": "my Credit Card Number",
                    }
                )
            ),
            device=None,
            geo=None,
            extra=MultiScalarTypeKeyValueRecordField.list_from_scalar_dict(
                {
                    "slam-poetry-id": "sddf89sdfd89dsafh9sd",
                }
            ),
            client_ip=None,
        )

        _write_flat_data_to_object(
            data={
                "target.attributes": None,
                "client_ip": None,
                "user": None,
                "device": None,
                "extra.0.value.bool_value": None,
                "target.content": "grandma is [AGE]",
                "account": None,
                "visitor_id": "23d35726-3f73-4045-a724-b788c0b12b97",
                "target.attributes.0.value.1": "shingles",
                "current_page.url.query_params.0.value": "3742-0454-5540-0126",
                "target.id": "grandmamas health record",
                "action": "vote for [PERSON_NAME]! [PERSON_NAME]",
                "extra.0.value.numeric_value": None,
                "current_page.url.protocol": "https",
                "timestamp": None,
                "target.attributes.0.key": "conditions",
                "extra.1.key": None,
                "current_page.url.hash": None,
                "extra.1.value.string_value": None,
                "current_page.url.domain": "sensitive_domain.com",
                "current_page.pageview_id": None,
                "geo": None,
                "extra.0.key": "slam-poetry-id",
                "current_page.url.query_params": None,
                "extra.0.value.string_value": "sddf89sdfd89dsafh9sd",
                "target.attributes.0.value.0": "type 1 diabetes",
                "extra.1.value.bool_value": None,
                "current_page.url.query_params.0.key": "ccn",
                "session": None,
                "target.type": "AB+",
                "current_page.url.raw": "https://sensitive_domain.com/your_credit_card_number?ccn=3742-0454-5540-0126",
                "extra.1.value.numeric_value": None,
                "traffic_source": None,
                "current_page.url.path": "/your_credit_card_number",
                "current_page.title": "my Credit Card Number",
            },
            obj=obj,
        )

        flat_modified_obj = _flatten_to_dict(obj)
        assert flat_modified_obj == {
            "action": "vote for [PERSON_NAME]! [PERSON_NAME]",
            "timestamp": None,
            "session": None,
            "traffic_source": None,
            "device": None,
            "geo": None,
            "client_ip": None,
            "account": None,
            "visitor_id": "23d35726-3f73-4045-a724-b788c0b12b97",
            "target.type": "AB+",
            "target.id": "grandmamas health record",
            "target.content": "grandma is [AGE]",
            "current_page.title": "my Credit Card Number",
            "current_page.pageview_id": None,
            "current_page.url.raw": "https://sensitive_domain.com/your_credit_card_number?ccn=3742-0454-5540-0126",
            "current_page.url.protocol": "https",
            "current_page.url.domain": "sensitive_domain.com",
            "current_page.url.path": "/your_credit_card_number",
            "current_page.url.hash": None,
            "extra.0.key": "slam-poetry-id",
            "target.attributes.0.key": "conditions",
            "extra.0.value.string_value": "sddf89sdfd89dsafh9sd",
            "extra.0.value.numeric_value": None,
            "extra.0.value.bool_value": None,
            "target.attributes.0.value.0": "type 1 diabetes",
            "target.attributes.0.value.1": "shingles",
            "current_page.url.query_params.0.key": "ccn",
            "current_page.url.query_params.0.value": "3742-0454-5540-0126",
        }

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
            BrowserEventAtom(
                action="Bryan Cameron Ricker is my name!",
                timestamp=None,
                session=None,
                account=None,
                visitor_id=None,
                traffic_source=None,
                target=TargetRecordField.from_api_resource(
                    TargetProperties.from_api_payload(
                        {
                            "type": "xx",
                            "id": "xx",
                            "content": "xx",
                            "attributes": {},
                        }
                    )
                ),
                current_page=CurrentPageRecordField.from_api_resource(
                    CurrentPageProperties.from_api_payload(
                        {
                            "url": "https://sensitive_domain.com/your_credit_card_number/4263982640269299",
                            "title": "Your Credit Card Number",
                        }
                    )
                ),
                device=None,
                geo=None,
                extra=MultiScalarTypeKeyValueRecordField.list_from_scalar_dict(
                    {
                        "password": "my password is password123",
                        "ethnicity": "caucasian",
                    }
                ),
                client_ip=None,
            ),
            BrowserEventAtom(
                action="vote for Jeb! Bush",
                timestamp=None,
                session=None,
                account=None,
                visitor_id="23d35726-3f73-4045-a724-b788c0b12b97",
                traffic_source=None,
                target=TargetRecordField.from_api_resource(
                    TargetProperties.from_api_payload(
                        {
                            "blood-type": "AB+",
                            "id": "grandmamas health record",
                            "content": "grandma is 79 years old",
                            "attributes": {"conditions": ["type 1 diabetes", "shingles"]},
                        }
                    )
                ),
                current_page=CurrentPageRecordField.from_api_resource(
                    CurrentPageProperties.from_api_payload(
                        {
                            "url": "https://sensitive_domain.com/your_credit_card_number?ccn=3742-0454-5540-0126",
                            "title": "my Credit Card Number",
                        }
                    )
                ),
                device=None,
                geo=None,
                extra=MultiScalarTypeKeyValueRecordField.list_from_scalar_dict(
                    {
                        "slam-poetry-id": "sddf89sdfd89dsafh9sd",
                    }
                ),
                client_ip=None,
            ),
        ]

        await redact_atoms(atoms)
        updated_flat = [_flatten_to_dict(a) for a in atoms]

        assert updated_flat == [
            {
                "account": None,
                "action": "Bryan Cameron Ricker is my name!",
                "client_ip": None,
                "current_page.pageview_id": None,
                "current_page.title": "Your Credit Card Number",
                "current_page.url.domain": "sensitive_domain.com",
                "current_page.url.hash": None,
                "current_page.url.path": "/your_credit_card_number/[CREDIT_CARD_NUMBER]",
                "current_page.url.protocol": "https",
                "current_page.url.query_params": None,
                "current_page.url.raw": "https://sensitive_domain.com/your_credit_card_number/[CREDIT_CARD_NUMBER]",
                "device": None,
                "extra.0.key": "password",
                "extra.0.value.bool_value": None,
                "extra.0.value.numeric_value": None,
                "extra.0.value.string_value": "my password is password123",
                "extra.1.key": "ethnicity",
                "extra.1.value.bool_value": None,
                "extra.1.value.numeric_value": None,
                "extra.1.value.string_value": "caucasian",
                "geo": None,
                "session": None,
                "target.attributes": None,
                "target.content": "xx",
                "target.id": "xx",
                "target.type": "xx",
                "timestamp": None,
                "traffic_source": None,
                "visitor_id": None,
            },
            {
                "account": None,
                "action": "vote for Jeb! Bush",
                "client_ip": None,
                "current_page.pageview_id": None,
                "current_page.title": "my Credit Card Number",
                "current_page.url.domain": "sensitive_domain.com",
                "current_page.url.hash": None,
                "current_page.url.path": "/your_credit_card_number",
                "current_page.url.protocol": "https",
                "current_page.url.query_params.0.key": "ccn",
                "current_page.url.query_params.0.value": "3742-0454-5540-0126",
                "current_page.url.raw": "https://sensitive_domain.com/your_credit_card_number?ccn=3742-0454-5540-0126",
                "device": None,
                "extra.0.key": "slam-poetry-id",
                "extra.0.value.bool_value": None,
                "extra.0.value.numeric_value": None,
                "extra.0.value.string_value": "sddf89sdfd89dsafh9sd",
                "geo": None,
                "session": None,
                "target.attributes.0.key": "conditions",
                "target.attributes.0.value.0": "type 1 diabetes",
                "target.attributes.0.value.1": "shingles",
                "target.content": "grandma is [AGE]",
                "target.id": "grandmamas health record",
                "target.type": None,
                "timestamp": None,
                "traffic_source": None,
                "visitor_id": "23d35726-3f73-4045-a724-b788c0b12b97",
            },
        ]

    def test_handle_key_sep_in_dict_key(self) -> None:
        @dataclasses.dataclass
        class Foo:
            obj: dict[str, str]

        f = Foo(obj={"fizz.buzz": "bar"})
        flat = _flatten_to_dict(f)

        assert flat == {'obj."fizz.buzz"': "bar"}, "Object not flattened as expected"

        # alter flat and write back
        flat['obj."fizz.buzz"'] = "bazz"
        _write_flat_data_to_object(
            data=flat,
            obj=f,
        )

        assert f.obj["fizz.buzz"] == "bazz", "altered flat data not written back correctly"
