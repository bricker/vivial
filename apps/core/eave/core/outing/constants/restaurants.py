from eave.stdlib.google.places.models.price_level import PriceLevel

from ..models.category import Category, RestaurantCategory

RESTAURANT_BUDGET_MAP = {
    0: PriceLevel.PRICE_LEVEL_FREE,
    1: PriceLevel.PRICE_LEVEL_INEXPENSIVE,
    2: PriceLevel.PRICE_LEVEL_MODERATE,
    3: PriceLevel.PRICE_LEVEL_EXPENSIVE,
    4: PriceLevel.PRICE_LEVEL_VERY_EXPENSIVE,
}

# You must pass a field mask to the Google Places API to specify the list of fields to return in the response.
# Reference: https://developers.google.com/maps/documentation/places/web-service/nearby-search
RESTAURANT_FIELD_MASK = [
    "places.id",
    "places.displayName",
    "places.accessibilityOptions",
    "places.addressComponents",
    "places.formattedAddress",
    "places.businessStatus",
    "places.googleMapsUri",
    "places.location",
    "places.photos",
    "places.primaryType",
    "places.primaryTypeDisplayName",
    "places.types",
    "places.nationalPhoneNumber",
    "places.priceLevel",
    "places.rating",
    "places.regularOpeningHours",
    "places.currentOpeningHours",
    "places.userRatingCount",
    "places.websiteUri",
    "places.reservable",
]

BREAKFAST_RESTAURANT_CATEGORIES = [
    Category(id="coffee_shop"),
    Category(id="breakfast_restaurant"),
    Category(id="bakery"),
    Category(id="cafe"),
]

BRUNCH_RESTAURANT_CATEGORIES = [
    Category(id="brunch_restaurant"),
    Category(id="breakfast_restaurant"),
    Category(id="cafe"),
]

RESTAURANT_CATEGORIES = [
    RestaurantCategory(
        id="ccb375f8e428489eac14192d12f0fd5a",
        name="American",
        is_default=True,
        google_category_ids=["american_restaurant", "hamburger_restaurant"],
    ),
    RestaurantCategory(
        id="19f88f27577a4d26b057a86222e1c080",
        name="Breakfast & Brunch",
        is_default=True,
        google_category_ids=["breakfast_restaurant", "brunch_restaurant"],
    ),
    RestaurantCategory(
        id="9ec628070ac64a58855caf7bfc2e87b1",
        name="Bakery",
        is_default=True,
        google_category_ids=["bakery"],
    ),
    RestaurantCategory(
        id="0069ad60d5da4fe3aa472bd644a7e6b5",
        name="Bar",
        is_default=True,
        google_category_ids=["bar"],
    ),
    RestaurantCategory(
        id="d05066d4db074ff8aa766ecaf658e5f7",
        name="Barbecue",
        is_default=True,
        google_category_ids=["barbecue_restaurant"],
    ),
    RestaurantCategory(
        id="dccdf86f88bb4bcf85cc7d949ef3c16a",
        name="Brazilian",
        is_default=True,
        google_category_ids=["brazilian_restaurant"],
    ),
    RestaurantCategory(
        id="a74c22060af8430d8f658b6188fd7e61",
        name="Cafe",
        is_default=True,
        google_category_ids=["cafe"],
    ),
    RestaurantCategory(
        id="dd9d9b7235fb420bb69731194e643ce5",
        name="Chinese",
        is_default=True,
        google_category_ids=["chinese_restaurant"],
    ),
    RestaurantCategory(
        id="5e3ebc3cfcff4bdf8c073c5e01efaa2d",
        name="Coffee Shop",
        is_default=True,
        google_category_ids=["coffee_shop"],
    ),
    RestaurantCategory(
        id="3c80c400a9fa42bdbc183a761d23b1a8",
        name="Fast Food",
        is_default=True,
        google_category_ids=["fast_food_restaurant"],
    ),
    RestaurantCategory(
        id="7c5d109676b24c16a7253b0465018665",
        name="French",
        is_default=True,
        google_category_ids=["french_restaurant"],
    ),
    RestaurantCategory(
        id="aa408106f2f34a71964e0aa02a53b390",
        name="Greek",
        is_default=True,
        google_category_ids=["greek_restaurant"],
    ),
    RestaurantCategory(
        id="ef5607c25e914e6d9fbe4ff88a7c7901",
        name="Indian",
        is_default=True,
        google_category_ids=["indian_restaurant"],
    ),
    RestaurantCategory(
        id="5af9b02255374d029e109c01ee895e2e",
        name="Indonesian",
        is_default=True,
        google_category_ids=["indonesian_restaurant"],
    ),
    RestaurantCategory(
        id="e37668410fa64ddb99672a9e6f7c525a",
        name="Italian",
        is_default=True,
        google_category_ids=["italian_restaurant", "pizza_restaurant"],
    ),
    RestaurantCategory(
        id="7cfdf3556dc749e99448c3b9d87be7e5",
        name="Japanese",
        is_default=True,
        google_category_ids=["japanese_restaurant", "ramen_restaurant", "sushi_restaurant"],
    ),
    RestaurantCategory(
        id="137c07c086f9458388e766834c6f9990",
        name="Korean",
        is_default=True,
        google_category_ids=["korean_restaurant"],
    ),
    RestaurantCategory(
        id="49938dc2a3f64bacae030a3f33272972",
        name="Lebanese",
        is_default=True,
        google_category_ids=["lebanese_restaurant"],
    ),
    RestaurantCategory(
        id="dffdcc00edc245cd9d444f6293e386cd",
        name="Mediterranean",
        is_default=True,
        google_category_ids=["mediterranean_restaurant"],
    ),
    RestaurantCategory(
        id="b31f88899d3a4d0590e68195ec25b9ad",
        name="Mexican",
        is_default=True,
        google_category_ids=["mexican_restaurant"],
    ),
    RestaurantCategory(
        id="b52041a0c39d4be49f108a89165e81a7",
        name="Middle Eastern",
        is_default=True,
        google_category_ids=["middle_eastern_restaurant"],
    ),
    RestaurantCategory(
        id="455f69f80b2149eb875ee4afa387a4d8",
        name="Sandwiches",
        is_default=True,
        google_category_ids=["sandwich_shop"],
    ),
    RestaurantCategory(
        id="4f4fe5090e71448e801b913c3a2dcab7",
        name="Seafood",
        is_default=True,
        google_category_ids=["seafood_restaurant"],
    ),
    RestaurantCategory(
        id="f89e9149753b42ffb418bc9147c8e316",
        name="Spanish",
        is_default=True,
        google_category_ids=["spanish_restaurant"],
    ),
    RestaurantCategory(
        id="f8a6be526f1846978e305e908979659e",
        name="Steak House",
        is_default=True,
        google_category_ids=["steak_house"],
    ),
    RestaurantCategory(
        id="56a17c1c90b44c708fa53060a2e37102",
        name="Thai",
        is_default=True,
        google_category_ids=["thai_restaurant"],
    ),
    RestaurantCategory(
        id="6be9d4f28022421ebb3b761b27bd9b0a",
        name="Turkish",
        is_default=True,
        google_category_ids=["turkish_restaurant"],
    ),
    RestaurantCategory(
        id="7310a499f62e44f9b1cd16dbc75008e0",
        name="Vegan",
        is_default=True,
        google_category_ids=["vegan_restaurant"],
    ),
    RestaurantCategory(
        id="2f63ccac0cf94c73be7f71d6e47ea76b",
        name="Vegetarian",
        is_default=True,
        google_category_ids=["vegetarian_restaurant"],
    ),
    RestaurantCategory(
        id="fb4f0fc6df3c44dd86403e4f7c1ad7b5",
        name="Vietnamese",
        is_default=True,
        google_category_ids=["vietnamese_restaurant"],
    ),
]
