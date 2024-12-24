# from sqlalchemy.dialects.postgresql import Range

# from eave.core.lib.address import Address
# from eave.core.orm.evergreen_activity import EvergreenActivityOrm
# from eave.core.orm.image import ImageOrm
# from eave.core.shared.geo import GeoPoint

# from ..base import BaseTestCase


# class TestEvergreenActivityOrm(BaseTestCase):
#     def make_evergreen_activity(self, session) -> EvergreenActivityOrm:
#         activity = EvergreenActivityOrm(
#             session,
#             title=self.anystr("title"),
#             description=self.anystr("description"),
#             coordinates=self.anycoordinates(),
#             is_bookable=self.anybool("is_bookable"),
#             booking_url=self.anyurl("booking_url"),
#             activity_category_id=self.anyuuid("category_id"),
#             duration_minutes=self.anyint("duration_minutes"),
#             availability=[],
#             address=self.anyaddress(),
#         )
#         return activity

#     async def test_new_activity_record(self) -> None:
#         async with self.db_session.begin() as session:
#             activity = EvergreenActivityOrm(
#                 session,
#                 title=self.anystr("title"),
#                 description=self.anystr("description"),
#                 coordinates=GeoPoint(
#                     lat=self.anylatitude("lat"),
#                     lon=self.anylongitude("lon"),
#                 ),
#                 is_bookable=self.anybool("is_bookable"),
#                 booking_url=self.anyurl("booking_url"),
#                 activity_category_id=self.anyuuid("category_id"),
#                 duration_minutes=self.anyint("duration_minutes"),
#                 availability=[],
#                 address=Address(
#                     address1=self.anystr("address.address1"),
#                     address2=self.anystr("address.address2"),
#                     city=self.anystr("address.city"),
#                     country=self.anystr("address.country"),
#                     state=self.anyusstate("address.state"),
#                     zip_code=self.anydigits("address.zip", length=5),
#                 ),
#             )

#         async with self.db_session.begin() as session:
#             obj = await EvergreenActivityOrm.get_one(session, activity.id)

#             assert obj.title == self.getstr("title")
#             assert obj.description == self.getstr("description")
#             assert obj.is_bookable == self.getbool("is_bookable")
#             assert obj.booking_url == self.geturl("booking_url")
#             assert obj.activity_category_id == self.getuuid("category_id")
#             assert obj.duration_minutes == self.getint("duration_minutes")
#             assert obj.availability == self.getstr("availability")
#             assert (
#                 obj.coordinates
#                 == GeoPoint(lat=self.getlatitude("lat"), lon=self.getlongitude("lon")).geoalchemy_shape()
#             )

#             assert obj.address.address1 == self.getstr("address.address1")
#             assert obj.address.address2 == self.getstr("address.address2")
#             assert obj.address.city == self.getstr("address.city")
#             assert obj.address.country == self.getstr("address.country")
#             assert obj.address.state == self.getusstate("address.state")
#             assert obj.address.zip_code == self.getdigits("address.zip")

#     async def test_activity_search_by_availability_with_no_availability(self) -> None:
#         async with self.db_session.begin() as session:
#             activity = self.make_evergreen_activity(session)
#             activity.availability = []

#         async with self.db_session.begin() as session:
#             results = (await session.scalars(EvergreenActivityOrm.select(business_hours_contains=1200))).all()

#         assert len(results) == 0

#     async def test_activity_search_by_availability_with_monday_availability(self) -> None:
#         async with self.db_session.begin() as session:
#             activity = self.make_evergreen_activity(session)
#             activity.availability = [Range(10 * 60, 17 * 60)]

#         async with self.db_session.begin() as session:
#             results = (await session.scalars(EvergreenActivityOrm.select(business_hours_contains=12 * 60))).all()

#         assert len(results) == 1

#     async def test_activity_images(self) -> None:
#         async with self.db_session.begin() as session:
#             activity_orm = self.make_evergreen_activity(session)

#             images = [
#                 ImageOrm(
#                     session,
#                     src=self.anyurl("image src 1"),
#                     alt=self.anystr("image alt 1"),
#                 ),
#                 ImageOrm(
#                     session,
#                     src=self.anyurl("image src 2"),
#                     alt=self.anystr("image alt 2"),
#                 ),
#             ]

#             activity_orm.images = images

#         async with self.db_session.begin() as session:
#             activity_orm_fetched = await EvergreenActivityOrm.get_one(session, activity_orm.id)
#             assert len(activity_orm_fetched.images) == 2

#             assert activity_orm_fetched.images[0].src == self.geturl("image src 1")
#             assert activity_orm_fetched.images[0].alt == self.geturl("image alt 1")
#             assert activity_orm_fetched.images[1].src == self.geturl("image src 2")
#             assert activity_orm_fetched.images[1].alt == self.geturl("image alt 2")
