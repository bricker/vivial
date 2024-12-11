import random

from eave.core.orm.account import AccountOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import OutingBudget

from ..base import BaseTestCase


class TestSurveyOrm(BaseTestCase):
    async def test_survey_orm(self) -> None:
        async with self.db_session.begin() as session:
            account = AccountOrm(
                email=self.anyemail(),
                plaintext_password=self.anystr(),
            )
            session.add(account)

            survey = SurveyOrm(
                account=account,
                budget=OutingBudget.INEXPENSIVE,
                headcount=self.anyint(min=1, max=2),
                search_area_ids=[s.id for s in random.choices(SearchRegionOrm.all(), k=3)],
                start_time_utc=self.anydatetime(future=True),
                timezone=self.anytimezone(),
                visitor_id=self.anyuuid("visitor id"),
            )
            session.add(survey)

        async with self.db_session.begin() as session:
            survey_fetched = await SurveyOrm.get_one(session, survey.id)

            assert survey_fetched.id == survey.id
            assert survey_fetched.account is not None
            assert survey_fetched.account.id == account.id
            assert survey_fetched.account_id == account.id
