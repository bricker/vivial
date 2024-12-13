
from eave.core.orm.account import AccountOrm
from eave.core.orm.survey import SurveyOrm

from ..base import BaseTestCase


class TestSurveyOrm(BaseTestCase):
    async def test_survey_orm(self) -> None:
        async with self.db_session.begin() as session:
            account = AccountOrm(
                email=self.anyemail(),
                plaintext_password=self.anystr(),
            )
            session.add(account)

            survey = self.make_survey(session, account)
            session.add(survey)

        async with self.db_session.begin() as session:
            survey_fetched = await SurveyOrm.get_one(session, survey.id)

            assert survey_fetched.id == survey.id
            assert survey_fetched.account is not None
            assert survey_fetched.account.id == account.id
            assert survey_fetched.account_id == account.id
