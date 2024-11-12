import strawberry

from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.restaurant import RestaurantCategory
from eave.core.orm.restaurant_category import RestaurantCategoryOrm


async def list_restaurant_categories_query(*, info: strawberry.Info[GraphQLContext]) -> list[RestaurantCategory]:
    all_restaurant_categories = RestaurantCategoryOrm.all()
    return [RestaurantCategory.from_orm(orm) for orm in all_restaurant_categories]
