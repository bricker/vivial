import strawberry

from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.activity import ActivityCategoryGroup
from eave.core.orm.activity_category_group import ActivityCategoryGroupOrm


async def list_activity_category_groups_query(*, info: strawberry.Info[GraphQLContext]) -> list[ActivityCategoryGroup]:
    all_activity_category_groups = ActivityCategoryGroupOrm.all()
    return [ActivityCategoryGroup.from_orm(orm) for orm in all_activity_category_groups]
