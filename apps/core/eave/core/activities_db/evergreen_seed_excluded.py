# isort: off

import math
import sys

sys.path.append(".")

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

load_standard_dotenv_files()

# isort: on

# ruff: noqa: E402

import asyncio

from sqlalchemy.dialects.postgresql import Range

from eave.core import database
from eave.core.lib.google_places import GoogleMapsUtility, GooglePlacesUtility
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.evergreen_activity import EvergreenActivityOrm, EvergreenActivityTicketTypeOrm, WeeklyScheduleOrm
from eave.core.orm.image import ImageOrm


def day_to_min(day: int) -> int:
    return day * 24 * 60


def hour_to_min(hour: int) -> int:
    return hour * 60


# Title,Description,Address,Images,Category,Subcategory,Format,Availability (Days & Hours),Duration (Minutes),Ticket Type A,Ticket Type A Cost,Ticket Type B,Ticket Type B Cost,Taxes,Service Fees,Bookable,Book URL


async def import_evergreen_activities() -> None:
    await build_evergreen_activity(
        title="Wine Tasting at San Antonio Winery",
        description="""San Antonio Winery in Downtown Los Angeles offers a delightful wine-tasting experience in a historic and charming setting. Established in 1917, it's the oldest and last remaining winery in the city, blending Old World tradition with a modern, inviting atmosphere. The winery features an extensive selection of award-winning wines, ranging from robust reds and crisp whites to sweet dessert varieties, catering to all palates.
Visitors can enjoy guided tastings led by knowledgeable staff, who share insights about the winemaking process, the region's history, and pairing suggestions. The experience is complemented by the elegant tasting room, adorned with rustic décor that reflects the winery's rich heritage.
Afterward, guests can dine at Maddalena Restaurant, located on-site, which serves Italian-inspired dishes that pair beautifully with the wines. Whether you're a seasoned connoisseur or a curious beginner, San Antonio Winery provides a welcoming and educational journey into the world of wine, right in the heart of Los Angeles.""",
        address="737 Lamar St, Los Angeles, CA 90031",
        image_urls=[
            "https://lh3.googleusercontent.com/p/AF1QipMr_inDBvrnwJYK1hWxynf8M8m9vDX3OMuKFi-V=s1360-w1360-h1020",
            "https://lh3.googleusercontent.com/p/AF1QipOiOfFCVO1TLlCE5UzNGxPLvoFdkZW-yTNe3Miy=s1360-w1360-h1020",
            "https://sanantoniowinery.com/wp-content/uploads/2024/02/6S9A0746-scaled.jpg",
        ],
        category="Food & Drink",
        subcategory="Wine",
        minute_spans_by_day=[
            Range(day_to_min(0) + hour_to_min(9), day_to_min(0) + hour_to_min(18), bounds="[)"),
            Range(day_to_min(1) + hour_to_min(9), day_to_min(1) + hour_to_min(18), bounds="[)"),
            Range(day_to_min(2) + hour_to_min(9), day_to_min(2) + hour_to_min(18), bounds="[)"),
            Range(day_to_min(3) + hour_to_min(9), day_to_min(3) + hour_to_min(18), bounds="[)"),
            Range(day_to_min(4) + hour_to_min(9), day_to_min(4) + hour_to_min(19), bounds="[)"),
            Range(day_to_min(5) + hour_to_min(9), day_to_min(5) + hour_to_min(19), bounds="[)"),
            Range(day_to_min(6) + hour_to_min(9), day_to_min(6) + hour_to_min(19), bounds="[)"),
        ],
        duration=90,
        ticket_type="Wine Flights (select onsite)",
        ticket_max_cost=100,
        ticket_min_cost=50,
        tax_percentage=0,
        fees_dollars=0,
        bookable=False,
        booking_url=None,
    )
    await build_evergreen_activity(
        title="Wine Tasting at Angeleno Wine Co.",
        description="With a focus on unique varietals, Angeleno Wine Co. aims to push the boundaries of what Southern California wine growing can be. Tannat, Graciano, Godello, Loureiro, Treixadura and Alicante Bouschet are some of the unique varietals that Angeleno makes into wine every year. Our wines are naturally made and 100% vegan. We strive to make wines that are elegant, balanced and that express Los Angeles' unique character: a growing region where the desert meets the sea.",
        address="1646 N Spring St, Los Angeles, CA 90012",
        image_urls=[
            "https://s3-media0.fl.yelpcdn.com/bphoto/-mGE8JEq5XAiBHPTRa2dlw/o.jpg",
            "https://s3-media0.fl.yelpcdn.com/bphoto/yW-8Y5xgiuqf2j7ccIlbkA/o.jpg",
            "https://s3-media0.fl.yelpcdn.com/bphoto/apsmSVXdZsV8S0m4nxfLpg/o.jpg",
        ],
        category="Food & Drink",
        subcategory="Wine",
        minute_spans_by_day=[
            Range(day_to_min(5) + hour_to_min(12), day_to_min(5) + hour_to_min(20), bounds="[)"),
            Range(day_to_min(6) + hour_to_min(12), day_to_min(6) + hour_to_min(18), bounds="[)"),
        ],
        duration=90,
        ticket_type="Wine Flights (select onsite)",
        ticket_max_cost=100,
        ticket_min_cost=50,
        tax_percentage=0,
        fees_dollars=0,
        bookable=False,
        booking_url=None,
    )
    await build_evergreen_activity(
        title="Wine Tasting at Quartini & Pintxos SVLK Tasting Bar",
        description="""Our in-store tasting bar at Wine Stop SVLK was inspired by the classic European tasting bar experience. Here, we believe that enjoying a glass of quality appellation wine shouldn't come with a hefty price tag.
Much like the beloved local wine bars of Italy, Portugal, and Spain, we offer an inviting space where you can savor amazing wines by the glass, quartino, and bottle at very reasonable prices.
But that's not all—Q&P is the perfect spot for so many occasions!
Stop by while waiting to see a movie or after the credits roll for a relaxing glass of wine. Whether you're winding down after a long day, catching up with colleagues, simply exploring new flavors, meeting visiting friends before heading out for shopping or a walk, or enjoying a pre-dinner drink before your reservation, Q&P offers a welcoming atmosphere to unwind and discover new exciting flavors.
Come in, relax, and find your new favorite pour without breaking the bank. Cheers!""",
        address="2856 Sunset Boulevard, Los Angeles, CA 90026",
        image_urls=[
            "https://s3-media0.fl.yelpcdn.com/bphoto/9KVtHfM4UlS8nvdvaKQ5Sw/o.jpg",
            "https://s3-media0.fl.yelpcdn.com/bphoto/jyWAHpe2Hlc4AktWryA2UA/o.jpg",
            "https://s3-media0.fl.yelpcdn.com/bphoto/UEVamFnpZy3h-SoQcBMpcg/o.jpg",
        ],
        category="Food & Drink",
        subcategory="Wine",
        minute_spans_by_day=[
            Range(day_to_min(3) + hour_to_min(17), day_to_min(3) + hour_to_min(22), bounds="[)"),
            Range(day_to_min(4) + hour_to_min(17), day_to_min(4) + hour_to_min(22), bounds="[)"),
            Range(day_to_min(5) + hour_to_min(17), day_to_min(5) + hour_to_min(22), bounds="[)"),
            Range(day_to_min(6) + hour_to_min(13), day_to_min(6) + hour_to_min(20), bounds="[)"),
        ],
        duration=90,
        ticket_type="Wine Flights (select onsite)",
        ticket_max_cost=100,
        ticket_min_cost=50,
        tax_percentage=0,
        fees_dollars=0,
        bookable=False,
        booking_url=None,
    )
    await build_evergreen_activity(
        title="Kiss Kiss Bang Bang",
        description="""Kiss Kiss Bang Bang is a Disco-Deco dreamscape brought to you by the Houston Brothers. Come dance the night away with a heady mix of 1970's glitz and glam and the Gatsbyesque decadence of the roaring 1920s. Dress code enforced.
Kiss Kiss Bang Bang is a lively and stylish speakeasy-style bar nestled in the heart of Los Angeles, offering a retro-chic vibe with a modern twist. Known for its immersive atmosphere, this nightlife destination blends neon aesthetics with mid-century glamour, creating a playful yet sophisticated setting.
Guests are greeted by dim lighting, bold decor, and eclectic music spanning multiple genres. The drink menu features inventive craft cocktails with witty names and premium ingredients, appealing to adventurous palates. On some nights, DJs and live performers take the energy to the next level, making it a hotspot for socializing and dancing.
Located in the up-and-coming neighborhood of Koreatown, Kiss Kiss Bang Bang attracts a diverse crowd of locals and visitors, making it the perfect spot for a fun night out. Whether you're there for a quick drink or an all-night party, the bar's unique charm and welcoming vibe deliver a memorable experience.""",
        address="3515 Wilshire Blvd, Los Angeles, CA 90010",
        image_urls=[
            "https://cdn.vox-cdn.com/thumbor/TY2VNAeW-z0pd936NDKi4Frhsgg=/0x0:2000x1335/1200x675/filters:focal(840x508:1160x828)/cdn.vox-cdn.com/uploads/chorus_image/image/66268506/2020_02_05_KissKissBangBang_031.0.jpg",
            "https://i0.wp.com/nightclubslosangeles.com/wp-content/uploads/2022/07/Kiss-Kiss-Bang-Bang-Los-Angeles.jpeg?resize=950%2C635&ssl=1",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRsqY2jarHFeBVnOCI504s_vaQX8HCAgxT-jQ&s",
        ],
        category="Music",
        subcategory="DJ/Dance",
        minute_spans_by_day=[
            Range(day_to_min(3) + hour_to_min(21) + 30, day_to_min(4) + hour_to_min(2), bounds="[)"),
            Range(day_to_min(4) + hour_to_min(21) + 30, day_to_min(5) + hour_to_min(2), bounds="[)"),
            Range(day_to_min(5) + hour_to_min(21) + 30, day_to_min(6) + hour_to_min(2), bounds="[)"),
        ],
        bookable=False,
        booking_url=None,
        duration=120,
        ticket_type="Cover Fee (at door)",
        ticket_max_cost=20,
        ticket_min_cost=10,
        tax_percentage=0,
        fees_dollars=0,
    )
    await build_evergreen_activity(
        title='Guided Tours of "Nuestro Pueblo"  The Watts Towers',
        description="""*Purchase tickets on premise - CASH or CHECK ONLY*

The Watts Towers Tour Guide Program offers visitors a unique and in-depth look at one of Los Angeles' most iconic landmarks. Participants will be guided by knowledgeable tour guides through the towers, learning about the history, cultural significance, and artistic processes involved in their creation. The tour, which is the only way to gain access to the towers, will last approximately 30 minutes and highlight the life of Simon Rodia, the Italian immigrant who built the towers over a 33-year period, and the cultural and social context of the Watts neighborhood in which they stand. The tour also includes a visit to the Watts Towers Arts Center, where visitors can see rotating exhibitions of contemporary art and learn about the ongoing preservation efforts for the Towers. With this program, visitors will gain a greater appreciation for the Watts Towers as a masterpiece of folk art and a symbol of resilience and community spirit.""",
        address="10624 Graham Ave., Los Angeles, CA 90002",
        image_urls=[
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQjEXrs6n-ofhG3dKOrT71GESR3qXbTWXQz4Q&s",
            "https://www.parks.ca.gov/pages/613/images/P0078604.JPG",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTJMA4K4Jsr5ZgvUWsxXZo60eivcQaz1yMTfw&s",
        ],
        category="Arts & Theater",
        subcategory="Museums",
        minute_spans_by_day=[
            Range(day_to_min(3) + hour_to_min(11), day_to_min(3) + hour_to_min(13), bounds="[)"),
            Range(day_to_min(3) + hour_to_min(14), day_to_min(3) + hour_to_min(15) + 30, bounds="[)"),
            Range(day_to_min(4) + hour_to_min(11), day_to_min(4) + hour_to_min(13), bounds="[)"),
            Range(day_to_min(4) + hour_to_min(14), day_to_min(4) + hour_to_min(15) + 30, bounds="[)"),
            Range(day_to_min(5) + hour_to_min(11), day_to_min(5) + hour_to_min(13), bounds="[)"),
            Range(day_to_min(5) + hour_to_min(14), day_to_min(5) + hour_to_min(15) + 30, bounds="[)"),
        ],
        duration=30,
        ticket_type="General Admission",
        ticket_max_cost=7,
        ticket_min_cost=7,
        fees_dollars=0,
        tax_percentage=0,
        bookable=False,
        booking_url=None,
    )
    await build_evergreen_activity(
        title="The Gamble House",
        description="The Gamble House (1908) is an internationally recognized masterpiece of the American Arts and Crafts movement. Built for David and Mary Gamble of the Procter and Gamble Company, the house is the most complete and original example of the work of architects Charles and Henry Greene. This Local, State, and National Historic Landmark is owned by the City of Pasadena and operated by The Gamble House Conservancy.",
        address="4 Westmoreland Place, Pasadena, CA 91103",
        image_urls=[
            "https://upload.wikimedia.org/wikipedia/commons/a/a5/Gamble_House_2016-1.jpg",
            "https://gamblehouse.org/wp-content/uploads/2024/03/Students-at-Gamble-House.jpg",
            "https://gamblehouse.org/wp-content/uploads/2024/03/Gamble-House-Entry.jpg",
        ],
        category="Arts & Theater",
        subcategory="Museums",
        minute_spans_by_day=[
            Range(day_to_min(1) + hour_to_min(10), day_to_min(1) + hour_to_min(16), bounds="[)"),
            Range(day_to_min(3) + hour_to_min(10), day_to_min(3) + hour_to_min(16), bounds="[)"),
            Range(day_to_min(4) + hour_to_min(10), day_to_min(4) + hour_to_min(16), bounds="[)"),
            Range(day_to_min(5) + hour_to_min(10), day_to_min(5) + hour_to_min(16), bounds="[)"),
            Range(day_to_min(6) + hour_to_min(10), day_to_min(6) + hour_to_min(16), bounds="[)"),
        ],
        duration=90,
        ticket_type="Multiple Tour Selection - Book on premise (Purchase at bookstore)",
        ticket_min_cost=20,
        ticket_max_cost=100,
        tax_percentage=0,
        fees_dollars=0,
        bookable=False,
        booking_url=None,
    )


async def build_evergreen_activity(
    title: str,
    description: str,
    image_urls: list[str],
    address: str,
    category: str,
    subcategory: str | None,
    bookable: bool,  # noqa
    booking_url: str | None,
    duration: int,
    ticket_type: str,
    ticket_min_cost: int,
    ticket_max_cost: int,
    tax_percentage: int,
    fees_dollars: float,
    minute_spans_by_day: list[Range[int]],
) -> None:
    maps = GoogleMapsUtility()
    geocode_results = maps.geocode(address=address)
    assert len(geocode_results) > 0
    geocode_result = geocode_results[0]
    place_id = geocode_result.get("place_id")
    assert place_id

    places = GooglePlacesUtility()
    google_place = await places.get_google_place(place_id)
    assert google_place
    location = places.location_from_google_place(google_place)

    activity_category = next((a for a in ActivityCategoryOrm.all() if a.name == subcategory), None)
    if not activity_category:
        raise Exception(f"no matching category for {subcategory}")

    async with database.async_session.begin() as session:
        activity = EvergreenActivityOrm(
            session,
            activity_category_id=activity_category.id,
            address=location.address.to_address(),
            booking_url=booking_url,
            coordinates=location.coordinates,
            description=description,
            duration_minutes=duration,
            google_place_id=place_id,
            is_bookable=bookable,
            title=title,
        )

        WeeklyScheduleOrm(
            session,
            evergreen_activity=activity,
            week_of=None,
            minute_spans_local=minute_spans_by_day,
        )

        for image in image_urls:
            img = ImageOrm(
                session,
                src=image.strip(),
                alt=None,
            )

            activity.images.append(img)

        activity.ticket_types.append(
            EvergreenActivityTicketTypeOrm(
                session,
                evergreen_activity=activity,
                min_base_cost_cents=math.floor(ticket_min_cost * 100),
                max_base_cost_cents=math.floor(ticket_max_cost * 100),
                service_fee_cents=math.floor(fees_dollars * 100),
                tax_percentage=tax_percentage,
                title=ticket_type,
            )
        )


if __name__ == "__main__":
    asyncio.run(import_evergreen_activities())
