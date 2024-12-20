# isort: off

import sys


sys.path.append(".")

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

load_standard_dotenv_files()

# isort: on

# ruff: noqa: E402

import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from pprint import pprint
import random

from aiohttp import ClientResponseError

import eave.core.database
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.activity_format import ActivityFormatOrm
from eave.core.orm.eventbrite_event import EventbriteEventOrm
from eave.stdlib.eventbrite.client import EventbriteClient, ListEventsQuery, OrderBy
from eave.stdlib.eventbrite.models.event import EventStatus
from eave.stdlib.eventbrite.models.expansions import Expansion
from eave.stdlib.logging import LOGGER
from eave.stdlib.typing import JsonObject
from eave.stdlib.time import LOS_ANGELES_TIMEZONE



# These are hand-picked by Vivial staff
_EVENTBRITE_ORGANIZER_IDS = {
    "48911761313",
    "26796434141",
    "88553967793",
    "34632551663",
    "26776278029",
    "79143220483",
    "34211184597",
    "33957525325",
    "87660637953",
    "17814628551",
    "62788201173",
    "42072740953",
    "68721082653",
    "52961985803",
    "32986481267",
    "98444000781",
    "9885768343",
    "73830137433",
    "86474824963",
    "90573063213",
    "13289593491",
    "20220039381",
    "34355803895",
    "46818510413",
    "28493531241",
    "104111326291",
    "12686317917",
    "26369713863",
    "36665060323",
    "58553675543",
    "2250648021",
    "61311022803",
    "24762733193",
    "26817846989",
    "42895439813",
    "43205656233",
    "7820184768",
    "39560769383",
    "50402624813",
    "84972602503",
    "32775246905",
    "22786337594",
    "65639128943",
    "49287976513",
    "58995879453",
    "60129298233",
    "93636931203",
    "19172721115",
    "62947871093",
    "11249610877",
    "90081012803",
    "17408675634",
    "40410365213",
    "58136354603",
    "75753930373",
    "31125575477",
    "68235366273",
    "15433390756",
    "52816846893",
    "39269232813",
    "76056191493",
    "60462031173",
    "76555915243",
    "33801476577",
    "42514401083",
    "9781640515",
    "66723184583",
    "13794689586",
    "82851679243",
    "34388086301",
    "18430092853",
    "48108709023",
    "61456675283",
    "86524288803",
    "55455569553",
    "7519974907",
    "33815338939",
    "47693341663",
    "56635511733",
    "33427218985",
    "25319501479",
    "33898057947",
    "26901438059",
    "72707090753",
    "60021156503",
    "66799777003",
    "34444860961",
    "103395943421",
    "3958753645",
    "56319434573",
    "13238834649",
    "75704023453",
    "34936776433",
    "30684421868",
    "18338262509",
    "31921194093",
    "80185304363",
    "42327622723",
    "19227081996",
    "14349236430",
    "66755891943",
    "84687752413",
    "416807370",
    "30643648438",
    "15166975815",
    "15201693147",
    "66876178093",
    "12408817920",
    "28197753187",
    "17845928125",
    "50834577463",
    "102888898781",
    "54089473353",
    "31720676225",
    "7770305037",
    "32752281263",
    "17723511163",
    "17976072805",
    "85863727013",
    "38438578653",
    "33265156433",
    "102396949071",
    "41336835423",
    "14584771716",
    "96352034813",
    "45041940873",
    "9247944613",
    "10978192153",
    "48349996293",
    "38488858163",
    "59689380213",
    "32749610699",
    "65743705893",
    "96071625593",
    "10692829500",
    "78698629983",
    "53812941083",
    "32922945609",
    "68098867423",
    "30129993850",
    "22890027377",
    "84716331073",
    "15944553019",
    "61469031173",
    "68121041563",
    "60253018253",
    "7581146129",
    "18488614658",
    "69483190323",
    "102349992661",
    "77626698623",
    "60399224583",
    "4852548719",
    "17226942344",
    "17678212275",
    "104322433771",
    "45556779693",
    "1329450463",
    "14834044496",
    "3172656214",
    "7470200911",
    "12162076738",
    "27520666527",
    "80601749213",
    "933443685",
    "62994082323",
    "35345044443",
    "50132285593",
    "59409726243",
    "17848682270",
    "29423352747",
    "15181574294",
    "8465530788",
    "18677495634",
    "68450088883",
    "33330202591",
    "96988408463",
    "50440145633",
    "51046842993",
    "34302056277",
    "93322042303",
    "4863565299",
    "51028243703",
    "18722653542",
    "26198260029",
    "8115529812",
    "30187429102",
    "70531245713",
    "36732992543",
    "18461172901",
    "86612512073",
}

full_analysis: dict[str, dict[str, int]] = {}

async def get_eventbrite_events() -> None:
    client = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)

    organizer_ids_copy = list(_EVENTBRITE_ORGANIZER_IDS)
    random.shuffle(organizer_ids_copy)

    for organizer_id in organizer_ids_copy:
        await asyncio.sleep(2)

        analysis = {
            "total_count": 0,
        }

        full_analysis[organizer_id] = analysis

        paginator = client.list_events_for_organizer(
            organizer_id=organizer_id,
            query=ListEventsQuery(
                order_by=OrderBy.START_ASC,
                status=EventStatus.LIVE,
                only_public=True,
                expand=Expansion.all(),
            )
        )

        pagenum = 0
        try:
            async for batch in paginator:
                pagenum += 1
                LOGGER.info(f"organizer {organizer_id}; pagenum {pagenum}")

                evnum = 0
                for event in batch:
                    analysis["total_count"] += 1
                    evnum += 1

                    # FIXME: This will ignore events that may have previously been added into the database, if their settings were changed to become excluded.

                    if (eventbrite_event_id := event.get("id")) is None:
                        analysis.setdefault("no_id", 0)
                        analysis["no_id"] += 1
                        LOGGER.warning("No eventbrite event id; skipping")
                        continue

                    pfx = f"[{organizer_id}; {evnum}/{len(batch)}; {eventbrite_event_id}]"
                    logmeta: JsonObject = { "eventbrite_organizer_id": organizer_id, "eventbrite_event_id": eventbrite_event_id }

                    LOGGER.info(f"{pfx} processing event", logmeta)

                    if event.get("status") != EventStatus.LIVE:
                        analysis.setdefault("invalid_status", 0)
                        analysis["invalid_status"] += 1
                        LOGGER.warning(f"{pfx} Status is not LIVE; skipping", logmeta)
                        continue

                    if event.get("online_event") is True:
                        analysis.setdefault("online_event", 0)
                        analysis["online_event"] += 1
                        LOGGER.info(f"{pfx} online_event=True; skipping", logmeta)
                        continue

                    if event.get("is_locked") is True:
                        analysis.setdefault("is_locked", 0)
                        analysis["is_locked"] += 1
                        LOGGER.info(f"{pfx} is_locked=True; skipping", logmeta)
                        continue

                    if event.get("show_pick_a_seat") is True:
                        analysis.setdefault("show_pick_a_seat", 0)
                        analysis["show_pick_a_seat"] += 1
                        LOGGER.info(
                            f"{pfx} show_pick_a_seat=True skipping", logmeta
                        )
                        continue

                    if event.get("is_sold_out") is True:
                        analysis.setdefault("is_sold_out", 0)
                        analysis["is_sold_out"] += 1
                        LOGGER.info(f"{pfx} is_sold_out=True; skipping", logmeta)
                        continue

                    if not (event_name := event.get("name")):
                        analysis.setdefault("no_name", 0)
                        analysis["no_name"] += 1
                        LOGGER.warning(
                            f"{pfx} No eventbrite event name; skipping", logmeta
                        )
                        continue

                    if (venue := event.get("venue")) is None:
                        analysis.setdefault("no_venue", 0)
                        analysis["no_venue"] += 1
                        LOGGER.warning(
                            f"{pfx} No eventbrite event venue; skipping", logmeta
                        )
                        continue

                    if (lat := venue.get("latitude")) is None:
                        analysis.setdefault("no_lat", 0)
                        analysis["no_lat"] += 1
                        LOGGER.warning(
                            f"{pfx} No venue latitude; skipping", logmeta
                        )
                        continue

                    if (lon := venue.get("longitude")) is None:
                        analysis.setdefault("no_lon", 0)
                        analysis["no_lon"] += 1
                        LOGGER.warning(
                            f"{pfx} No venue longitude; skipping", logmeta
                        )
                        continue

                    if (ticket_availability := event.get("ticket_availability")) is None:
                        analysis.setdefault("no_ticket_availability", 0)
                        analysis["no_ticket_availability"] += 1
                        LOGGER.warning(
                            f"{pfx} No eventbrite ticket_availability; skipping",
                            logmeta,
                        )
                        continue

                    if event.get("category_id") is None:
                        analysis.setdefault("no_category_id", 0)
                        analysis["no_category_id"] += 1
                        LOGGER.info(f"{pfx} category_id=None; skipping", logmeta)
                        continue

                    if (eb_subcategory_id := event.get("subcategory_id")) is None:
                        analysis.setdefault("no_subcategory_id", 0)
                        analysis["no_subcategory_id"] += 1
                        LOGGER.info(
                            f"{pfx} subcategory_id=None; skipping", logmeta
                        )
                        continue

                    if not (
                        vivial_category := ActivityCategoryOrm.get_by_eventbrite_subcategory_id(
                            eventbrite_subcategory_id=eb_subcategory_id
                        )
                    ):
                        analysis.setdefault("no_category_mapping", 0)
                        analysis["no_category_mapping"] += 1
                        logmeta["eventbrite_subcategory_id"] = eb_subcategory_id
                        LOGGER.warning(
                            f"{pfx} No mapped vivial category; skipping", logmeta
                        )
                        continue

                    if (eb_format_id := event.get("format_id")) is None:
                        analysis.setdefault("no_format_id", 0)
                        analysis["no_format_id"] += 1
                        LOGGER.info(f"{pfx} format_id=None; skipping", logmeta)
                        continue

                    if not (vivial_format := ActivityFormatOrm.get_by_eventbrite_id(eventbrite_format_id=eb_format_id)):
                        analysis.setdefault("no_format_mapping", 0)
                        analysis["no_format_mapping"] += 1
                        logmeta["eventbrite_format_id"] = eb_format_id
                        LOGGER.warning(
                            f"{pfx} No mapped vivial format; skipping", logmeta
                        )
                        continue

                    if event_start := event.get("start"):
                        start_time_utc = datetime.fromisoformat(event_start["utc"])
                        start_timezone = ZoneInfo(event_start["timezone"])
                    else:
                        LOGGER.warning(f"{pfx} No start time; skipping", logmeta)
                        continue

                    if event_end := event.get("end"):
                        end_time_utc = datetime.fromisoformat(event_end["utc"])
                        end_timezone = ZoneInfo(event_end["timezone"])
                    else:
                        end_timezone = None
                        end_time_utc = None

                    if minimum_ticket_price := ticket_availability.get("minimum_ticket_price"):
                        min_cost_cents = minimum_ticket_price["value"]
                    else:
                        min_cost_cents = 0

                    if maximum_ticket_price := ticket_availability.get("maximum_ticket_price"):
                        max_cost_cents = maximum_ticket_price["value"]
                    else:
                        max_cost_cents = 0

                    # These should never be different, but we need to choose one.
                    timezone = start_timezone or end_timezone or LOS_ANGELES_TIMEZONE

                    async with eave.core.database.async_session.begin() as db_session:
                        query = EventbriteEventOrm.select(
                            eventbrite_event_id=eventbrite_event_id,
                        ).limit(1)

                        target = (await db_session.scalars(query)).one_or_none()
                        if not target:
                            LOGGER.info(
                                f"{pfx} new event - adding to database", logmeta
                            )
                            target = EventbriteEventOrm(
                                db_session,
                                eventbrite_event_id=eventbrite_event_id,
                                eventbrite_organizer_id=event.get("organizer_id", organizer_id),
                                title=event_name["text"],
                                start_time=start_time_utc,
                                end_time=end_time_utc,
                                timezone=timezone,
                                min_cost_cents=min_cost_cents,
                                max_cost_cents=max_cost_cents,
                                lat=float(lat),
                                lon=float(lon),
                                vivial_activity_category_id=vivial_category.id,
                                vivial_activity_format_id=vivial_format.id,
                            )
                        else:
                            LOGGER.info(
                                f"{pfx} existing event - updating database", logmeta
                            )

                        target.update(
                            title=event_name["text"],
                            start_time=start_time_utc,
                            end_time=end_time_utc,
                            timezone=timezone,
                            min_cost_cents=min_cost_cents,
                            max_cost_cents=max_cost_cents,
                            lat=float(lat),
                            lon=float(lon),
                            vivial_activity_category_id=vivial_category.id,
                            vivial_activity_format_id=vivial_format.id,
                        )
        except ClientResponseError as e:
            LOGGER.exception(e)
            await asyncio.sleep(10)

        except Exception as e:
            LOGGER.exception(e)


if __name__ == "__main__":
    try:
        asyncio.run(get_eventbrite_events())
    except KeyboardInterrupt:
        pprint(full_analysis)
        raise
