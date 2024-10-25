ACTIVITY_BUDGET_MAP = {
    1: 10,
    2: 50,
    3: 150,
    4: None,
}

# TODO: don't need this

# TODO map to google PriceLevel
RESTAURANT_BUDGET_MAP = {
    1: {
        min: 0,
        max: 10,
    },
    2: {
        min: 11,
        max: 30,
    },
    3: {
        min: 31,
        max: 60,
    },
    4: {
        min: 61,
        max: None,
    },
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
