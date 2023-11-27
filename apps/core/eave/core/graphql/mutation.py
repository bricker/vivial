from typing import Any, Awaitable, Coroutine
from uuid import UUID, uuid4
import strawberry.federation as sb
from eave.core.graphql.types.connect import ConnectInstallationMutationResult, ConnectInstallationResolvers
from eave.core.graphql.types.document import DocumentInput, DocumentReferenceMutationResult, DocumentResolvers, UpsertDocumentMutationResult
from eave.core.graphql.types.github_document import GithubDocument, GithubDocumentCreateInput, GithubDocumentMutationResult, GithubDocumentResolvers
from eave.core.graphql.types.github_installation import GithubInstallationResolvers, delete_github_installation_resolver
from eave.core.graphql.types.github_repo import GithubRepo, GithubRepoCreateInput, GithubRepoMutationResult, GithubRepoResolvers
from eave.core.graphql.types.mutation_result import MutationResult
from eave.core.graphql.types.subscription import DocumentReference, SubscriptionInput, SubscriptionMutationResult, SubscriptionResolvers
import eave.core.internal.database as eave_db
from eave.core.internal.orm.github_documents import GithubDocumentsOrm
from eave.core.internal.orm.github_installation import GithubInstallationOrm
from eave.core.internal.orm.github_repos import GithubRepoOrm
from eave.core.internal.orm.subscription import SubscriptionOrm
from eave.core.internal.orm.team import TeamOrm
from eave.core.graphql.types.team import ConfluenceDestinationMutationResult, Team, TeamResolvers
from eave.stdlib.core_api.models.github_repos import GithubRepoFeatureState
from eave.stdlib.core_api.models.subscriptions import SubscriptionSource, SubscriptionSourceEvent, SubscriptionSourcePlatform

@sb.type
class Mutation:
    upsert_document: DocumentReferenceMutationResult = sb.mutation(resolver=DocumentResolvers.upsert_document)
    delete_document: MutationResult = sb.mutation(resolver=DocumentResolvers.delete_document)

    create_subscription: SubscriptionMutationResult = sb.mutation(resolver=SubscriptionResolvers.create_subscription)
    delete_subscription: MutationResult = sb.mutation(resolver=SubscriptionResolvers.delete_subscription)

    upsert_confluence_destination: ConfluenceDestinationMutationResult = sb.mutation(resolver=TeamResolvers.upsert_confluence_destination)
    register_connect_installation: ConnectInstallationMutationResult = sb.mutation(resolver=ConnectInstallationResolvers.register_connect_installation)

    delete_github_installation: MutationResult = sb.mutation(resolver=GithubInstallationResolvers.delete_github_installation)

    create_github_repo: GithubRepoMutationResult = sb.mutation(resolver=GithubRepoResolvers.create_github_repo)
    update_github_repo: GithubRepoMutationResult = sb.mutation(resolver=GithubRepoResolvers.update_github_repo)
    delete_github_repo: MutationResult = sb.mutation(resolver=GithubRepoResolvers.delete_github_repo)

    create_github_document: GithubDocumentMutationResult = sb.mutation(resolver=GithubDocumentResolvers.create_github_document)
    update_github_document: GithubDocumentMutationResult = sb.mutation(resolver=GithubDocumentResolvers.update_github_document)
    delete_github_document: MutationResult = sb.mutation(resolver=GithubDocumentResolvers.delete_github_document)
