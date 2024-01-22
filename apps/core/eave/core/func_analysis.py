# ruff: noqa: E402

"""
1. probelms
How can we know what code is worth tracking?
* arb code
* what does it mean to be "worth tracking"?
* functions vs lines; granularity diff
* what data to get/how to get data about event to create if it is worth track

2. problem effecs/constraints
* should be all/mostly automated
* can we make any assumptions about code? ie. only looking at complete fucntiosn?
* we need to get context from somewhere
* dont want to dup events from other sources

2.5. break down probelms
find product relevant points of interest in code [using AI somehow]
deterimine if POI is worth tracking
and determine if POI is already covered by http/db?
gather data to define POI in human readable terms
create unique ID from POI (but flex enough to not become invalidated if code changes a bit, or is moved)

3. ideas
static code analysis to gather ctx about code


"""

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files
from eave.stdlib.config import SHARED_CONFIG

load_standard_dotenv_files()


import asyncio
import os
from textwrap import dedent
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionUserMessageParam
from eave.stdlib.transformer_ai.models import OpenAIModel
from eave.stdlib.transformer_ai.openai_client import chat_completion, formatprompt

openai_client = AsyncOpenAI(
    api_key=SHARED_CONFIG.eave_openai_api_key,
    organization=SHARED_CONFIG.eave_openai_api_org,
)

funcs = [
    dedent(f).strip()
    for f in [
        r"""
        async def get(self, request: Request) -> Response:
            # random value for verifying request wasnt tampered with via CSRF
            token: str = oauthlib.common.generate_token()

            # For GitHub, there is a problem: The combined Installation + Authorization flow doesn't allow us
            # to specify a redirect_uri; it chooses the first one configured. So it always redirects to eave.fyi,
            # which makes it practically impossible to test in development (without some proxy configuration).
            # So instead, we're going to set a special cookie and read it on the other side (callback), and redirect if necessary.
            # https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app#generating-a-user-access-token-when-a-user-installs-your-app
            state_json = json.dumps({"token": token, "redirect_uri": GITHUB_OAUTH_CALLBACK_URI})
            state = eave.stdlib.util.b64encode(state_json, urlsafe=True)

            authorization_url = f"{SHARED_CONFIG.eave_github_app_public_url}/installations/new?state={state}"
            # authorization_url = f"https://github.com/login/oauth/authorize?{qp}"
            response = RedirectResponse(url=authorization_url)

            utm_cookies.set_tracking_cookies(
                response=response,
                request=request,
            )

            oauth_cookies.save_state_cookie(
                response=response,
                state=state,
                provider=_AUTH_PROVIDER,
            )

            return response
        """,

        r"""
        async def get(
            self,
            request: Request,
        ) -> Response:
            self.response = Response()
            self.eave_state = EaveRequestState.load(request=request)

            if "state" not in request.query_params and "code" not in request.query_params:
                # unable to check validity of data received. or could just be a
                # permissions update from gh website redirecting to our callback
                shared.set_redirect(
                    response=self.response,
                    location=shared.DEFAULT_REDIRECT_LOCATION,
                )
                return self.response

            if "state" in request.query_params:
                # we set this state in our /oauth/github/authorize endpoint before handing
                # auth over to github
                self.state = state = request.query_params["state"]

                # Because of the GitHub redirect_uri issue described in this file, we need to get the redirect_uri from state,
                # and redirect if it's on a different host.
                # Reminder that in this scenario, the cookies from your local environment won't be available here (because we're probably at eave.fyi)
                state_decoded = json.loads(eave.stdlib.util.b64decode(state, urlsafe=True))
                if redirect_uri := state_decoded.get("redirect_uri"):
                    url = urllib.parse.urlparse(redirect_uri)
                    if url.hostname != request.url.hostname:
                        qp = urllib.parse.urlencode(request.query_params)
                        location = f"{redirect_uri}?{qp}"
                        return shared.set_redirect(response=self.response, location=location)

                shared.verify_oauth_state_or_exception(
                    state=self.state, auth_provider=_AUTH_PROVIDER, request=request, response=self.response
                )

            if "code" in request.query_params:
                # github marketplace installs skip the step where we set state, so manually
                # validate the user (oauth code) has access to the app installation
                installation_id = request.query_params.get("installation_id")
                code = request.query_params.get("code")
                if not installation_id or not code:
                    eaveLogger.warning(
                        "Missing GitHub user oauth code and/or app installation_id. Cannot proceed.",
                        self.eave_state.ctx,
                    )
                    return shared.cancel_flow(response=self.response)

                await shared.verify_stateless_installation_or_exception(code, installation_id, self.eave_state.ctx)

            setup_action = request.query_params.get("setup_action")
            if setup_action not in ["install", "update"]:
                eaveLogger.warning(f"Unexpected github setup_action: {setup_action}", self.eave_state.ctx)

            installation_id = request.query_params.get("installation_id")
            if not installation_id:
                eaveLogger.warning(
                    f"github installation_id not provided for action {setup_action}. Cannot proceed.",
                    self.eave_state.ctx,
                )
                return shared.cancel_flow(response=self.response)

            self.installation_id = installation_id
            auth_cookies = get_auth_cookies(cookies=request.cookies)

            try:
                await self._maybe_set_account_data(auth_cookies)
                await self._update_or_create_github_installation()
                # dont link github repos to our db until we know what team to associate them w/
                if self._request_logged_in():
                    assert self.eave_team  # make types happy
                    await shared.sync_github_repos(team_id=self.eave_team.id, ctx=self.eave_state.ctx)
            except Exception as e:
                if shared.is_error_response(self.response):
                    return self.response
                raise e

            return self.response
        """,

        r"""
        async def _maybe_set_account_data(self, auth_cookies: AuthCookies) -> None:
            if not auth_cookies.all_set:
                # This is the case where they're going through the install flow but not logged in.
                # (e.g. installing from github marketplace w/o an Eave account)
                shared.set_redirect(
                    response=self.response,
                    location=shared.SIGNUP_REDIRECT_LOCATION,
                )
            else:
                async with database.async_session.begin() as db_session:
                    eave_account = await AccountOrm.one_or_none(
                        session=db_session,
                        params=AccountOrm.QueryParams(
                            id=eave.stdlib.util.ensure_uuid(auth_cookies.account_id), access_token=auth_cookies.access_token
                        ),
                    )

                    if not eave_account:
                        shared.cancel_flow(response=self.response)
                        raise Exception("auth_cookies did not point to valid account")

                    self.eave_account = eave_account
                    self.eave_team = await self.eave_account.get_team(session=db_session)

                shared.set_redirect(
                    response=self.response,
                    location=shared.DEFAULT_REDIRECT_LOCATION,
                )
        """,

        r"""
        async def _update_or_create_github_installation(
            self,
        ) -> None:
            async with database.async_session.begin() as db_session:
                # try fetch existing github installation
                github_installation_orm = await GithubInstallationOrm.query(
                    session=db_session,
                    params=GithubInstallationOrm.QueryParams(
                        team_id=self.eave_team.id if self.eave_team else None,
                        github_install_id=self.installation_id,
                    ),
                )

                if not github_installation_orm:
                    # create state cookie we can use later to associate new accounts
                    # with a dangling app installation row
                    state = None

                    # only set state cookie for installations that wont have a team_id set
                    if not self._request_logged_in():
                        state = shared.generate_and_set_state_cookie(
                            response=self.response, installation_id=self.installation_id
                        )

                    # create new github installation associated with the TeamOrm
                    # (or create a dangling installation to later associate w/ a future account)
                    github_installation_orm = await GithubInstallationOrm.create(
                        session=db_session,
                        team_id=self.eave_account.team_id if self.eave_account else None,
                        github_install_id=self.installation_id,
                        install_flow_state=state,
                    )

                elif self.eave_account and github_installation_orm.team_id != self.eave_account.team_id:
                    eaveLogger.warning(
                        f"A Github integration already exists with github install id {self.installation_id}",
                        self.eave_state.ctx,
                    )
                    shared.set_error_code(response=self.response, error_code=EaveOnboardingErrorCode.already_linked)
                    raise Exception("Attempted to link Github integration when one already existed")

                self.github_installation_orm = github_installation_orm
        """,

        r"""
        def _request_logged_in(self) -> bool:
            return self.eave_team is not None and self.eave_account is not None
        """
    ]
]

async def main():
    for f in funcs:
        # TODO: asking for just exact copy of the line alone is overly simplistic... there can be identical copies of a line throughout a function
        poi_prompt = formatprompt(
            r"""
            Locate all points of interest (if any) in a function that we might want to fire a product analytics event from.
            For each point of interest you find, give a name and description for the event, and the full line of the point of interest.
            Provide your response as a JSON array of JSON objects with "name", "description", and "line" fields.

            For example:
            ###
            ```
            async def post(self, request: Request) -> Response:
                eave_state = EaveRequestState.load(request=request)
                body = await request.json()
                input = UpdateGithubReposRequest.RequestBody.parse_obj(body)
                assert eave_state.ctx.eave_team_id, "eave_team_id unexpectedly missing"

                # transform to dict for ease of use
                update_values = {repo.id: repo.new_values for repo in input.repos}

                async with database.async_session.begin() as db_session:
                    gh_repo_orms = await GithubRepoOrm.query(
                        session=db_session,
                        params=GithubRepoOrm.QueryParams(
                            team_id=ensure_uuid(eave_state.ctx.eave_team_id),
                            ids=list(map(lambda r: r.id, input.repos)),
                        ),
                    )

                    for gh_repo_orm in gh_repo_orms:
                        assert gh_repo_orm.id in update_values, "Received a GithubRepo ORM that was not requested"
                        new_values = update_values[gh_repo_orm.id]

                        if (
                            gh_repo_orm.api_documentation_state == GithubRepoFeatureState.DISABLED
                            and new_values.api_documentation_state == GithubRepoFeatureState.ENABLED
                        ):
                            await _trigger_api_documentation(github_repo_orm=gh_repo_orm, ctx=eave_state.ctx)

                        gh_repo_orm.update(session=db_session, input=new_values)

                return json_response(
                    UpdateGithubReposRequest.ResponseBody(
                        repos=[orm.api_model for orm in gh_repo_orms],
                    )
                )
            ```
            [
                {
                    "name": "github_feature_state_change",
                    "description": "A GitHub App feature was activated/deactivated",
                    "line": "new_values = update_values[gh_repo_orm.id]"
                }
            ]
            ###
            ###
            ```
            def set_http_cookie(
                response: HTTPFrameworkResponse,
                key: str,
                value: str,
                httponly: bool = True,
            ) -> None:
                response.set_cookie(
                    key=key,
                    value=value,
                    domain=SHARED_CONFIG.eave_cookie_domain,
                    path="/",
                    httponly=httponly,
                    secure=(not SHARED_CONFIG.is_development),
                    samesite="lax",
                    max_age=int(ONE_YEAR_IN_MS / 1000),
                )
            ```
            []
            ###
            ###
            ```
            async def post(self, request: Request) -> Response:
                eave_state = EaveRequestState.load(request=request)
                body = await request.json()
                input = UpsertDocumentOp.RequestBody.parse_obj(body)

                async with eave_db.async_session.begin() as db_session:
                    eave_team = await TeamOrm.one_or_exception(
                        session=db_session,
                        team_id=eave.stdlib.util.unwrap(eave_state.ctx.eave_team_id),
                    )
                    # get all subscriptions we wish to associate the new document with
                    subscriptions = [
                        await SubscriptionOrm.one_or_exception(
                            team_id=eave_team.id,
                            source=subscription.source,
                            session=db_session,
                        )
                        for subscription in input.subscriptions
                    ]

                    # make sure we got even 1 subscription
                    if len(subscriptions) < 1:
                        raise UnexpectedMissingValue("Expected to have at least 1 subscription input")

                    destination = await eave_team.get_document_client(session=db_session)
                    if destination is None:
                        raise UnexpectedMissingValue("document destination")

                    # FIXME: boldly assuming all subscriptions have the same value for document_reference_id
                    existing_document_reference = await subscriptions[0].get_document_reference(session=db_session)

                    if existing_document_reference is None:
                        document_metadata = await destination.create_document(input=input.document, ctx=eave_state.ctx)

                        document_reference = await DocumentReferenceOrm.create(
                            session=db_session,
                            team_id=eave_team.id,
                            document_id=document_metadata.id,
                            document_url=document_metadata.url,
                        )
                    else:
                        await destination.update_document(
                            input=input.document,
                            document_id=existing_document_reference.document_id,
                            ctx=eave_state.ctx,
                        )

                        document_reference = existing_document_reference

                    # update all subscriptions without a document reference
                    for subscription in subscriptions:
                        if subscription.document_reference_id is None:
                            subscription.document_reference_id = document_reference.id

                model = UpsertDocumentOp.ResponseBody(
                    team=eave_team.api_model,
                    subscriptions=[subscription.api_model for subscription in subscriptions],
                    document_reference=document_reference.api_model,
                )

                return eave.stdlib.api_util.json_response(status_code=http.HTTPStatus.ACCEPTED, model=model)
            ```
            [
                {
                    "name": "created_documentation",
                    "description": "created some documentation",
                    "line": "document_reference = await DocumentReferenceOrm.create(",
                },
                {
                    "name": "updated_documentation",
                    "description": "updated some existing documentation",
                    "line": "await destination.update_document(",
                }
            ]
            ###
            """,
            f"""
            ###
            ```
            {f}
            ```

            """
        )

        # TODO for each POI
        response = await openai_client.chat.completions.create(
            stream=True,
            model="gpt-4-1106-preview",
            messages=[
                ChatCompletionUserMessageParam({
                    "role": "user",
                    "content": poi_prompt,
                }),
            ],
            temperature=0.2,
        )
        response = "".join(filter(None, [chunk.choices[0].delta.content async for chunk in response]))
        json_resp_len = len(response)
        json_resp_init = 0
        while response[json_resp_len-1] != "]":
            json_resp_len -= 1
        while json_resp_init < json_resp_len and response[json_resp_init] != "[":
            json_resp_init += 1
        
        # json parse
        import json
        response = response[json_resp_init:json_resp_len]
        print(response)
        json_resp = json.loads(response)
        for poi in json_resp:
            print(f"candidate poi: {poi}")
            if poi["line"] not in f:
                print("poi was not in func body")
                continue

            dup_prompt = formatprompt(
                f"""
                Does this point of interest represent a database transaction or a network request? Respond with Yes or No.

                Name: {poi["name"]}
                Description: {poi["description"]}

                Answer: 
                """,
            )

            response = await openai_client.chat.completions.create(
                stream=True,
                model="gpt-4-1106-preview",
                messages=[
                    ChatCompletionUserMessageParam({
                        "role": "user",
                        "content": dup_prompt,
                    }),
                ],
            )

            response = "".join(filter(None, [chunk.choices[0].delta.content async for chunk in response]))

            if response.lower() == "yes":
                print("poi was dup of http/db event")
                continue
            elif response.lower() == "no":
                pass
            else:
                # mostly seems to happen for "No." and "No. {some explanation}"
                print("gpt responded badly:", response)

            print(f"""poi is valid event!""")
            with open("event.txt", "a") as fil:
                fil.write(json.dumps(poi))


if __name__ == "__main__":
    print("")
    print("")
    asyncio.run(main())