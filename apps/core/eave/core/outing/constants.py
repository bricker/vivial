from eave.stdlib.google.places.models.price_level import PriceLevel

ACTIVITY_BUDGET_MAP = {
    0: 0,
    1: 10,
    2: 50,
    3: 150,
    4: None,
}

RESTAURANT_BUDGET_MAP = {
    0: PriceLevel.PRICE_LEVEL_FREE,
    1: PriceLevel.PRICE_LEVEL_INEXPENSIVE,
    2: PriceLevel.PRICE_LEVEL_MODERATE,
    3: PriceLevel.PRICE_LEVEL_EXPENSIVE,
    4: PriceLevel.PRICE_LEVEL_VERY_EXPENSIVE,
}

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
