# # isort: off

# import sys

# sys.path.append(".")

# from eave.core.lib.api_clients import GOOGLE_MAPS_API_CLIENT
# from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

# load_standard_dotenv_files()

# # isort: on

# # ruff: noqa: E402

# import asyncio
# import csv
# import os
# import re
# from pprint import pprint

# import googlemaps.geocoding

# from eave.core.orm.activity_category import ActivityCategoryOrm
# from eave.core.shared.geo import GeoPoint

# header = "[Title, Description, Address, Images, Category, Subcategory, Format, Availability (Days & Hours), Duration (Minutes), Ticket Type A, Ticket Type A Cost, Ticket Type B, Ticket Type B Cost, Taxes, Service Fees, Bookable, Book URL]"


# async def import_evergreen_activities() -> None:
#     with open(os.path.dirname(os.path.abspath(__file__)) + "/evergreen.csv") as f:
#         rdr = csv.reader(f)
#         i = 0
#         for row in rdr:
#             i += 1

#             if i == 1:
#                 continue

#             (
#                 title,
#                 description,
#                 address,
#                 images,
#                 category,
#                 subcategory,
#                 fmt,
#                 availability,
#                 duration,
#                 ticket_type_a,
#                 ticket_type_a_cost,
#                 ticket_type_b,
#                 ticket_type_b_cost,
#                 taxes,
#                 fees,
#                 bookable,
#                 book_url,
#             ) = row

#             activity_category = next((a for a in ActivityCategoryOrm.all() if a.name == subcategory), None)
#             if not activity_category:
#                 raise Exception(f"no matching category for {subcategory}")

#             images = images.split()
#             bookable = bookable == "Yes"
#             duration = int(duration)
#             fmt = None if not fmt else fmt
#             book_url = None if book_url == "N/A" else book_url
#             taxes = None if taxes == "N/A" else int(taxes)
#             fees = None if fees == "N/A" else int(fees)

#             # address = address.split(", ")
#             # address = [a.strip() for a in address]

#             # if m := re.match(r"(CA)\s(\d{5})", address[-1]):
#             #     state, zipcode = m.groups()
#             #     address[-1] = state
#             #     address.append(zipcode)

#             # print(address)

#             geocode_result = googlemaps.geocoding.geocode(client=GOOGLE_MAPS_API_CLIENT, address=address)

#             coordinates = GeoPoint(
#                 lat=geocode_result["geometry"]["location"]["lat"],
#                 lon=geocode_result["geometry"]["location"]["lng"],
#             )
#             place_id = geocode_result["place_id"]
#             pprint(geocode_result)

#             ticket_type_a = None if ticket_type_a == "N/A" else ticket_type_a
#             ticket_type_b = None if ticket_type_b == "N/A" else ticket_type_b

#             if ticket_type_a_cost == "N/A":
#                 ticket_type_a_cost = None
#             else:
#                 ticket_type_a_cost = re.sub("^\\$", "", ticket_type_a_cost)
#                 ticket_type_a_cost = int(ticket_type_a_cost)

#             if ticket_type_b_cost == "N/A":
#                 ticket_type_b_cost = None
#             else:
#                 ticket_type_b_cost = re.sub(r"^\$", "", ticket_type_b_cost)
#                 ticket_type_b_cost = int(ticket_type_b_cost)

#             availability = availability.split("\n")
#             availability = [d.split(": ") for d in availability]
#             availability_schedule = [[], [], [], [], [], [], []]

#             for day in availability:
#                 hours_text = day[1].strip()

#                 openclose = []
#                 if hours_text == "CLOSED":
#                     pass
#                 else:
#                     hours = hours_text.split("-")

#                     for hour in hours:
#                         if m := re.match(r"(\d+)(:\d+)?(AM|PM)$", hour):
#                             hr, mn, ap = m.groups()
#                             if ap == "AM":
#                                 if hr == "12":
#                                     hr = 0
#                                 else:
#                                     hr = int(hr)
#                             elif ap == "PM":
#                                 if hr == "12":
#                                     hr = 12
#                                 else:
#                                     hr = int(hr) + 12
#                             else:
#                                 raise Exception(f"invalid ampm: {ap}")

#                             minutes = hr * 60
#                             if mn:
#                                 minutes += int(re.sub(r"^:", "", mn))

#                             # print(minutes)
#                             openclose.append(minutes)
#                         else:
#                             raise Exception(f"doesnt match re: {hour}")

#                 match day[0].strip():
#                     case "Mon":
#                         availability_schedule[0] = openclose
#                     case "Tues":
#                         availability_schedule[1] = openclose
#                     case "Weds":
#                         availability_schedule[2] = openclose
#                     case "Thurs":
#                         availability_schedule[3] = openclose
#                     case "Fri":
#                         availability_schedule[4] = openclose
#                     case "Sat":
#                         availability_schedule[5] = openclose
#                     case "Sun":
#                         availability_schedule[6] = openclose
#                     case _:
#                         raise Exception(f"invalid day: {day[0]}")

#             # pprint({
#             #     "title": title,
#             #     "description": description,
#             #     "address": address,
#             #     "images": images,
#             #     "activity_category": activity_category,
#             #     "availability": availability_schedule,
#             #     "duration": duration,
#             #     "ticket_type_a": ticket_type_a,
#             #     "ticket_type_a_cost": ticket_type_a_cost,
#             #     "ticket_type_b": ticket_type_b,
#             #     "ticket_type_b_cost": ticket_type_b_cost,
#             #     "taxes": taxes,
#             #     "fees": fees,
#             #     "bookable": bookable,
#             #     "booking_url": book_url,
#             # })


# if __name__ == "__main__":
#     asyncio.run(import_evergreen_activities())
