from dataclasses import dataclass
from types import MappingProxyType
from uuid import UUID


@dataclass(kw_only=True, frozen=True)
class ActivityCategoryOrm:
    id: UUID
    name: str
    is_default: bool
    is_manually_curated: bool
    activity_category_group_id: UUID
    eventbrite_subcategory_ids: list[str]

    @classmethod
    def all(cls) -> list["ActivityCategoryOrm"]:
        return list(_ACTIVITY_CATEGORIES_TABLE)  # shallow copy

    @classmethod
    def one_or_exception(cls, *, activity_category_id: UUID) -> "ActivityCategoryOrm":
        return _ACTIVITY_CATEGORIES_PK[activity_category_id]

    @classmethod
    def one_or_none(cls, *, activity_category_id: UUID) -> "ActivityCategoryOrm | None":
        return _ACTIVITY_CATEGORIES_PK.get(activity_category_id)

    @classmethod
    def get_by_eventbrite_subcategory_id(cls, *, eventbrite_subcategory_id: str) -> "ActivityCategoryOrm | None":
        return _ACTIVITY_CATEGORIES_EBID_IDX.get(eventbrite_subcategory_id)

    @classmethod
    def get_by_activity_category_group_id(cls, *, activity_category_group_id: UUID) -> list["ActivityCategoryOrm"]:
        return _ACTIVITY_CATEGORIES_CATEGORY_GROUP_ID_IDX.get(activity_category_group_id, [])

    @classmethod
    def defaults(cls) -> list["ActivityCategoryOrm"]:
        return list(_DEFAULT_ACTIVITY_CATEGORIES)  # shallow copy


_ACTIVITY_CATEGORIES_TABLE = (
    ActivityCategoryOrm(
        id=UUID("bb6ceceeec6c4e0fb12f1a188b89a2da"),
        name="St Patricks Day",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("c44d71bc95bd4a5bb66a7a97c68250ec"),
        eventbrite_subcategory_ids=["16001"],
    ),
    ActivityCategoryOrm(
        id=UUID("bec246c04fc14be9a5b7033623e187a0"),
        name="Easter",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("c44d71bc95bd4a5bb66a7a97c68250ec"),
        eventbrite_subcategory_ids=["16002"],
    ),
    ActivityCategoryOrm(
        id=UUID("4caf07eede164d788fc118fae8fdad96"),
        name="Independence Day",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("c44d71bc95bd4a5bb66a7a97c68250ec"),
        eventbrite_subcategory_ids=["16003"],
    ),
    ActivityCategoryOrm(
        id=UUID("c96d127101f74f3ea0e7b51b858e21db"),
        name="Halloween/Haunt",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("c44d71bc95bd4a5bb66a7a97c68250ec"),
        eventbrite_subcategory_ids=["16004"],
    ),
    ActivityCategoryOrm(
        id=UUID("8233dcef41ac42ddab863ee732d990ab"),
        name="Thanksgiving",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("c44d71bc95bd4a5bb66a7a97c68250ec"),
        eventbrite_subcategory_ids=["16005"],
    ),
    ActivityCategoryOrm(
        id=UUID("c9f19a939f0246839c9032e1da39d3b1"),
        name="Christmas",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("c44d71bc95bd4a5bb66a7a97c68250ec"),
        eventbrite_subcategory_ids=["16006"],
    ),
    ActivityCategoryOrm(
        id=UUID("e1811d506bd34cd7b77be0612cae9004"),
        name="Channukah",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("c44d71bc95bd4a5bb66a7a97c68250ec"),
        eventbrite_subcategory_ids=["16007"],
    ),
    ActivityCategoryOrm(
        id=UUID("1117ad156d9341878a0fbcc467d5ba52"),
        name="Fall events",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("c44d71bc95bd4a5bb66a7a97c68250ec"),
        eventbrite_subcategory_ids=["16008"],
    ),
    ActivityCategoryOrm(
        id=UUID("e8b8ee2b04b546f69b87b4adac689703"),
        name="New Years Eve",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("c44d71bc95bd4a5bb66a7a97c68250ec"),
        eventbrite_subcategory_ids=["16009"],
    ),
    ActivityCategoryOrm(
        id=UUID("6eb87a9524894b7d81484967a625a3b6"),
        name="Other",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("c44d71bc95bd4a5bb66a7a97c68250ec"),
        eventbrite_subcategory_ids=["16999"],
    ),
    ActivityCategoryOrm(
        id=UUID("0029283722634cefbe520adb1a801d03"),
        name="Beer",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("f3a21e9638d2401ebc290fee6fe44384"),
        eventbrite_subcategory_ids=["10001"],
    ),
    ActivityCategoryOrm(
        id=UUID("eb74e5976fdc4d3ba47494d9f99ff0ca"),
        name="Wine",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("f3a21e9638d2401ebc290fee6fe44384"),
        eventbrite_subcategory_ids=["10002"],
    ),
    ActivityCategoryOrm(
        id=UUID("e68caeb87d6b46d3a7fe7ca566cef03a"),
        name="Food",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("f3a21e9638d2401ebc290fee6fe44384"),
        eventbrite_subcategory_ids=["10003"],
    ),
    ActivityCategoryOrm(
        id=UUID("f5a9f44253ec4ab4a9ef42b42725e69e"),
        name="Spirits",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("f3a21e9638d2401ebc290fee6fe44384"),
        eventbrite_subcategory_ids=["10004"],
    ),
    ActivityCategoryOrm(
        id=UUID("9d6cefdfc73e4be3ba8092c41da28fce"),
        name="Other",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("f3a21e9638d2401ebc290fee6fe44384"),
        eventbrite_subcategory_ids=["10999"],
    ),
    ActivityCategoryOrm(
        id=UUID("5d5a5fa478d147f8bf5386a1539f1737"),
        name="TV",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("64064c758d894eac9613f23cb6da6fd1"),
        eventbrite_subcategory_ids=["4001"],
    ),
    ActivityCategoryOrm(
        id=UUID("e28d08bfb22a4701ac55a152503f1cc0"),
        name="Film",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("64064c758d894eac9613f23cb6da6fd1"),
        eventbrite_subcategory_ids=["4002"],
    ),
    ActivityCategoryOrm(
        id=UUID("fc7f96da9a7e4c3d9117b7b58c28815a"),
        name="Anime",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("64064c758d894eac9613f23cb6da6fd1"),
        eventbrite_subcategory_ids=["4003"],
    ),
    ActivityCategoryOrm(
        id=UUID("f734097d915b4a2c9585d10ee1ab9a31"),
        name="Gaming",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("64064c758d894eac9613f23cb6da6fd1"),
        eventbrite_subcategory_ids=["4004"],
    ),
    ActivityCategoryOrm(
        id=UUID("22366fcf52364532a279d31f5a330c1c"),
        name="Comics",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("64064c758d894eac9613f23cb6da6fd1"),
        eventbrite_subcategory_ids=["4005"],
    ),
    ActivityCategoryOrm(
        id=UUID("9fa1f54dcbb94dd6b127d8d2e10db33a"),
        name="Adult",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("64064c758d894eac9613f23cb6da6fd1"),
        eventbrite_subcategory_ids=["4006"],
    ),
    ActivityCategoryOrm(
        id=UUID("6a8686d3a985469387ef5fc4732a2e8f"),
        name="Comedy",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("64064c758d894eac9613f23cb6da6fd1"),
        eventbrite_subcategory_ids=["4007", "5010"],
    ),
    ActivityCategoryOrm(
        id=UUID("59ffdf67bb0f487ba9b4f8955c71b20c"),
        name="Boats & Cruises",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("64064c758d894eac9613f23cb6da6fd1"),
        eventbrite_subcategory_ids=["18003"],
    ),
    ActivityCategoryOrm(
        id=UUID("05425f277e304d8590c9ad2d0be7cd72"),
        name="Other",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("64064c758d894eac9613f23cb6da6fd1"),
        eventbrite_subcategory_ids=["4999"],
    ),
    ActivityCategoryOrm(
        id=UUID("109b3339ad5c409891edd8a484bc118e"),
        name="Alternative / Indie",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3001", "3009"],
    ),
    ActivityCategoryOrm(
        id=UUID("ac77b63be7004e63912f24d6735370e0"),
        name="Blues & Jazz",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3002", "3022", "3027"],
    ),
    ActivityCategoryOrm(
        id=UUID("e9d46ee39a4d4c48b80b360bc2dae044"),
        name="Classical",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3003"],
    ),
    ActivityCategoryOrm(
        id=UUID("930aa074db984a2899e3daed73d40ea0"),
        name="Country",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3004"],
    ),
    ActivityCategoryOrm(
        id=UUID("adbe6d3879bd4fdfb9f3979daf7abb28"),
        name="EDM / Electronic",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3006", "3024", "3025"],
    ),
    ActivityCategoryOrm(
        id=UUID("e99ed47827af45289aa995beb9e39dd8"),
        name="Americana",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3007", "3019", "3020", "3021"],
    ),
    ActivityCategoryOrm(
        id=UUID("a35cb10f8fff47509d8c43742f7822f8"),
        name="Hip Hop / Rap",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3008"],
    ),
    ActivityCategoryOrm(
        id=UUID("9ba3ac761df84b7fb10a4e1977f04d44"),
        name="Latin",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3010"],
    ),
    ActivityCategoryOrm(
        id=UUID("9bf9a0b8b3db46b68c2c5f44589df084"),
        name="Metal",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3011"],
    ),
    ActivityCategoryOrm(
        id=UUID("14de24b63532453cafd74a72eededd9e"),
        name="Opera",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3012"],
    ),
    ActivityCategoryOrm(
        id=UUID("544872e1a6274d95bb8ea319862f1836"),
        name="Pop",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3013"],
    ),
    ActivityCategoryOrm(
        id=UUID("eff8767feb8a48fe896b86b5d037a185"),
        name="R&B",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3014"],
    ),
    ActivityCategoryOrm(
        id=UUID("0241442022b040cba448538d57f87976"),
        name="Reggae",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3015"],
    ),
    ActivityCategoryOrm(
        id=UUID("d9d75f420eb4402889826e7c78b0245c"),
        name="Rock",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3017"],
    ),
    ActivityCategoryOrm(
        id=UUID("997bcc5d3d0547b39c2c179c49291039"),
        name="Top 40",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3018"],
    ),
    ActivityCategoryOrm(
        id=UUID("6a33b795ac784eb7b98436e7170cac52"),
        name="DJ/Dance",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3023"],
    ),
    ActivityCategoryOrm(
        id=UUID("758e04a5da8a4c1381b2755903426641"),
        name="Experimental",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3026", "3028"],
    ),
    ActivityCategoryOrm(
        id=UUID("5ae127fefc0d4ae99c1076ddb2c488f6"),
        name="Punk/Hardcore",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3029"],
    ),
    ActivityCategoryOrm(
        id=UUID("d75f88c8b19a40e2a65f27a4a46cf2fb"),
        name="Singer/Songwriter",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3030"],
    ),
    ActivityCategoryOrm(
        id=UUID("508255627fdf496896877c7c7ccf8eec"),
        name="World",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3031", "3005"],
    ),
    ActivityCategoryOrm(
        id=UUID("0785dbb1676546f7b457096139363fc4"),
        name="Other",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("68917f14a9354a4382829b43d99c9ba8"),
        eventbrite_subcategory_ids=["3999"],
    ),
    ActivityCategoryOrm(
        id=UUID("175c5d8184cd4beea05de77e37321b86"),
        name="Theatre",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=["5001"],
    ),
    ActivityCategoryOrm(
        id=UUID("545d46fa27454e7c934a914f6474226a"),
        name="Musical",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=["5002"],
    ),
    ActivityCategoryOrm(
        id=UUID("3cf8061ab08f48e8ae3f7a64e75dc5fa"),
        name="Ballet",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=["5003"],
    ),
    ActivityCategoryOrm(
        id=UUID("18be5db4d5b0474dbc954a8db59636e8"),
        name="Dance",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=["5004"],
    ),
    ActivityCategoryOrm(
        id=UUID("9154932b8fa94748bb3e05513fd47863"),
        name="Opera",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=["5005"],
    ),
    ActivityCategoryOrm(
        id=UUID("00ea927e544844fb9d9d4a5d9da48312"),
        name="Orchestra",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=["5006"],
    ),
    ActivityCategoryOrm(
        id=UUID("3132c46139a24add8fe5771865e47384"),
        name="Craft",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=["5007"],
    ),
    ActivityCategoryOrm(
        id=UUID("b51d48cea0fa4d9992a11d7ac40b75ec"),
        name="Fine Art",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=["5008"],
    ),
    ActivityCategoryOrm(
        id=UUID("93141507f9064df08db3bbc90c4d00a5"),
        name="Literary Arts",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=["5009"],
    ),
    ActivityCategoryOrm(
        id=UUID("7705289d18c44484b4514e786bbc01ce"),
        name="Sculpture",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=["5011"],
    ),
    ActivityCategoryOrm(
        id=UUID("3a9a051de18f495794d9a6e8c92c971c"),
        name="Painting",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=["5012"],
    ),
    ActivityCategoryOrm(
        id=UUID("0f8d2aa76cbe48fd90fa825e44423ab5"),
        name="Design",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=["5013"],
    ),
    ActivityCategoryOrm(
        id=UUID("5a0fe0ec867e42649f9125fe4ab2414d"),
        name="Jewelry",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=["5014"],
    ),
    ActivityCategoryOrm(
        id=UUID("c138128a61ec4b8a90db16f394ca792b"),
        name="Other",
        is_default=True,
        is_manually_curated=False,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=["5999"],
    ),
    ActivityCategoryOrm(
        id=UUID("8be06cf7e3aa444c80ce2e771f270072"),
        name="Museums",
        is_default=True,
        is_manually_curated=True,
        activity_category_group_id=UUID("988e0bf142564462985a2657602aad1b"),
        eventbrite_subcategory_ids=[],
    ),
    ActivityCategoryOrm(
        id=UUID("bd4b7b603dad456d9290550614591a32"),
        name="Auto",
        is_default=False,
        is_manually_curated=False,
        activity_category_group_id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        eventbrite_subcategory_ids=["18001"],
    ),
    ActivityCategoryOrm(
        id=UUID("9f04aed67aa6465bb6f37d25dfc6b7bc"),
        name="Motorcycle/ATV",
        is_default=False,
        is_manually_curated=False,
        activity_category_group_id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        eventbrite_subcategory_ids=["18002"],
    ),
    ActivityCategoryOrm(
        id=UUID("2d1dfd2d23e042a2a9af15444229214d"),
        name="Air",
        is_default=False,
        is_manually_curated=False,
        activity_category_group_id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        eventbrite_subcategory_ids=["18004"],
    ),
    ActivityCategoryOrm(
        id=UUID("29116796602745829386535303be5653"),
        name="Anime/Comics",
        is_default=False,
        is_manually_curated=False,
        activity_category_group_id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        eventbrite_subcategory_ids=["19001"],
    ),
    ActivityCategoryOrm(
        id=UUID("44c7de44df4f4a8c814934a2a92e2f3f"),
        name="Gaming",
        is_default=False,
        is_manually_curated=False,
        activity_category_group_id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        eventbrite_subcategory_ids=["19002"],
    ),
    ActivityCategoryOrm(
        id=UUID("857e60b7381d4f08955120741dcbc6cc"),
        name="DIY",
        is_default=False,
        is_manually_curated=False,
        activity_category_group_id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        eventbrite_subcategory_ids=["19003"],
    ),
    ActivityCategoryOrm(
        id=UUID("15de119a1815467f9d8a2b9a3468630d"),
        name="Photography",
        is_default=False,
        is_manually_curated=False,
        activity_category_group_id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        eventbrite_subcategory_ids=["19004"],
    ),
    ActivityCategoryOrm(
        id=UUID("b2a740a876074c498f9e74db29afc169"),
        name="Knitting",
        is_default=False,
        is_manually_curated=False,
        activity_category_group_id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        eventbrite_subcategory_ids=["19005"],
    ),
    ActivityCategoryOrm(
        id=UUID("7ce5ac6dc9fa4770b6e9e2586185fcbd"),
        name="Books",
        is_default=False,
        is_manually_curated=True,
        activity_category_group_id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        eventbrite_subcategory_ids=["19006"],
    ),
    ActivityCategoryOrm(
        id=UUID("19632d3e007e4a18a9f3b282742eb425"),
        name="Adult",
        is_default=False,
        is_manually_curated=False,
        activity_category_group_id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        eventbrite_subcategory_ids=["19007"],
    ),
    ActivityCategoryOrm(
        id=UUID("b55e6792a93041409cae632607632f15"),
        name="Drawing & Painting",
        is_default=False,
        is_manually_curated=False,
        activity_category_group_id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        eventbrite_subcategory_ids=["19008"],
    ),
    ActivityCategoryOrm(
        id=UUID("07f19c38766047fcbc8670cae3d93c5c"),
        name="Pets & Animals",
        is_default=False,
        is_manually_curated=True,
        activity_category_group_id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        eventbrite_subcategory_ids=["17002"],
    ),
    ActivityCategoryOrm(
        id=UUID("6d018ecd566f477eab40de3a1f8388b8"),
        name="Home & Garden",
        is_default=False,
        is_manually_curated=False,
        activity_category_group_id=UUID("12e3ee96b00641c58e2a6ba3567816d3"),
        eventbrite_subcategory_ids=["17003"],
    ),
    ActivityCategoryOrm(
        id=UUID("6a5e0da4e7524022a7f00923fed6bbfa"),
        name="Hiking",
        is_default=True,
        is_manually_curated=True,
        activity_category_group_id=UUID("c0f686d1a4da425ab5c060e2b62344fc"),
        eventbrite_subcategory_ids=["9001"],
    ),
    ActivityCategoryOrm(
        id=UUID("af34d9e559db4a39b18aa5f221b6c923"),
        name="Kayaking",
        is_default=False,
        is_manually_curated=True,
        activity_category_group_id=UUID("c0f686d1a4da425ab5c060e2b62344fc"),
        eventbrite_subcategory_ids=["9003"],
    ),
    ActivityCategoryOrm(
        id=UUID("f08a5ed6cdcc42e0a5d8d66646a06858"),
        name="Climbing",
        is_default=False,
        is_manually_curated=True,
        activity_category_group_id=UUID("c0f686d1a4da425ab5c060e2b62344fc"),
        eventbrite_subcategory_ids=["9005"],
    ),
    ActivityCategoryOrm(
        id=UUID("d5e10852c14b4672aff30e387c3e5ca2"),
        name="Walking",
        is_default=True,
        is_manually_curated=True,
        activity_category_group_id=UUID("c0f686d1a4da425ab5c060e2b62344fc"),
        eventbrite_subcategory_ids=[],
    ),
    ActivityCategoryOrm(
        id=UUID("e79a9e28b1fd40a08ce4fa9ac3a18971"),
        name="Biking",
        is_default=False,
        is_manually_curated=True,
        activity_category_group_id=UUID("c0f686d1a4da425ab5c060e2b62344fc"),
        eventbrite_subcategory_ids=[],
    ),
    ActivityCategoryOrm(
        id=UUID("33c323801f0c406bb4c3a0c12d59716a"),
        name="Botanical Gardens",
        is_default=True,
        is_manually_curated=True,
        activity_category_group_id=UUID("c0f686d1a4da425ab5c060e2b62344fc"),
        eventbrite_subcategory_ids=[],
    ),
    ActivityCategoryOrm(
        id=UUID("390831bc03f4433abe6700969bd2bbcc"),
        name="Water & Boating",
        is_default=True,
        is_manually_curated=True,
        activity_category_group_id=UUID("c0f686d1a4da425ab5c060e2b62344fc"),
        eventbrite_subcategory_ids=[],
    ),
    ActivityCategoryOrm(
        id=UUID("fd5ab13e2f6c4c45b9e0c4931a9b261a"),
        name="Horseback Riding",
        is_default=True,
        is_manually_curated=True,
        activity_category_group_id=UUID("c0f686d1a4da425ab5c060e2b62344fc"),
        eventbrite_subcategory_ids=[],
    ),
)

_ACTIVITY_CATEGORIES_PK = MappingProxyType({cat.id: cat for cat in _ACTIVITY_CATEGORIES_TABLE})

_ACTIVITY_CATEGORIES_EBID_IDX = MappingProxyType(
    {ebid: cat for cat in _ACTIVITY_CATEGORIES_TABLE for ebid in cat.eventbrite_subcategory_ids}
)


def _make_category_group_id_idx() -> MappingProxyType[UUID, list[ActivityCategoryOrm]]:
    idx: dict[UUID, list[ActivityCategoryOrm]] = {}
    for cat in _ACTIVITY_CATEGORIES_TABLE:
        idx.setdefault(cat.activity_category_group_id, [])
        idx[cat.activity_category_group_id].append(cat)
    return MappingProxyType(idx)


_ACTIVITY_CATEGORIES_CATEGORY_GROUP_ID_IDX = _make_category_group_id_idx()

_DEFAULT_ACTIVITY_CATEGORIES = [cat for cat in _ACTIVITY_CATEGORIES_TABLE if cat.is_default]
