from eave.stdlib.deidentification import _flatten_to_dict

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
