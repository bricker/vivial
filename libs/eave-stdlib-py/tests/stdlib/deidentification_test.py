import dataclasses
from eave.stdlib.deidentification import _flatten_to_dict, _write_flat_data_to_object, Redactable, redactable

from eave.core.internal.atoms.api_types import CurrentPageProperties, TargetProperties
from eave.core.internal.atoms.browser_events import BrowserEventAtom
from eave.core.internal.atoms.record_fields import (
    CurrentPageRecordField,
    MultiScalarTypeKeyValueRecordField,
    TargetRecordField,
    UserRecordField,
)

from .base import StdlibBaseTestCase


class DeidentificationTest(StdlibBaseTestCase):
    def test_object_flattening(self) -> None:
        obj = BrowserEventAtom(
            action="Bryan Cameron Ricker is my name!",
            timestamp=None,
            session=None,
            user=UserRecordField(
                account_id=None,
                visitor_id="23d35726-3f73-4041-a724-b788c0b12b97",
            ),
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
            "user.account_id": None,
            "user.visitor_id": "23d35726-3f73-4041-a724-b788c0b12b97",
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
            "extra.0.value.float_value": None,
            "extra.0.value.int_value": None,
            "extra.1.value.bool_value": None,
            "extra.1.value.float_value": None,
            "extra.1.value.int_value": None,
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
            user=UserRecordField(
                account_id=None,
                visitor_id="23d35726-3f73-4045-a724-b788c0b12b97",
            ),
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
                "user.account_id": None,
                "user.visitor_id": "23d35726-3f73-4045-a724-b788c0b12b97",
                "target.attributes.0.value.1": "shingles",
                "current_page.url.query_params.0.value": "3742-0454-5540-0126",
                "target.id": "grandmamas health record",
                "action": "vote for [PERSON_NAME]! [PERSON_NAME]",
                "extra.0.value.int_value": None,
                "current_page.url.protocol": "https",
                "timestamp": None,
                "target.attributes.0.key": "conditions",
                "extra.1.key": None,
                "current_page.url.hash": None,
                "extra.1.value.string_value": None,
                "current_page.url.domain": "sensitive_domain.com",
                "current_page.pageview_id": None,
                "extra.0.value.float_value": None,
                "extra.1.value.float_value": None,
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
                "extra.1.value.int_value": None,
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
            "user.account_id": None,
            "user.visitor_id": "23d35726-3f73-4045-a724-b788c0b12b97",
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
            "extra.0.value.int_value": None,
            "extra.0.value.float_value": None,
            "extra.0.value.bool_value": None,
            "target.attributes.0.value.0": "type 1 diabetes",
            "target.attributes.0.value.1": "shingles",
            "current_page.url.query_params.0.key": "ccn",
            "current_page.url.query_params.0.value": "3742-0454-5540-0126",
        }

    def test_redactable_field_identification(self) -> None:
        @dataclasses.dataclass
        class Spec(Redactable):
            info: str | None = redactable()

        @dataclasses.dataclass
        class Basket(Redactable):
            thread_count: int
            woven_underwater: bool = redactable()
            price: str | None = redactable()
            specs: dict[str, Spec] = redactable()

        @dataclasses.dataclass
        class WeavingSpider(Redactable):
            genus: str
            favorite_legs: list[int] = redactable()
            name: str = redactable()

        @dataclasses.dataclass
        class Tool:
            type: str

        @dataclasses.dataclass
        class BasketWeaver(Redactable):
            tools: list[Tool]
            name: str = redactable()
            helpers: list[WeavingSpider] | None = redactable()
            latest_work: Basket = redactable()

        assert sorted(Basket.redactable_fields_matchers()) == sorted(
            [
                r"woven_underwater",
                r"price",
                r'specs\.".*?(?="\.)"\.info',
            ]
        ), "Single object matchers did not match expected"
        assert sorted(BasketWeaver.redactable_fields_matchers()) == sorted(
            [
                r"name",
                r"latest_work\.woven_underwater",
                r"latest_work\.price",
                r"helpers\.[0-9]+\.favorite_legs\.[0-9]+",
                r"helpers\.[0-9]+\.name",
            ]
        ), "Nested object and list matchers did not match expected"
