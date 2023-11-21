import enum
from typing import Optional
import uuid

import strawberry.federation as sb
from strawberry.unset import UNSET
from eave.core.graphql.types.mutation_result import MutationResult
from eave.core.internal.orm.github_installation import GithubInstallationOrm
from eave.core.internal.orm.github_repos import GithubRepoOrm
import eave.core.internal.database as eave_db
from eave.stdlib.analytics import log_event

@sb.enum
class GithubRepoFeature(enum.StrEnum):
    API_DOCUMENTATION = "api_documentation"
    INLINE_CODE_DOCUMENTATION = "inline_code_documentation"
    ARCHITECTURE_DOCUMENTATION = "architecture_documentation"

@sb.enum
class GithubRepoFeatureState(enum.StrEnum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    PAUSED = "paused"

@sb.type
class GithubRepo:
    id: uuid.UUID = sb.field()
    team_id: uuid.UUID = sb.field()
    github_installation_id: uuid.UUID = sb.field()
    external_repo_id: str = sb.field()
    display_name: Optional[str] = sb.field()
    api_documentation_state: GithubRepoFeatureState = sb.field()
    inline_code_documentation_state: GithubRepoFeatureState = sb.field()
    architecture_documentation_state: GithubRepoFeatureState = sb.field()

    @classmethod
    def from_orm(cls, orm: GithubRepoOrm) -> "GithubRepo":
        return GithubRepo(
            id=orm.id,
            team_id=orm.team_id,
            github_installation_id=orm.github_installation_id,
            external_repo_id=orm.external_repo_id,
            display_name=orm.display_name,
            api_documentation_state=GithubRepoFeatureState(value=orm.api_documentation_state),
            inline_code_documentation_state=GithubRepoFeatureState(value=orm.inline_code_documentation_state),
            architecture_documentation_state=GithubRepoFeatureState(value=orm.architecture_documentation_state),
        )

@sb.type
class GithubRepoMutationResult(MutationResult):
    github_repo: GithubRepo

@sb.input
class GithubRepoCreateInput:
    external_repo_id: str = sb.field()
    display_name: str = sb.field()
    api_documentation_state: Optional[GithubRepoFeatureState] = sb.field()
    inline_code_documentation_state: Optional[GithubRepoFeatureState] = sb.field()
    architecture_documentation_state: Optional[GithubRepoFeatureState] = sb.field()


@sb.input
class GithubRepoRefInput:
    id: uuid.UUID = sb.field()

@sb.input
class GithubRepoListInput:
    external_repo_id: str = sb.field()

@sb.input
class GithubRepoUpdateValues:
    api_documentation_state: Optional[GithubRepoFeatureState] = sb.field()
    inline_code_documentation_state: Optional[GithubRepoFeatureState] = sb.field()
    architecture_documentation_state: Optional[GithubRepoFeatureState] = sb.field()

@sb.input
class GithubRepoUpdateInput:
    id: uuid.UUID = sb.field()
    new_values: GithubRepoUpdateValues = sb.field()

@sb.input
class GithubReposDeleteInput:
    id: uuid.UUID = sb.field()

@sb.input
class GithubReposFeatureStateInput:
    feature: GithubRepoFeature = sb.field()
    state: GithubRepoFeatureState = sb.field()

class GithubRepoResolvers:
    @staticmethod
    async def get_github_repos_for_team(team_id: uuid.UUID, external_repo_ids: Optional[list[str]] = UNSET) -> list[GithubRepo]:
        async with eave_db.async_session.begin() as db_session:
            gh_repo_orms = await GithubRepoOrm.query(
                session=db_session,
                params=GithubRepoOrm.QueryParams(
                    team_id=team_id,
                    external_repo_ids=external_repo_ids,
                ),
            )

        repo_list = list(gh_repo_orms)
        repo_list.sort(key=lambda r: r.display_name.lower() if r.display_name else str(r.created))
        return [GithubRepo.from_orm(repo) for repo in repo_list]

    @staticmethod
    async def get_github_repos_for_feature_state(query: GithubReposFeatureStateInput) -> list[GithubRepo]:
        async with eave_db.async_session.begin() as db_session:
            feature = query.feature
            state = query.state

            gh_repo_orms = await GithubRepoOrm.query(
                session=db_session,
                params=GithubRepoOrm.QueryParams(
                    team_id=None,
                    api_documentation_state=state if feature is GithubRepoFeature.API_DOCUMENTATION else None,
                    inline_code_documentation_state=state
                    if feature is GithubRepoFeature.INLINE_CODE_DOCUMENTATION
                    else None,
                    architecture_documentation_state=state
                    if feature is GithubRepoFeature.ARCHITECTURE_DOCUMENTATION
                    else None,
                ),
            )

        repo_list = list(gh_repo_orms)
        repo_list.sort(key=lambda r: r.display_name.lower() if r.display_name else str(r.created))
        return [GithubRepo.from_orm(repo) for repo in repo_list]

    @staticmethod
    async def get_github_repos_feature_states_match(team_id: uuid.UUID, input: GithubReposFeatureStateInput) -> bool:
        async with eave_db.async_session.begin() as db_session:
            state = await GithubRepoOrm.all_repos_match_feature_state(
                session=db_session,
                team_id=team_id,
                feature=input.feature,
                state=input.state,
            )

        return json_response(
            FeatureStateGithubReposRequest.ResponseBody(
                states_match=state,
            )
        )

    @staticmethod
    async def create_github_repo(team_id: uuid.UUID, github_repo: GithubRepoCreateInput) -> GithubRepoMutationResult:
        async with eave_db.async_session.begin() as db_session:
            github_installation_orm = await GithubInstallationOrm.one_or_exception(
                session=db_session,
                team_id=team_id,
            )

            gh_repo_orm = await GithubRepoOrm.create(
                session=db_session,
                team_id=team_id,
                external_repo_id=input.external_repo_id,
                github_installation_id=github_installation_orm.id,
                display_name=input.display_name,
                api_documentation_state=input.api_documentation_state,
                inline_code_documentation_state=input.inline_code_documentation_state,
                architecture_documentation_state=input.architecture_documentation_state,
            )

        await _trigger_api_documentation(github_repo_orm=gh_repo_orm, ctx=ctx)
        return GithubRepoMutationResult(
            eave_request_id=ctx.eave_request_id,
            github_repo=GithubRepo.from_orm(gh_repo_orm),
        )

    @staticmethod
    async def update_github_repo(team_id: uuid.UUID, input: GithubRepoUpdateInput) -> GithubRepoMutationResult:
        # transform to dict for ease of use
        update_values = {repo.id: repo.new_values for repo in input.repos}

        async with eave_db.async_session.begin() as db_session:
            gh_repo_orms = await GithubRepoOrm.query(
                session=db_session,
                params=GithubRepoOrm.QueryParams(
                    team_id=team_id,
                    ids=list(map(lambda r: r.id, input.repos)),
                ),
            )

            for gh_repo_orm in gh_repo_orms:
                assert gh_repo_orm.id in update_values, "Received a GithubRepo ORM that was not requested"
                new_values = update_values[gh_repo_orm.id]

                # fire analytics event for each changed feature
                _event_name = "eave_github_feature_state_change"
                _event_description = "An Eave GitHub App feature was activated/deactivated"
                _event_source = "eave core api"
                if (
                    new_values.api_documentation_state
                    and new_values.api_documentation_state.value != gh_repo_orm.api_documentation_state
                ):
                    await log_event(
                        event_name=_event_name,
                        event_description=_event_description,
                        event_source=_event_source,
                        opaque_params={
                            "feature": GithubRepoFeature.API_DOCUMENTATION.value,
                            "new_state": new_values.api_documentation_state.value,
                            "external_repo_id": gh_repo_orm.external_repo_id,
                        },
                        ctx=eave_state.ctx,
                    )
                if (
                    new_values.architecture_documentation_state
                    and new_values.architecture_documentation_state.value
                    != gh_repo_orm.architecture_documentation_state
                ):
                    await log_event(
                        event_name=_event_name,
                        event_description=_event_description,
                        event_source=_event_source,
                        opaque_params={
                            "feature": GithubRepoFeature.ARCHITECTURE_DOCUMENTATION.value,
                            "new_state": new_values.architecture_documentation_state.value,
                            "external_repo_id": gh_repo_orm.external_repo_id,
                        },
                        ctx=eave_state.ctx,
                    )
                if (
                    new_values.inline_code_documentation_state
                    and new_values.inline_code_documentation_state.value != gh_repo_orm.inline_code_documentation_state
                ):
                    await log_event(
                        event_name=_event_name,
                        event_description=_event_description,
                        event_source=_event_source,
                        opaque_params={
                            "feature": GithubRepoFeature.INLINE_CODE_DOCUMENTATION.value,
                            "new_state": new_values.inline_code_documentation_state.value,
                            "external_repo_id": gh_repo_orm.external_repo_id,
                        },
                        ctx=eave_state.ctx,
                    )

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
    @staticmethod
    async def delete_github_repo(team_id: uuid.UUID, ids: list[uuid.UUID]) -> MutationResult:
        ids = [repo.id for repo in input.repos]

        async with eave_db.async_session.begin() as db_session:
            await GithubRepoOrm.delete_by_ids(
                session=db_session,
                team_id=team_id,
                ids=ids,
            )



async def _trigger_api_documentation(github_repo_orm: GithubRepoOrm, ctx: LogContext) -> None:
    if github_repo_orm.api_documentation_state == GithubRepoFeatureState.ENABLED:
        assert ctx.eave_team_id, "eave_team_id unexpectedly missing"

        await create_task(
            target_path=RunApiDocumentationTask.config.path,
            queue_name=GITHUB_EVENT_QUEUE_NAME,
            audience=EaveApp.eave_github_app,
            origin=app_config.eave_origin,
            payload=RunApiDocumentationTask.RequestBody(
                repo=GithubRepoInput(external_repo_id=github_repo_orm.external_repo_id)
            ).json(),
            headers={
                EAVE_TEAM_ID_HEADER: ctx.eave_team_id,
                EAVE_REQUEST_ID_HEADER: ctx.eave_request_id,
            },
            ctx=ctx,
        )


def _sort_repos(repos: list[GithubRepoOrm]) -> None:
    repos.sort(key=lambda r: r.display_name.lower() if r.display_name else str(r.created))
