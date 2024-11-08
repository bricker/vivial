from uuid import UUID, uuid4

import strawberry

from ..types.category import Category

MOCK_RESTAURANT_CATEGORIES = [
    Category(id=uuid4(), label="American", is_default=True),
    Category(id=uuid4(), label="Breakfast & Brunch", is_default=True),
    Category(id=uuid4(), label="Bakery", is_default=True),
    Category(id=uuid4(), label="Barbecue", is_default=True),
    Category(id=uuid4(), label="Brazilian", is_default=True),
    Category(id=uuid4(), label="Cafe", is_default=True),
    Category(id=uuid4(), label="Chinese", is_default=True),
    Category(id=uuid4(), label="Coffee Shop", is_default=True),
    Category(id=uuid4(), label="Fast Food", is_default=True),
    Category(id=uuid4(), label="French", is_default=True),
    Category(id=uuid4(), label="Greek", is_default=True),
    Category(id=uuid4(), label="Indian", is_default=True),
    Category(id=uuid4(), label="Indonesian", is_default=True),
    Category(id=uuid4(), label="Italian", is_default=True),
    Category(id=uuid4(), label="Japanese", is_default=True),
    Category(id=uuid4(), label="Korean", is_default=True),
    Category(id=uuid4(), label="Lebanese", is_default=True),
    Category(id=uuid4(), label="Mediterranean", is_default=True),
    Category(id=uuid4(), label="Mexican", is_default=True),
    Category(id=uuid4(), label="Middle Eastern", is_default=True),
    Category(id=uuid4(), label="Sandwiches", is_default=True),
    Category(id=uuid4(), label="Seafood", is_default=True),
    Category(id=uuid4(), label="Spanish", is_default=True),
    Category(id=uuid4(), label="Steak House", is_default=True),
    Category(id=uuid4(), label="Thai", is_default=True),
    Category(id=uuid4(), label="Turkish", is_default=True),
    Category(id=uuid4(), label="Vegan", is_default=True),
    Category(id=uuid4(), label="Vegetarian", is_default=True),
    Category(id=uuid4(), label="Vietnamese", is_default=True),
]


MOCK_SEASONAL_HOLIDAY_ID = UUID("7984e346-aa79-4315-bc10-6e2628461011")
MOCK_FOOD_DRINK_ID = UUID("d96659f4-a8a3-488e-9e52-29bcd988f992")
MOCK_FILM_MEDIA_ENTERTAINMENT_ID = UUID("f309c05b-4734-4911-aa47-fb01253926a3")
MOCK_MUSIC_ID = UUID("87ef7954-2797-4e58-8d28-fca38aa838fd")
MOCK_ARTS_THEATRE_ID = UUID("b4350487-d042-45a4-a2ee-fb3f7327543a")
MOCK_HOBBIES_ID = UUID("e913df7d-8935-4e18-a31d-cbfffdaf8d45")
MOCK_FITNESS_OUTDOORS_ID = UUID("8847a7f4-8289-4803-aae0-0b9c17813b6b")

MOCK_ACTIVITY_CATEGORIES = [
    Category(
        id=MOCK_SEASONAL_HOLIDAY_ID,
        label="Seasonal & Holiday",
        subcategory_id=uuid4(),
        subcategory_label="St Patricks Day",
        is_default=True,
    ),
    Category(
        id=MOCK_SEASONAL_HOLIDAY_ID,
        label="Seasonal & Holiday",
        subcategory_id=uuid4(),
        subcategory_label="Easter",
        is_default=True,
    ),
    Category(
        id=MOCK_SEASONAL_HOLIDAY_ID,
        label="Seasonal & Holiday",
        subcategory_id=uuid4(),
        subcategory_label="Independence Day",
        is_default=True,
    ),
    Category(
        id=MOCK_SEASONAL_HOLIDAY_ID,
        label="Seasonal & Holiday",
        subcategory_id=uuid4(),
        subcategory_label="Halloween/Haunt",
        is_default=True,
    ),
    Category(
        id=MOCK_SEASONAL_HOLIDAY_ID,
        label="Seasonal & Holiday",
        subcategory_id=uuid4(),
        subcategory_label="Thanksgiving",
        is_default=True,
    ),
    Category(
        id=MOCK_SEASONAL_HOLIDAY_ID,
        label="Seasonal & Holiday",
        subcategory_id=uuid4(),
        subcategory_label="Christmas",
        is_default=True,
    ),
    Category(
        id=MOCK_SEASONAL_HOLIDAY_ID,
        label="Seasonal & Holiday",
        subcategory_id=uuid4(),
        subcategory_label="Hannukah",
        is_default=True,
    ),
    Category(
        id=MOCK_SEASONAL_HOLIDAY_ID,
        label="Seasonal & Holiday",
        subcategory_id=uuid4(),
        subcategory_label="Fall Events",
        is_default=True,
    ),
    Category(
        id=MOCK_SEASONAL_HOLIDAY_ID,
        label="Seasonal & Holiday",
        subcategory_id=uuid4(),
        subcategory_label="New Years Eve",
        is_default=True,
    ),
    Category(
        id=MOCK_SEASONAL_HOLIDAY_ID,
        label="Seasonal & Holiday",
        subcategory_id=uuid4(),
        subcategory_label="Other",
        is_default=True,
    ),
    Category(
        id=MOCK_FOOD_DRINK_ID, label="Food & Drink", subcategory_id=uuid4(), subcategory_label="Beer", is_default=True
    ),
    Category(
        id=MOCK_FOOD_DRINK_ID, label="Food & Drink", subcategory_id=uuid4(), subcategory_label="Wine", is_default=True
    ),
    Category(
        id=MOCK_FOOD_DRINK_ID, label="Food & Drink", subcategory_id=uuid4(), subcategory_label="Food", is_default=True
    ),
    Category(
        id=MOCK_FOOD_DRINK_ID,
        label="Food & Drink",
        subcategory_id=uuid4(),
        subcategory_label="Spirits",
        is_default=True,
    ),
    Category(
        id=MOCK_FOOD_DRINK_ID, label="Food & Drink", subcategory_id=uuid4(), subcategory_label="Other", is_default=True
    ),
    Category(
        id=MOCK_FILM_MEDIA_ENTERTAINMENT_ID,
        label="Film, Media & Entertainment",
        subcategory_id=uuid4(),
        subcategory_label="TV",
        is_default=True,
    ),
    Category(
        id=MOCK_FILM_MEDIA_ENTERTAINMENT_ID,
        label="Film, Media & Entertainment",
        subcategory_id=uuid4(),
        subcategory_label="Film",
        is_default=True,
    ),
    Category(
        id=MOCK_FILM_MEDIA_ENTERTAINMENT_ID,
        label="Film, Media & Entertainment",
        subcategory_id=uuid4(),
        subcategory_label="Anime",
        is_default=True,
    ),
    Category(
        id=MOCK_FILM_MEDIA_ENTERTAINMENT_ID,
        label="Film, Media & Entertainment",
        subcategory_id=uuid4(),
        subcategory_label="Gaming",
        is_default=True,
    ),
    Category(
        id=MOCK_FILM_MEDIA_ENTERTAINMENT_ID,
        label="Film, Media & Entertainment",
        subcategory_id=uuid4(),
        subcategory_label="Comics",
        is_default=True,
    ),
    Category(
        id=MOCK_FILM_MEDIA_ENTERTAINMENT_ID,
        label="Film, Media & Entertainment",
        subcategory_id=uuid4(),
        subcategory_label="Adult",
        is_default=True,
    ),
    Category(
        id=MOCK_FILM_MEDIA_ENTERTAINMENT_ID,
        label="Film, Media & Entertainment",
        subcategory_id=uuid4(),
        subcategory_label="Comedy",
        is_default=True,
    ),
    Category(
        id=MOCK_FILM_MEDIA_ENTERTAINMENT_ID,
        label="Film, Media & Entertainment",
        subcategory_id=uuid4(),
        subcategory_label="Other",
        is_default=True,
    ),
    Category(
        id=MOCK_MUSIC_ID,
        label="Music",
        subcategory_id=uuid4(),
        subcategory_label="Alternative / Indie",
        is_default=True,
    ),
    Category(
        id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Blues & Jazz", is_default=True
    ),
    Category(id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Classical", is_default=True),
    Category(id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Country", is_default=True),
    Category(
        id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="EDM / Electronic", is_default=True
    ),
    Category(id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Americana", is_default=True),
    Category(
        id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Hip Hop / Rap", is_default=True
    ),
    Category(id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Latin", is_default=True),
    Category(id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Metal", is_default=True),
    Category(id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Opera", is_default=True),
    Category(id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Pop", is_default=True),
    Category(id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="R&B", is_default=True),
    Category(id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Reggae", is_default=True),
    Category(id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Rock", is_default=True),
    Category(id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Top 40", is_default=True),
    Category(id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="DJ/Dance", is_default=True),
    Category(
        id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Experimental", is_default=True
    ),
    Category(
        id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Punk/Hardcore", is_default=True
    ),
    Category(
        id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Singer/Songwriter", is_default=True
    ),
    Category(id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="World", is_default=True),
    Category(id=MOCK_MUSIC_ID, label="Music", subcategory_id=uuid4(), subcategory_label="Other", is_default=True),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Theatre",
        is_default=True,
    ),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Musical",
        is_default=True,
    ),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Ballet",
        is_default=True,
    ),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Dance",
        is_default=True,
    ),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Opera",
        is_default=True,
    ),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Orchestra",
        is_default=True,
    ),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Craft",
        is_default=True,
    ),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Fine Art",
        is_default=True,
    ),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Literary Arts",
        is_default=True,
    ),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Sculpture",
        is_default=True,
    ),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Painting",
        is_default=True,
    ),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Design",
        is_default=True,
    ),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Jewelry",
        is_default=True,
    ),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Museums",
        is_default=True,
    ),
    Category(
        id=MOCK_ARTS_THEATRE_ID,
        label="Arts & Theater",
        subcategory_id=uuid4(),
        subcategory_label="Other",
        is_default=True,
    ),
    Category(id=MOCK_HOBBIES_ID, label="Hobbies", subcategory_id=uuid4(), subcategory_label="Auto", is_default=False),
    Category(
        id=MOCK_HOBBIES_ID,
        label="Hobbies",
        subcategory_id=uuid4(),
        subcategory_label="Motorcycle/ATV",
        is_default=False,
    ),
    Category(id=MOCK_HOBBIES_ID, label="Hobbies", subcategory_id=uuid4(), subcategory_label="Air", is_default=False),
    Category(
        id=MOCK_HOBBIES_ID, label="Hobbies", subcategory_id=uuid4(), subcategory_label="Anime/Comics", is_default=False
    ),
    Category(id=MOCK_HOBBIES_ID, label="Hobbies", subcategory_id=uuid4(), subcategory_label="Gaming", is_default=False),
    Category(id=MOCK_HOBBIES_ID, label="Hobbies", subcategory_id=uuid4(), subcategory_label="DIY", is_default=False),
    Category(
        id=MOCK_HOBBIES_ID, label="Hobbies", subcategory_id=uuid4(), subcategory_label="Photography", is_default=False
    ),
    Category(
        id=MOCK_HOBBIES_ID, label="Hobbies", subcategory_id=uuid4(), subcategory_label="Knitting", is_default=False
    ),
    Category(id=MOCK_HOBBIES_ID, label="Hobbies", subcategory_id=uuid4(), subcategory_label="Books", is_default=False),
    Category(id=MOCK_HOBBIES_ID, label="Hobbies", subcategory_id=uuid4(), subcategory_label="Adult", is_default=False),
    Category(
        id=MOCK_HOBBIES_ID,
        label="Hobbies",
        subcategory_id=uuid4(),
        subcategory_label="Drawing & Painting",
        is_default=False,
    ),
    Category(
        id=MOCK_HOBBIES_ID,
        label="Hobbies",
        subcategory_id=uuid4(),
        subcategory_label="Pets & Animals",
        is_default=False,
    ),
    Category(
        id=MOCK_HOBBIES_ID, label="Hobbies", subcategory_id=uuid4(), subcategory_label="Home & Garden", is_default=False
    ),
    Category(
        id=MOCK_FITNESS_OUTDOORS_ID,
        label="Fitness & Outdoors",
        subcategory_id=uuid4(),
        subcategory_label="Hiking",
        is_default=True,
    ),
    Category(
        id=MOCK_FITNESS_OUTDOORS_ID,
        label="Fitness & Outdoors",
        subcategory_id=uuid4(),
        subcategory_label="Kayaking",
        is_default=False,
    ),
    Category(
        id=MOCK_FITNESS_OUTDOORS_ID,
        label="Fitness & Outdoors",
        subcategory_id=uuid4(),
        subcategory_label="Climbing",
        is_default=False,
    ),
    Category(
        id=MOCK_FITNESS_OUTDOORS_ID,
        label="Fitness & Outdoors",
        subcategory_id=uuid4(),
        subcategory_label="Walking",
        is_default=True,
    ),
    Category(
        id=MOCK_FITNESS_OUTDOORS_ID,
        label="Fitness & Outdoors",
        subcategory_id=uuid4(),
        subcategory_label="Biking",
        is_default=False,
    ),
    Category(
        id=MOCK_FITNESS_OUTDOORS_ID,
        label="Fitness & Outdoors",
        subcategory_id=uuid4(),
        subcategory_label="Botanical Gardens",
        is_default=True,
    ),
]


async def restaurant_categories_query(*, info: strawberry.Info) -> list[Category]:
    # TODO: Store Vivial->Google Places category mappings in DB.
    # https://docs.google.com/spreadsheets/d/1FfuMVBXhxvmRZH4633jgvswEt8BPOO_gzQm8VBRi3XY/edit?gid=463849599#gid=463849599
    # TODO: Fetch Vivial restaurant categories from DB (client doesn't need the Google Places mappings).
    return MOCK_RESTAURANT_CATEGORIES


async def activity_categories_query(*, info: strawberry.Info) -> list[Category]:
    # TODO: Store Vivial->Eventbrite category mappings in DB.
    # https://docs.google.com/spreadsheets/d/1FfuMVBXhxvmRZH4633jgvswEt8BPOO_gzQm8VBRi3XY/edit?gid=463849599#gid=463849599
    # TODO: Fetch Vivial activity categories from DB (client doesn't need the Eventbrite mappings).
    return MOCK_ACTIVITY_CATEGORIES
