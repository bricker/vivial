import strawberry

from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.activity import ActivityCategory
from eave.core.orm.activity_category import ActivityCategoryOrm


async def list_activity_categories_query(*, info: strawberry.Info[GraphQLContext]) -> list[ActivityCategory]:
    all_activity_categories = ActivityCategoryOrm.all()
    return [ActivityCategory.from_orm(orm) for orm in all_activity_categories]
