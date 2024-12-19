from eave.core.orm.base import InvalidRecordError
from eave.core.orm.survey import SurveyOrm

from ..base import BaseTestCase


class TestSurveyOrm(BaseTestCase):
    async def test_survey_orm(self) -> None:
        async with self.db_session.begin() as session:
            account = self.make_account(session)
            survey = self.make_survey(session, account)

        async with self.db_session.begin() as session:
            survey_fetched = await SurveyOrm.get_one(session, survey.id)

            assert survey_fetched.id == survey.id
            assert survey_fetched.account is not None
            assert survey_fetched.account.id == account.id
            assert survey_fetched.account_id == account.id

    async def test_survey_orm_validations(self) -> None:
        with self.assertRaises(InvalidRecordError):
            async with self.db_session.begin() as session:
                account = self.make_account(session)
                survey = self.make_survey(session, account)
                survey.headcount = 0

        with self.assertRaises(InvalidRecordError):
            async with self.db_session.begin() as session:
                account = self.make_account(session)
                survey = self.make_survey(session, account)
                survey.search_area_ids = []
