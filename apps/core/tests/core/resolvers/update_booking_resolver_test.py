from eave.core.orm.booking import BookingOrm

from ..base import BaseTestCase


class TestUpdateBookingResolver(BaseTestCase):
    async def test_update_booking_with_unauthorized_account_for_booking(self) -> None:
        async with self.db_session.begin() as session:
            account1 = self.make_account(session)
            reserver_details = self.make_reserver_details(session, account1)
            survey = self.make_survey(session, account1)
            outing = self.make_outing(session, account1, survey)
            booking = self.make_booking(session, account1, outing)

            viewer_account = self.make_account(session)

        assert booking.reserver_details is None

        response = await self.make_graphql_request(
            "updateBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                    "reserverDetailsId": str(reserver_details.id),
                },
            },
            account_id=viewer_account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        data = result.data["viewer"]["updateBooking"]
        assert "booking" not in data
        assert data["__typename"] == "UpdateBookingFailure"
        assert data["failureReason"] == "BOOKING_NOT_FOUND"

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking.id)
            assert booking_fetched.reserver_details is None

    async def test_update_booking_with_unauthorized_account_for_reserver_details(self) -> None:
        async with self.db_session.begin() as session:
            account1 = self.make_account(session)
            reserver_details = self.make_reserver_details(session, account1)

            viewer_account = self.make_account(session)
            survey = self.make_survey(session, viewer_account)
            outing = self.make_outing(session, viewer_account, survey)
            booking = self.make_booking(session, viewer_account, outing)

        assert booking.reserver_details is None

        response = await self.make_graphql_request(
            "updateBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                    "reserverDetailsId": str(reserver_details.id),
                },
            },
            account_id=viewer_account.id,
        )

        result = self.parse_graphql_response(response)
        assert not result.data
        assert result.errors  # Currently this just throws an uncaught error.

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking.id)
            assert booking_fetched.reserver_details is None

    async def test_update_booking_reserver_details_success(self) -> None:
        async with self.db_session.begin() as session:
            viewer_account = self.make_account(session)
            reserver_details = self.make_reserver_details(session, viewer_account)
            survey = self.make_survey(session, viewer_account)
            outing = self.make_outing(session, viewer_account, survey)
            booking = self.make_booking(session, viewer_account, outing)

        assert booking.reserver_details is None

        response = await self.make_graphql_request(
            "updateBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                    "reserverDetailsId": str(reserver_details.id),
                },
            },
            account_id=viewer_account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert result.data["viewer"]["updateBooking"]["booking"]["reserverDetails"]["id"] == str(reserver_details.id)

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking.id)
            assert booking_fetched.reserver_details is not None
            assert booking_fetched.reserver_details.id == reserver_details.id

    async def test_update_booking_reserver_details_unset_param(self) -> None:
        async with self.db_session.begin() as session:
            viewer_account = self.make_account(session)
            survey = self.make_survey(session, viewer_account)
            outing = self.make_outing(session, viewer_account, survey)
            booking = self.make_booking(session, viewer_account, outing)

        assert booking.reserver_details is None

        response = await self.make_graphql_request(
            "updateBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                },
            },
            account_id=viewer_account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert result.data["viewer"]["updateBooking"]["booking"]["reserverDetails"] is None

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking.id)
            assert booking_fetched.reserver_details is None

    async def test_update_booking_reserver_details_null_param(self) -> None:
        async with self.db_session.begin() as session:
            viewer_account = self.make_account(session)
            survey = self.make_survey(session, viewer_account)
            outing = self.make_outing(session, viewer_account, survey)
            booking = self.make_booking(session, viewer_account, outing)

        assert booking.reserver_details is None

        response = await self.make_graphql_request(
            "updateBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                    "reserverDetailsId": None,
                },
            },
            account_id=viewer_account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert result.data["viewer"]["updateBooking"]["booking"]["reserverDetails"] is None

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking.id)
            assert booking_fetched.reserver_details is None

    async def test_update_booking_reserver_details_with_existing_reserver_details(self) -> None:
        async with self.db_session.begin() as session:
            viewer_account = self.make_account(session)
            survey = self.make_survey(session, viewer_account)
            outing = self.make_outing(session, viewer_account, survey)
            prev_reserver_details = self.make_reserver_details(session, viewer_account)
            booking = self.make_booking(session, viewer_account, outing, reserver_details=prev_reserver_details)

            new_reserver_details = self.make_reserver_details(session, viewer_account)

        assert booking.reserver_details is not None
        assert booking.reserver_details.id == prev_reserver_details.id

        response = await self.make_graphql_request(
            "updateBooking",
            {
                "input": {
                    "bookingId": str(booking.id),
                    "reserverDetailsId": str(new_reserver_details.id),
                },
            },
            account_id=viewer_account.id,
        )

        result = self.parse_graphql_response(response)
        assert result.data
        assert not result.errors

        assert result.data["viewer"]["updateBooking"]["booking"]["reserverDetails"]["id"] == str(
            new_reserver_details.id
        )

        async with self.db_session.begin() as session:
            booking_fetched = await BookingOrm.get_one(session, booking.id)
            assert booking_fetched.reserver_details is not None
            assert booking_fetched.reserver_details.id == new_reserver_details.id
