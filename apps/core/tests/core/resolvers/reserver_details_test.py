from http import HTTPStatus

from eave.core.graphql.types.reserver_details import SubmitReserverDetailsErrorCode

from ..base import BaseTestCase


class TestReserverDetailsEndpoints(BaseTestCase):
    async def test_valid_reserver_details_form_submit(self) -> None:
        async with self.db_session.begin() as session:
            account = await self.make_account(session=session)
        phone_num = "+12345678900"

        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": f"""
mutation {{
    submitReserverDetails(accountId: "{account.id}", firstName: "{self.anystr("first")}", lastName: "{self.anystr("last")}", phoneNumber: "{phone_num}") {{
        ... on SubmitReserverDetailsSuccess {{
            reserverDetails {{
                id
                firstName
                lastName
                phoneNumber
            }}
        }}
        ... on SubmitReserverDetailsError {{
            errorCode
        }}
    }}
}}
"""
            },
        )
        assert response.status_code == HTTPStatus.OK
        details = response.json().get("data").get("submitReserverDetails").get("reserverDetails")
        assert details.get("id") is not None
        assert details.get("firstName") == self.getstr("first")
        assert details.get("lastName") == self.getstr("last")
        assert details.get("phoneNumber") == phone_num

    async def test_reserver_details_form_submit_invalid_phone_number(self) -> None:
        async with self.db_session.begin() as session:
            account = await self.make_account(session=session)

        # invalid phone number
        phone_num = "1-800-BEANS-FOR-BREAKFAST"

        response = await self.httpclient.post(
            "/graphql",
            json={
                "query": f"""
mutation {{
    submitReserverDetails(accountId: "{account.id}", firstName: "{self.anystr("first")}", lastName: "{self.anystr("last")}", phoneNumber: "{phone_num}") {{
        ... on SubmitReserverDetailsSuccess {{
            reserverDetails {{
                id
                firstName
                lastName
                phoneNumber
            }}
        }}
        ... on SubmitReserverDetailsError {{
            errorCode
        }}
    }}
}}
"""
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json().get("data").get("submitReserverDetails").get("reserverDetails") is None
        assert (
            response.json().get("data").get("submitReserverDetails").get("errorCode")
            == SubmitReserverDetailsErrorCode.INVALID_PHONE_NUMBER
        )
