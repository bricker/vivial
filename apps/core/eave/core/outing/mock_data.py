# TODO: Delete this file.

from models import OutingConstraints, EventbriteCategory, UserPreferences
from datetime import datetime

MockOutingConstraints = OutingConstraints(
    id = "UUID",
    visitor_id = "UUID",
    start_time = datetime.fromisoformat("2024-10-20T01:00:00.000Z"),
    search_area_ids = [],
    budget = 3,
    headcount = 2,
)

# 103: Music, 3008: Hip-Hop
mock_category_1 = EventbriteCategory(id="103", subcategory_ids=["3008", "3012"])
mock_category_2 = EventbriteCategory(id="105", subcategory_ids=["5001"])
mock_category_3 = EventbriteCategory(id="103", subcategory_ids=["3008", "3013"])
mock_category_4 = EventbriteCategory(id="104", subcategory_ids=["4007"])

MockUserPreferences = UserPreferences(
  open_to_bars = True,
  requires_wheelchair_accessibility = False,
  google_food_types = ["mexican_restaurant", "sushi_restaurant"],
  eventbrite_categories = [mock_category_1, mock_category_2],
)

MockPartnerPreferences = UserPreferences(
  open_to_bars = True,
  requires_wheelchair_accessibility = False,
  google_food_types = ["mexican_restaurant", "chinese_restaurant"],
  eventbrite_categories = [mock_category_3, mock_category_4],
)

class MockVivialAPI:
    response = {
    "pagination": {
        "object_count": 9,
        "page_number": 1,
        "page_size": 50,
        "page_count": 1,
        "has_more_items": False
    },
    "events": [
        {
            "name": {
                "text": "Hip Hop Bingo Katy, TX",
                "html": "Hip Hop Bingo Katy, TX"
            },
            "description": {
                "text": "Get ready to bust a move and test your luck with Hip Hop Bingo, an electrifying in-person event that combines the thrill of bingo with the b",
                "html": "Get ready to bust a move and test your luck with Hip Hop Bingo, an electrifying in-person event that combines the thrill of bingo with the b"
            },
            "url": "https://www.eventbrite.com/e/hip-hop-bingo-katy-tx-tickets-979933606797",
            "start": {
                "timezone": "America/Chicago",
                "local": "2024-10-19T20:00:00",
                "utc": "2024-10-20T01:00:00Z"
            },
            "end": {
                "timezone": "America/Chicago",
                "local": "2024-10-19T23:00:00",
                "utc": "2024-10-20T04:00:00Z"
            },
            "organization_id": "2000672364063",
            "created": "2024-08-07T08:46:29Z",
            "changed": "2024-10-17T22:35:04Z",
            "published": "2024-08-07T08:50:06Z",
            "capacity": None,
            "capacity_is_custom": None,
            "status": "live",
            "currency": "USD",
            "listed": True,
            "shareable": True,
            "online_event": False,
            "tx_time_limit": 1200,
            "hide_start_date": False,
            "hide_end_date": False,
            "locale": "en_US",
            "is_locked": False,
            "privacy_setting": "unlocked",
            "is_series": True,
            "is_series_parent": False,
            "inventory_type": "limited",
            "is_reserved_seating": False,
            "show_pick_a_seat": False,
            "show_seatmap_thumbnail": False,
            "show_colors_in_seatmap_thumbnail": False,
            "source": "auto_create",
            "is_free": False,
            "version": None,
            "summary": "Get ready to bust a move and test your luck with Hip Hop Bingo, an electrifying in-person event that combines the thrill of bingo with the b",
            "facebook_event_id": None,
            "logo_id": "822135209",
            "organizer_id": "78698629983",
            "venue_id": "226512429",
            "category_id": "103",
            "subcategory_id": "3008",
            "format_id": "14",
            "id": "979933606797",
            "resource_uri": "https://www.eventbriteapi.com/v3/events/979933606797/",
            "is_externally_ticketed": False,
            "series_id": "979931169507",
            "logo": {
                "crop_mask": {
                    "top_left": {
                        "x": 228,
                        "y": 0
                    },
                    "width": 852,
                    "height": 426
                },
                "original": {
                    "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822135209%2F2000672303643%2F1%2Foriginal.20240807-083854?auto=format%2Ccompress&q=75&sharp=10&s=6bc5c730eae89c6e924da6984cc29a87",
                    "width": 1080,
                    "height": 1080
                },
                "id": "822135209",
                "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822135209%2F2000672303643%2F1%2Foriginal.20240807-083854?h=200&w=450&auto=format%2Ccompress&q=75&sharp=10&rect=228%2C0%2C852%2C426&s=081f812d25f544dd284859970f3c8de1",
                "aspect_ratio": "2",
                "edge_color": "#000000",
                "edge_color_set": True
            },
            "ticket_availability": {
                "has_available_tickets": True,
                "minimum_ticket_price": {
                    "currency": "USD",
                    "major_value": "35.00",
                    "value": 3500,
                    "display": "35.00 USD"
                },
                "maximum_ticket_price": {
                    "currency": "USD",
                    "major_value": "160.00",
                    "value": 16000,
                    "display": "160.00 USD"
                },
                "is_sold_out": False,
                "start_sales_date": None,
                "waitlist_available": False
            }
        },
        {
            "name": {
                "text": "Hip Hop Bingo KILLEEN, TX",
                "html": "Hip Hop Bingo KILLEEN, TX"
            },
            "description": {
                "text": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop & RnB beats meet the excitement of a classic game with a spin!",
                "html": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop &amp; RnB beats meet the excitement of a classic game with a spin!"
            },
            "url": "https://www.eventbrite.com/e/hip-hop-bingo-killeen-tx-tickets-1044290750747",
            "start": {
                "timezone": "America/Chicago",
                "local": "2024-10-25T20:00:00",
                "utc": "2024-10-26T01:00:00Z"
            },
            "end": {
                "timezone": "America/Chicago",
                "local": "2024-10-25T23:00:00",
                "utc": "2024-10-26T04:00:00Z"
            },
            "organization_id": "2000672364063",
            "created": "2024-10-10T18:33:04Z",
            "changed": "2024-10-17T18:11:39Z",
            "published": "2024-10-10T18:34:56Z",
            "capacity": None,
            "capacity_is_custom": None,
            "status": "live",
            "currency": "USD",
            "listed": True,
            "shareable": True,
            "online_event": False,
            "tx_time_limit": 1200,
            "hide_start_date": False,
            "hide_end_date": False,
            "locale": "en_US",
            "is_locked": False,
            "privacy_setting": "unlocked",
            "is_series": True,
            "is_series_parent": False,
            "inventory_type": "limited",
            "is_reserved_seating": False,
            "show_pick_a_seat": False,
            "show_seatmap_thumbnail": False,
            "show_colors_in_seatmap_thumbnail": False,
            "source": "auto_create",
            "is_free": False,
            "version": None,
            "summary": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop & RnB beats meet the excitement of a classic game with a spin!",
            "facebook_event_id": None,
            "logo_id": "745178669",
            "organizer_id": "78698629983",
            "venue_id": "236854049",
            "category_id": "105",
            "subcategory_id": "5004",
            "format_id": "11",
            "id": "1044290750747",
            "resource_uri": "https://www.eventbriteapi.com/v3/events/1044290750747/",
            "is_externally_ticketed": False,
            "series_id": "1044288875137",
            "logo": {
                "crop_mask": {
                    "top_left": {
                        "x": 123,
                        "y": 20
                    },
                    "width": 790,
                    "height": 395
                },
                "original": {
                    "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F745178669%2F2000672303643%2F1%2Foriginal.20240416-202447?auto=format%2Ccompress&q=75&sharp=10&s=550c19a942f2656adbdd3a92e6ab7dc1",
                    "width": 1080,
                    "height": 1080
                },
                "id": "745178669",
                "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F745178669%2F2000672303643%2F1%2Foriginal.20240416-202447?h=200&w=450&auto=format%2Ccompress&q=75&sharp=10&rect=123%2C20%2C790%2C395&s=720cf74fdf532045da33402b329cce05",
                "aspect_ratio": "2",
                "edge_color": "#000000",
                "edge_color_set": True
            },
            "ticket_availability": {
                "has_available_tickets": True,
                "minimum_ticket_price": {
                    "currency": "USD",
                    "major_value": "35.00",
                    "value": 3500,
                    "display": "35.00 USD"
                },
                "maximum_ticket_price": {
                    "currency": "USD",
                    "major_value": "35.00",
                    "value": 3500,
                    "display": "35.00 USD"
                },
                "is_sold_out": False,
                "start_sales_date": None,
                "waitlist_available": False
            }
        },
        {
            "name": {
                "text": "Hip Hop Bingo Los Angeles, CA",
                "html": "Hip Hop Bingo Los Angeles, CA"
            },
            "description": {
                "text": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop & RnB beats meet the excitement of a classic game with a spin!",
                "html": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop &amp; RnB beats meet the excitement of a classic game with a spin!"
            },
            "url": "https://www.eventbrite.com/e/hip-hop-bingo-los-angeles-ca-tickets-979920567797",
            "start": {
                "timezone": "America/Los_Angeles",
                "local": "2024-11-02T18:30:00",
                "utc": "2024-11-03T01:30:00Z"
            },
            "end": {
                "timezone": "America/Los_Angeles",
                "local": "2024-11-02T21:30:00",
                "utc": "2024-11-03T04:30:00Z"
            },
            "organization_id": "2000672364063",
            "created": "2024-08-07T08:21:21Z",
            "changed": "2024-10-04T03:07:29Z",
            "published": "2024-08-07T08:34:43Z",
            "capacity": None,
            "capacity_is_custom": None,
            "status": "live",
            "currency": "USD",
            "listed": True,
            "shareable": True,
            "online_event": False,
            "tx_time_limit": 1200,
            "hide_start_date": False,
            "hide_end_date": False,
            "locale": "en_US",
            "is_locked": False,
            "privacy_setting": "unlocked",
            "is_series": True,
            "is_series_parent": False,
            "inventory_type": "limited",
            "is_reserved_seating": False,
            "show_pick_a_seat": False,
            "show_seatmap_thumbnail": False,
            "show_colors_in_seatmap_thumbnail": False,
            "source": "auto_create",
            "is_free": False,
            "version": None,
            "summary": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop & RnB beats meet the excitement of a classic game with a spin!",
            "facebook_event_id": None,
            "logo_id": "822126119",
            "organizer_id": "78698629983",
            "venue_id": "226510549",
            "category_id": "105",
            "subcategory_id": "5004",
            "format_id": "11",
            "id": "979920567797",
            "resource_uri": "https://www.eventbriteapi.com/v3/events/979920567797/",
            "is_externally_ticketed": False,
            "series_id": "979914780487",
            "logo": {
                "crop_mask": {
                    "top_left": {
                        "x": 202,
                        "y": 0
                    },
                    "width": 878,
                    "height": 439
                },
                "original": {
                    "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822126119%2F2000672303643%2F1%2Foriginal.20240807-081442?auto=format%2Ccompress&q=75&sharp=10&s=777a509d99a0aa530622ebaffc5022b5",
                    "width": 1080,
                    "height": 1080
                },
                "id": "822126119",
                "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822126119%2F2000672303643%2F1%2Foriginal.20240807-081442?h=200&w=450&auto=format%2Ccompress&q=75&sharp=10&rect=202%2C0%2C878%2C439&s=2185ecdb2853c49e9f9066941bd51c75",
                "aspect_ratio": "2",
                "edge_color": "#000000",
                "edge_color_set": True
            },
            "ticket_availability": {
                "has_available_tickets": True,
                "minimum_ticket_price": {
                    "currency": "USD",
                    "major_value": "33.85",
                    "value": 3385,
                    "display": "33.85 USD"
                },
                "maximum_ticket_price": {
                    "currency": "USD",
                    "major_value": "33.85",
                    "value": 3385,
                    "display": "33.85 USD"
                },
                "is_sold_out": False,
                "start_sales_date": None,
                "waitlist_available": False
            }
        },
        {
            "name": {
                "text": "Hip Hop Bingo KILLEEN, TX",
                "html": "Hip Hop Bingo KILLEEN, TX"
            },
            "description": {
                "text": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop & RnB beats meet the excitement of a classic game with a spin!",
                "html": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop &amp; RnB beats meet the excitement of a classic game with a spin!"
            },
            "url": "https://www.eventbrite.com/e/hip-hop-bingo-killeen-tx-tickets-1044291161977",
            "start": {
                "timezone": "America/Chicago",
                "local": "2024-11-28T20:00:00",
                "utc": "2024-11-29T02:00:00Z"
            },
            "end": {
                "timezone": "America/Chicago",
                "local": "2024-11-28T23:00:00",
                "utc": "2024-11-29T05:00:00Z"
            },
            "organization_id": "2000672364063",
            "created": "2024-10-10T18:33:41Z",
            "changed": "2024-10-10T18:34:56Z",
            "published": "2024-10-10T18:34:56Z",
            "capacity": None,
            "capacity_is_custom": None,
            "status": "live",
            "currency": "USD",
            "listed": True,
            "shareable": True,
            "online_event": False,
            "tx_time_limit": 1200,
            "hide_start_date": False,
            "hide_end_date": False,
            "locale": "en_US",
            "is_locked": False,
            "privacy_setting": "unlocked",
            "is_series": True,
            "is_series_parent": False,
            "inventory_type": "limited",
            "is_reserved_seating": False,
            "show_pick_a_seat": False,
            "show_seatmap_thumbnail": False,
            "show_colors_in_seatmap_thumbnail": False,
            "source": "auto_create",
            "is_free": False,
            "version": None,
            "summary": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop & RnB beats meet the excitement of a classic game with a spin!",
            "facebook_event_id": None,
            "logo_id": "745178669",
            "organizer_id": "78698629983",
            "venue_id": "236854049",
            "category_id": "105",
            "subcategory_id": "5004",
            "format_id": "11",
            "id": "1044291161977",
            "resource_uri": "https://www.eventbriteapi.com/v3/events/1044291161977/",
            "is_externally_ticketed": False,
            "series_id": "1044288875137",
            "logo": {
                "crop_mask": {
                    "top_left": {
                        "x": 123,
                        "y": 20
                    },
                    "width": 790,
                    "height": 395
                },
                "original": {
                    "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F745178669%2F2000672303643%2F1%2Foriginal.20240416-202447?auto=format%2Ccompress&q=75&sharp=10&s=550c19a942f2656adbdd3a92e6ab7dc1",
                    "width": 1080,
                    "height": 1080
                },
                "id": "745178669",
                "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F745178669%2F2000672303643%2F1%2Foriginal.20240416-202447?h=200&w=450&auto=format%2Ccompress&q=75&sharp=10&rect=123%2C20%2C790%2C395&s=720cf74fdf532045da33402b329cce05",
                "aspect_ratio": "2",
                "edge_color": "#000000",
                "edge_color_set": True
            },
            "ticket_availability": {
                "has_available_tickets": True,
                "minimum_ticket_price": {
                    "currency": "USD",
                    "major_value": "35.00",
                    "value": 3500,
                    "display": "35.00 USD"
                },
                "maximum_ticket_price": {
                    "currency": "USD",
                    "major_value": "35.00",
                    "value": 3500,
                    "display": "35.00 USD"
                },
                "is_sold_out": False,
                "start_sales_date": None,
                "waitlist_available": False
            }
        },
        {
            "name": {
                "text": "Hip Hop Bingo Katy, TX",
                "html": "Hip Hop Bingo Katy, TX"
            },
            "description": {
                "text": "Get ready to bust a move and test your luck with Hip Hop Bingo, an electrifying in-person event that combines the thrill of bingo with the b",
                "html": "Get ready to bust a move and test your luck with Hip Hop Bingo, an electrifying in-person event that combines the thrill of bingo with the b"
            },
            "url": "https://www.eventbrite.com/e/hip-hop-bingo-katy-tx-tickets-979933917727",
            "start": {
                "timezone": "America/Chicago",
                "local": "2024-11-30T20:00:00",
                "utc": "2024-12-01T02:00:00Z"
            },
            "end": {
                "timezone": "America/Chicago",
                "local": "2024-11-30T23:00:00",
                "utc": "2024-12-01T05:00:00Z"
            },
            "organization_id": "2000672364063",
            "created": "2024-08-07T08:47:59Z",
            "changed": "2024-10-10T18:23:56Z",
            "published": "2024-08-07T08:50:06Z",
            "capacity": None,
            "capacity_is_custom": None,
            "status": "live",
            "currency": "USD",
            "listed": True,
            "shareable": True,
            "online_event": False,
            "tx_time_limit": 1200,
            "hide_start_date": False,
            "hide_end_date": False,
            "locale": "en_US",
            "is_locked": False,
            "privacy_setting": "unlocked",
            "is_series": True,
            "is_series_parent": False,
            "inventory_type": "limited",
            "is_reserved_seating": False,
            "show_pick_a_seat": False,
            "show_seatmap_thumbnail": False,
            "show_colors_in_seatmap_thumbnail": False,
            "source": "auto_create",
            "is_free": False,
            "version": None,
            "summary": "Get ready to bust a move and test your luck with Hip Hop Bingo, an electrifying in-person event that combines the thrill of bingo with the b",
            "facebook_event_id": None,
            "logo_id": "822135209",
            "organizer_id": "78698629983",
            "venue_id": "226512429",
            "category_id": "103",
            "subcategory_id": "3008",
            "format_id": "14",
            "id": "979933917727",
            "resource_uri": "https://www.eventbriteapi.com/v3/events/979933917727/",
            "is_externally_ticketed": False,
            "series_id": "979931169507",
            "logo": {
                "crop_mask": {
                    "top_left": {
                        "x": 228,
                        "y": 0
                    },
                    "width": 852,
                    "height": 426
                },
                "original": {
                    "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822135209%2F2000672303643%2F1%2Foriginal.20240807-083854?auto=format%2Ccompress&q=75&sharp=10&s=6bc5c730eae89c6e924da6984cc29a87",
                    "width": 1080,
                    "height": 1080
                },
                "id": "822135209",
                "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822135209%2F2000672303643%2F1%2Foriginal.20240807-083854?h=200&w=450&auto=format%2Ccompress&q=75&sharp=10&rect=228%2C0%2C852%2C426&s=081f812d25f544dd284859970f3c8de1",
                "aspect_ratio": "2",
                "edge_color": "#000000",
                "edge_color_set": True
            },
            "ticket_availability": {
                "has_available_tickets": True,
                "minimum_ticket_price": {
                    "currency": "USD",
                    "major_value": "35.00",
                    "value": 3500,
                    "display": "35.00 USD"
                },
                "maximum_ticket_price": {
                    "currency": "USD",
                    "major_value": "160.00",
                    "value": 16000,
                    "display": "160.00 USD"
                },
                "is_sold_out": False,
                "start_sales_date": None,
                "waitlist_available": False
            }
        },
        {
            "name": {
                "text": "Hip Hop Bingo Los Angeles, CA",
                "html": "Hip Hop Bingo Los Angeles, CA"
            },
            "description": {
                "text": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop & RnB beats meet the excitement of a classic game with a spin!",
                "html": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop &amp; RnB beats meet the excitement of a classic game with a spin!"
            },
            "url": "https://www.eventbrite.com/e/hip-hop-bingo-los-angeles-ca-tickets-979920577827",
            "start": {
                "timezone": "America/Los_Angeles",
                "local": "2024-12-07T18:30:00",
                "utc": "2024-12-08T02:30:00Z"
            },
            "end": {
                "timezone": "America/Los_Angeles",
                "local": "2024-12-07T21:30:00",
                "utc": "2024-12-08T05:30:00Z"
            },
            "organization_id": "2000672364063",
            "created": "2024-08-07T08:21:21Z",
            "changed": "2024-08-07T08:34:42Z",
            "published": "2024-08-07T08:34:43Z",
            "capacity": None,
            "capacity_is_custom": None,
            "status": "live",
            "currency": "USD",
            "listed": True,
            "shareable": True,
            "online_event": False,
            "tx_time_limit": 1200,
            "hide_start_date": False,
            "hide_end_date": False,
            "locale": "en_US",
            "is_locked": False,
            "privacy_setting": "unlocked",
            "is_series": True,
            "is_series_parent": False,
            "inventory_type": "limited",
            "is_reserved_seating": False,
            "show_pick_a_seat": False,
            "show_seatmap_thumbnail": False,
            "show_colors_in_seatmap_thumbnail": False,
            "source": "auto_create",
            "is_free": False,
            "version": None,
            "summary": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop & RnB beats meet the excitement of a classic game with a spin!",
            "facebook_event_id": None,
            "logo_id": "822126119",
            "organizer_id": "78698629983",
            "venue_id": "226510549",
            "category_id": "105",
            "subcategory_id": "5004",
            "format_id": "11",
            "id": "979920577827",
            "resource_uri": "https://www.eventbriteapi.com/v3/events/979920577827/",
            "is_externally_ticketed": False,
            "series_id": "979914780487",
            "logo": {
                "crop_mask": {
                    "top_left": {
                        "x": 202,
                        "y": 0
                    },
                    "width": 878,
                    "height": 439
                },
                "original": {
                    "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822126119%2F2000672303643%2F1%2Foriginal.20240807-081442?auto=format%2Ccompress&q=75&sharp=10&s=777a509d99a0aa530622ebaffc5022b5",
                    "width": 1080,
                    "height": 1080
                },
                "id": "822126119",
                "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822126119%2F2000672303643%2F1%2Foriginal.20240807-081442?h=200&w=450&auto=format%2Ccompress&q=75&sharp=10&rect=202%2C0%2C878%2C439&s=2185ecdb2853c49e9f9066941bd51c75",
                "aspect_ratio": "2",
                "edge_color": "#000000",
                "edge_color_set": True
            },
            "ticket_availability": {
                "has_available_tickets": True,
                "minimum_ticket_price": {
                    "currency": "USD",
                    "major_value": "33.85",
                    "value": 3385,
                    "display": "33.85 USD"
                },
                "maximum_ticket_price": {
                    "currency": "USD",
                    "major_value": "33.85",
                    "value": 3385,
                    "display": "33.85 USD"
                },
                "is_sold_out": False,
                "start_sales_date": None,
                "waitlist_available": False
            }
        },
        {
            "name": {
                "text": "Hip Hop Bingo Katy, TX",
                "html": "Hip Hop Bingo Katy, TX"
            },
            "description": {
                "text": "Get ready to bust a move and test your luck with Hip Hop Bingo, an electrifying in-person event that combines the thrill of bingo with the b",
                "html": "Get ready to bust a move and test your luck with Hip Hop Bingo, an electrifying in-person event that combines the thrill of bingo with the b"
            },
            "url": "https://www.eventbrite.com/e/hip-hop-bingo-katy-tx-tickets-1044284050707",
            "start": {
                "timezone": "America/Chicago",
                "local": "2024-12-21T20:00:00",
                "utc": "2024-12-22T02:00:00Z"
            },
            "end": {
                "timezone": "America/Chicago",
                "local": "2024-12-21T23:00:00",
                "utc": "2024-12-22T05:00:00Z"
            },
            "organization_id": "2000672364063",
            "created": "2024-10-10T18:20:44Z",
            "changed": "2024-10-10T18:22:04Z",
            "published": "2024-08-07T08:50:06Z",
            "capacity": None,
            "capacity_is_custom": None,
            "status": "live",
            "currency": "USD",
            "listed": True,
            "shareable": True,
            "online_event": False,
            "tx_time_limit": 1200,
            "hide_start_date": False,
            "hide_end_date": False,
            "locale": "en_US",
            "is_locked": False,
            "privacy_setting": "unlocked",
            "is_series": True,
            "is_series_parent": False,
            "inventory_type": "limited",
            "is_reserved_seating": False,
            "show_pick_a_seat": False,
            "show_seatmap_thumbnail": False,
            "show_colors_in_seatmap_thumbnail": False,
            "source": "auto_create",
            "is_free": False,
            "version": None,
            "summary": "Get ready to bust a move and test your luck with Hip Hop Bingo, an electrifying in-person event that combines the thrill of bingo with the b",
            "facebook_event_id": None,
            "logo_id": "822135209",
            "organizer_id": "78698629983",
            "venue_id": "226512429",
            "category_id": "103",
            "subcategory_id": "3008",
            "format_id": "14",
            "id": "1044284050707",
            "resource_uri": "https://www.eventbriteapi.com/v3/events/1044284050707/",
            "is_externally_ticketed": False,
            "series_id": "979931169507",
            "logo": {
                "crop_mask": {
                    "top_left": {
                        "x": 228,
                        "y": 0
                    },
                    "width": 852,
                    "height": 426
                },
                "original": {
                    "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822135209%2F2000672303643%2F1%2Foriginal.20240807-083854?auto=format%2Ccompress&q=75&sharp=10&s=6bc5c730eae89c6e924da6984cc29a87",
                    "width": 1080,
                    "height": 1080
                },
                "id": "822135209",
                "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822135209%2F2000672303643%2F1%2Foriginal.20240807-083854?h=200&w=450&auto=format%2Ccompress&q=75&sharp=10&rect=228%2C0%2C852%2C426&s=081f812d25f544dd284859970f3c8de1",
                "aspect_ratio": "2",
                "edge_color": "#000000",
                "edge_color_set": True
            },
            "ticket_availability": {
                "has_available_tickets": True,
                "minimum_ticket_price": {
                    "currency": "USD",
                    "major_value": "35.00",
                    "value": 3500,
                    "display": "35.00 USD"
                },
                "maximum_ticket_price": {
                    "currency": "USD",
                    "major_value": "160.00",
                    "value": 16000,
                    "display": "160.00 USD"
                },
                "is_sold_out": False,
                "start_sales_date": None,
                "waitlist_available": False
            }
        },
        {
            "name": {
                "text": "Hip Hop Bingo Los Angeles, CA",
                "html": "Hip Hop Bingo Los Angeles, CA"
            },
            "description": {
                "text": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop & RnB beats meet the excitement of a classic game with a spin!",
                "html": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop &amp; RnB beats meet the excitement of a classic game with a spin!"
            },
            "url": "https://www.eventbrite.com/e/hip-hop-bingo-los-angeles-ca-tickets-979920587857",
            "start": {
                "timezone": "America/Los_Angeles",
                "local": "2025-01-04T18:30:00",
                "utc": "2025-01-05T02:30:00Z"
            },
            "end": {
                "timezone": "America/Los_Angeles",
                "local": "2025-01-04T21:30:00",
                "utc": "2025-01-05T05:30:00Z"
            },
            "organization_id": "2000672364063",
            "created": "2024-08-07T08:21:21Z",
            "changed": "2024-08-07T08:34:42Z",
            "published": "2024-08-07T08:34:43Z",
            "capacity": None,
            "capacity_is_custom": None,
            "status": "live",
            "currency": "USD",
            "listed": True,
            "shareable": True,
            "online_event": False,
            "tx_time_limit": 1200,
            "hide_start_date": False,
            "hide_end_date": False,
            "locale": "en_US",
            "is_locked": False,
            "privacy_setting": "unlocked",
            "is_series": True,
            "is_series_parent": False,
            "inventory_type": "limited",
            "is_reserved_seating": False,
            "show_pick_a_seat": False,
            "show_seatmap_thumbnail": False,
            "show_colors_in_seatmap_thumbnail": False,
            "source": "auto_create",
            "is_free": False,
            "version": None,
            "summary": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop & RnB beats meet the excitement of a classic game with a spin!",
            "facebook_event_id": None,
            "logo_id": "822126119",
            "organizer_id": "78698629983",
            "venue_id": "226510549",
            "category_id": "105",
            "subcategory_id": "5004",
            "format_id": "11",
            "id": "979920587857",
            "resource_uri": "https://www.eventbriteapi.com/v3/events/979920587857/",
            "is_externally_ticketed": False,
            "series_id": "979914780487",
            "logo": {
                "crop_mask": {
                    "top_left": {
                        "x": 202,
                        "y": 0
                    },
                    "width": 878,
                    "height": 439
                },
                "original": {
                    "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822126119%2F2000672303643%2F1%2Foriginal.20240807-081442?auto=format%2Ccompress&q=75&sharp=10&s=777a509d99a0aa530622ebaffc5022b5",
                    "width": 1080,
                    "height": 1080
                },
                "id": "822126119",
                "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822126119%2F2000672303643%2F1%2Foriginal.20240807-081442?h=200&w=450&auto=format%2Ccompress&q=75&sharp=10&rect=202%2C0%2C878%2C439&s=2185ecdb2853c49e9f9066941bd51c75",
                "aspect_ratio": "2",
                "edge_color": "#000000",
                "edge_color_set": True
            },
            "ticket_availability": {
                "has_available_tickets": True,
                "minimum_ticket_price": {
                    "currency": "USD",
                    "major_value": "33.85",
                    "value": 3385,
                    "display": "33.85 USD"
                },
                "maximum_ticket_price": {
                    "currency": "USD",
                    "major_value": "33.85",
                    "value": 3385,
                    "display": "33.85 USD"
                },
                "is_sold_out": False,
                "start_sales_date": None,
                "waitlist_available": False
            }
        },
        {
            "name": {
                "text": "Hip Hop Bingo Los Angeles, CA",
                "html": "Hip Hop Bingo Los Angeles, CA"
            },
            "description": {
                "text": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop & RnB beats meet the excitement of a classic game with a spin!",
                "html": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop &amp; RnB beats meet the excitement of a classic game with a spin!"
            },
            "url": "https://www.eventbrite.com/e/hip-hop-bingo-los-angeles-ca-tickets-979920597887",
            "start": {
                "timezone": "America/Los_Angeles",
                "local": "2025-02-01T18:30:00",
                "utc": "2025-02-02T02:30:00Z"
            },
            "end": {
                "timezone": "America/Los_Angeles",
                "local": "2025-02-01T21:30:00",
                "utc": "2025-02-02T05:30:00Z"
            },
            "organization_id": "2000672364063",
            "created": "2024-08-07T08:21:21Z",
            "changed": "2024-08-07T08:34:42Z",
            "published": "2024-08-07T08:34:43Z",
            "capacity": None,
            "capacity_is_custom": None,
            "status": "live",
            "currency": "USD",
            "listed": True,
            "shareable": True,
            "online_event": False,
            "tx_time_limit": 1200,
            "hide_start_date": False,
            "hide_end_date": False,
            "locale": "en_US",
            "is_locked": False,
            "privacy_setting": "unlocked",
            "is_series": True,
            "is_series_parent": False,
            "inventory_type": "limited",
            "is_reserved_seating": False,
            "show_pick_a_seat": False,
            "show_seatmap_thumbnail": False,
            "show_colors_in_seatmap_thumbnail": False,
            "source": "auto_create",
            "is_free": False,
            "version": None,
            "summary": "Get ready to vibe at Hip Hop Bingo, where old-new school Hip Hop & RnB beats meet the excitement of a classic game with a spin!",
            "facebook_event_id": None,
            "logo_id": "822126119",
            "organizer_id": "78698629983",
            "venue_id": "226510549",
            "category_id": "105",
            "subcategory_id": "5004",
            "format_id": "11",
            "id": "979920597887",
            "resource_uri": "https://www.eventbriteapi.com/v3/events/979920597887/",
            "is_externally_ticketed": False,
            "series_id": "979914780487",
            "logo": {
                "crop_mask": {
                    "top_left": {
                        "x": 202,
                        "y": 0
                    },
                    "width": 878,
                    "height": 439
                },
                "original": {
                    "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822126119%2F2000672303643%2F1%2Foriginal.20240807-081442?auto=format%2Ccompress&q=75&sharp=10&s=777a509d99a0aa530622ebaffc5022b5",
                    "width": 1080,
                    "height": 1080
                },
                "id": "822126119",
                "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822126119%2F2000672303643%2F1%2Foriginal.20240807-081442?h=200&w=450&auto=format%2Ccompress&q=75&sharp=10&rect=202%2C0%2C878%2C439&s=2185ecdb2853c49e9f9066941bd51c75",
                "aspect_ratio": "2",
                "edge_color": "#000000",
                "edge_color_set": True
            },
            "ticket_availability": {
                "has_available_tickets": True,
                "minimum_ticket_price": {
                    "currency": "USD",
                    "major_value": "33.85",
                    "value": 3385,
                    "display": "33.85 USD"
                },
                "maximum_ticket_price": {
                    "currency": "USD",
                    "major_value": "33.85",
                    "value": 3385,
                    "display": "33.85 USD"
                },
                "is_sold_out": False,
                "start_sales_date": None,
                "waitlist_available": False
            }
        }
    ]
}

class MockEventbriteAPI:
    response = {
    "name": {
        "text": "Hip Hop Bingo Katy, TX",
        "html": "Hip Hop Bingo Katy, TX"
    },
    "description": {
        "text": "Get ready to bust a move and test your luck with Hip Hop Bingo, an electrifying in-person event that combines the thrill of bingo with the b",
        "html": "Get ready to bust a move and test your luck with Hip Hop Bingo, an electrifying in-person event that combines the thrill of bingo with the b"
    },
    "url": "https://www.eventbrite.com/e/hip-hop-bingo-katy-tx-tickets-979933606797",
    "start": {
        "timezone": "America/Chicago",
        "local": "2024-10-19T20:00:00",
        "utc": "2024-10-20T01:00:00Z"
    },
    "end": {
        "timezone": "America/Chicago",
        "local": "2024-10-19T23:00:00",
        "utc": "2024-10-20T04:00:00Z"
    },
    "organization_id": "2000672364063",
    "created": "2024-08-07T08:46:29Z",
    "changed": "2024-10-17T22:35:04Z",
    "published": "2024-08-07T08:50:06Z",
    "capacity": None,
    "capacity_is_custom": None,
    "status": "live",
    "currency": "USD",
    "listed": True,
    "shareable": True,
    "online_event": False,
    "tx_time_limit": 1200,
    "hide_start_date": False,
    "hide_end_date": False,
    "locale": "en_US",
    "is_locked": False,
    "privacy_setting": "unlocked",
    "is_series": True,
    "is_series_parent": False,
    "inventory_type": "limited",
    "is_reserved_seating": False,
    "show_pick_a_seat": False,
    "show_seatmap_thumbnail": False,
    "show_colors_in_seatmap_thumbnail": False,
    "source": "auto_create",
    "is_free": False,
    "version": None,
    "summary": "Get ready to bust a move and test your luck with Hip Hop Bingo, an electrifying in-person event that combines the thrill of bingo with the b",
    "facebook_event_id": None,
    "logo_id": "822135209",
    "organizer_id": "78698629983",
    "venue_id": "226512429",
    "category_id": "103",
    "subcategory_id": "3008",
    "format_id": "14",
    "id": "979933606797",
    "resource_uri": "https://www.eventbriteapi.com/v3/events/979933606797/",
    "is_externally_ticketed": False,
    "series_id": "979931169507",
    "logo": {
        "crop_mask": {
            "top_left": {
                "x": 228,
                "y": 0
            },
            "width": 852,
            "height": 426
        },
        "original": {
            "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822135209%2F2000672303643%2F1%2Foriginal.20240807-083854?auto=format%2Ccompress&q=75&sharp=10&s=6bc5c730eae89c6e924da6984cc29a87",
            "width": 1080,
            "height": 1080
        },
        "id": "822135209",
        "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F822135209%2F2000672303643%2F1%2Foriginal.20240807-083854?h=200&w=450&auto=format%2Ccompress&q=75&sharp=10&rect=228%2C0%2C852%2C426&s=081f812d25f544dd284859970f3c8de1",
        "aspect_ratio": "2",
        "edge_color": "#000000",
        "edge_color_set": True
    }
}

class MockGoogleAPI:
    request = {
        "includedPrimaryTypes": [
            "mexican_restaurant"
        ],
        "locationRestriction": {
            "circle": {
            "center": {
                "latitude": 34.046422,
                "longitude": -118.245325
            },
            "radius": 2719.791
            }
        }
    }
    response = {
  "places": [
    {
      "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U",
      "id": "ChIJ45QjyjTGwoARVNFElqulM0U",
      "types": [
        "mexican_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 222-5071",
      "internationalPhoneNumber": "+1 213-222-5071",
      "formattedAddress": "208 E 8th St, Los Angeles, CA 90014, USA",
      "addressComponents": [
        {
          "longText": "208",
          "shortText": "208",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "East 8th Street",
          "shortText": "E 8th St",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90014",
          "shortText": "90014",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "2104",
          "shortText": "2104",
          "types": [
            "postal_code_suffix"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632PRX+J4",
        "compoundCode": "2PRX+J4 Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.041615,
        "longitude": -118.2521844
      },
      "viewport": {
        "low": {
          "latitude": 34.040311669708508,
          "longitude": -118.25349393029147
        },
        "high": {
          "latitude": 34.043009630291508,
          "longitude": -118.25079596970849
        }
      },
      "rating": 4.5,
      "googleMapsUri": "https://maps.google.com/?cid=4986511368808354132",
      "websiteUri": "http://www.sonoratown.com/",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 1,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 11:00 AM – 9:00 PM",
          "Tuesday: 11:00 AM – 9:00 PM",
          "Wednesday: 11:00 AM – 9:00 PM",
          "Thursday: 11:00 AM – 9:00 PM",
          "Friday: 11:00 AM – 10:00 PM",
          "Saturday: 11:00 AM – 10:00 PM",
          "Sunday: 11:00 AM – 9:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e208 E 8th St\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90014-2104\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_INEXPENSIVE",
      "userRatingCount": 2911,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Sonoratown",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "reservable": False,
      "servesBreakfast": False,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": True,
      "servesWine": True,
      "servesBrunch": False,
      "servesVegetarianFood": False,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 11:00 AM – 9:00 PM",
          "Tuesday: 11:00 AM – 9:00 PM",
          "Wednesday: 11:00 AM – 9:00 PM",
          "Thursday: 11:00 AM – 9:00 PM",
          "Friday: 11:00 AM – 10:00 PM",
          "Saturday: 11:00 AM – 10:00 PM",
          "Sunday: 11:00 AM – 9:00 PM"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "208 E 8th St, Los Angeles",
      "editorialSummary": {
        "text": "Casual lunch and dinner destination for Northern Mexican-style tacos with grilled meats and vegetables.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/reviews/ChdDSUhNMG9nS0VJQ0FnSURucDQ2amlnRRAB",
          "relativePublishTimeDescription": "in the last week",
          "rating": 5,
          "text": {
            "text": "Next level tacos and burritos! The Cebesa is really good but a bit too fatty for me, their asada is just wow and it’s server on the softest tortillas I’ve ever had. You can taste the freshness of the ingredients from the first bite + the atmosphere is really charming!! Definitely saving this spot.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Next level tacos and burritos! The Cebesa is really good but a bit too fatty for me, their asada is just wow and it’s server on the softest tortillas I’ve ever had. You can taste the freshness of the ingredients from the first bite + the atmosphere is really charming!! Definitely saving this spot.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Célia",
            "uri": "https://www.google.com/maps/contrib/116433533280536491494/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUrtLPQ8sXNQhpjHh15ibAyBPe5Erw_wr8buuGsZ1zYgk7P5kg=s128-c0x00000000-cc-rp-mo-ba6"
          },
          "publishTime": "2024-10-10T23:39:27.310556Z"
        },
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/reviews/ChdDSUhNMG9nS0VJQ0FnSUQ3dU1EeW5BRRAB",
          "relativePublishTimeDescription": "a month ago",
          "rating": 5,
          "text": {
            "text": "Absolutely love the tripas here. Price makes sense for quality and location. I have visited previous times and was disappointed that this time around no cebollita was included with our orders. But the food is still good and vibes good and unchanged. Also, really like their merch.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Absolutely love the tripas here. Price makes sense for quality and location. I have visited previous times and was disappointed that this time around no cebollita was included with our orders. But the food is still good and vibes good and unchanged. Also, really like their merch.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Liz Velazquez",
            "uri": "https://www.google.com/maps/contrib/106087475574989405533/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocIU99MmQwzV2EBBVLN906iVZZqmRAtMiQVWQbKNRw8sK-PqSQ=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-08-21T15:27:28.791511Z"
        },
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/reviews/ChZDSUhNMG9nS0VJQ0FnSUNiakxtTFVnEAE",
          "relativePublishTimeDescription": "2 months ago",
          "rating": 5,
          "text": {
            "text": "The tacos here remind me of what I used to eat back home when I was a kid. The tortillas are perfect and the carne asada tacos are some of the best I’ve had in LA.  The aguas frescas here are also so delicious. We had the strawberry with lime and the horchata con coco and they were both amazing. 10/10",
            "languageCode": "en"
          },
          "originalText": {
            "text": "The tacos here remind me of what I used to eat back home when I was a kid. The tortillas are perfect and the carne asada tacos are some of the best I’ve had in LA.  The aguas frescas here are also so delicious. We had the strawberry with lime and the horchata con coco and they were both amazing. 10/10",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Kaina Crow",
            "uri": "https://www.google.com/maps/contrib/106035588606799586547/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUlZ8ybe7XTJ_3TZ2C-WBdAenN4nK1xVMM-WvmTGPtu6Od60H0Y=s128-c0x00000000-cc-rp-mo-ba3"
          },
          "publishTime": "2024-07-24T02:59:14.529712Z"
        },
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/reviews/ChZDSUhNMG9nS0VJQ0FnSUNiczlPR1hREAE",
          "relativePublishTimeDescription": "2 months ago",
          "rating": 5,
          "text": {
            "text": "Best tacos in LA. love the flour tortillas made with pork fat and grilled. Delicious salsas. Highly recommend the caramelo. It’s like a big taco! Next time I go back I’ll try the cabeza. Only had tripa. Delicious!",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Best tacos in LA. love the flour tortillas made with pork fat and grilled. Delicious salsas. Highly recommend the caramelo. It’s like a big taco! Next time I go back I’ll try the cabeza. Only had tripa. Delicious!",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Victoria",
            "uri": "https://www.google.com/maps/contrib/105323676993490918248/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocKR7LxkQ5AFy_JVimkj80CTaAF0y_aGG772N8y70g7AbMfocbM=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-07-29T19:26:25.533093Z"
        },
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/reviews/ChZDSUhNMG9nS0VJQ0FnSUNidE5HaGFnEAE",
          "relativePublishTimeDescription": "2 months ago",
          "rating": 5,
          "text": {
            "text": "First timers and let me just say BEST AUTHENTIC MEXICAN TACOS 🌮 the restaurant is clean and tidy, staff are all beyond kind and helpful but the chorizo and asada tacos are beyond good. Reminds me when I was in Mexico woudl certainly come back no questions asked!",
            "languageCode": "en"
          },
          "originalText": {
            "text": "First timers and let me just say BEST AUTHENTIC MEXICAN TACOS 🌮 the restaurant is clean and tidy, staff are all beyond kind and helpful but the chorizo and asada tacos are beyond good. Reminds me when I was in Mexico woudl certainly come back no questions asked!",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Jay",
            "uri": "https://www.google.com/maps/contrib/114333375208519975042/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocKSPX23tNzsm5p_dClr1KJv1Swas2Af1wFool-UmrQ_DG8YqvI=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-07-23T21:31:53.136758Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/photos/AdCG2DOLFmdtxR5-1qBNjcVtufXHhT6mi0fYDXsjOrBf0g3uKI8HTzobi7Zx-ppJFfV6bqyinkGwJh7D5DdSn7CjIeNk7FUJv_9v8hYOVPSjjYajEJJE6aUDlKuCzvyV9D8Mh5fYpnLQFrLjnq9Pbdr2iIxx9qNnSR-axYJW",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Conor Odell",
              "uri": "https://maps.google.com/maps/contrib/112277241584513559370",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVRaXnPSeMIyfRzABTMoTMBwFBfmqqrC1gKz8pA6kVB1JTop7wM=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/photos/AdCG2DOT2ScJtiiGTAa_MkUwIr9ow888RgSa_lc-WaCrAyZg6KeF4PVlx0oZ6YP50iwLViSJHKQMyie3PPwCCJ2s6_NMStVBtCuSSe24XSQoQ0qd_CjVIJjXDFQI-OA4dNFTrh71YjOxN07fvt2n50WBcUyxApfyEoZy8jK8",
          "widthPx": 750,
          "heightPx": 422,
          "authorAttributions": [
            {
              "displayName": "Sonoratown",
              "uri": "https://maps.google.com/maps/contrib/115291147672655077378",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWUWU8Zq4xfnvl3E0-EmwppqRVjTEJlHgr88K01ek5wG5YwLAA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/photos/AdCG2DP216OSw3GNBr2v9FFQ69x2BFXKhrFcPWQLLfrjVlHn-IifUMdSuvtFEgDf8WPDO9VtvOz1eUZRIzu5k6D3pemOFGOsimyAy46a68zov9Xu3x9R1CGRZsHLmbtc6-hhiBb6-hSeGYjLDvXfml6AcM0jt3RLlTk4ReI-",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "MATTHEW SODIKOFF",
              "uri": "https://maps.google.com/maps/contrib/106161808665916258813",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocKyR6ECfaOWFN9c4fFehvEv57ysaX3TWddgH_nrmnyVydPfmA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/photos/AdCG2DMiqimBBU0OOoKGNSZfFx6jsfn1RcCfsM_SYjWIZdNbPKSwnYnUf1zLb94jQdGUtRATgvQ68YZzlvkqOlzVAOztLAhxU-yRG0lZ8O5oyV1YokuVwIfQPEIwBD9lVxMXOUM4wf8CI8AM3eCtbk7uoOe_lV4njb5jiVPV",
          "widthPx": 4000,
          "heightPx": 3000,
          "authorAttributions": [
            {
              "displayName": "bert sanchez",
              "uri": "https://maps.google.com/maps/contrib/106718809878720811222",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWamASwnqh7lIAvaAfyPTaCGhi5trJLPLoLpmBOIrEu4FAxEek=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/photos/AdCG2DNwbCV21N4nG4GoEwKaPab0miyNYBcXD8ERZ6Lq_lQRFmDwXxwdOVN-L-k3AJ9pngC9oOutDXrWZ5Fx0edoyoNh3ja1Etz9xQdE2Mq9L0o8cfFIltXxn87sCc5IYsW3UJ85NTz08NEcUT_4scraAyNJPic1_J7DgAkL",
          "widthPx": 4800,
          "heightPx": 3600,
          "authorAttributions": [
            {
              "displayName": "Lei",
              "uri": "https://maps.google.com/maps/contrib/100002085310562449464",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWn1_iSm0cAYxNAV0VqeQpvj0VWxIH-GQ0VaPw-p35u-vSDahid=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/photos/AdCG2DM3Rqbt1deY92Ykgn0ZgoGTbFbx_7JpfEwMPjGot1bqQnFcyXssAYmci9HqKV3Glbt3AWcKybFfx-vR8QWUMBH-syKoht07RGf760LWMvCLFKBpkQ7gJ0HcNLIb9pMLxRfgBAngXtcdeE4WnQZsc5vm-MOCaOhL2B3a",
          "widthPx": 4080,
          "heightPx": 3072,
          "authorAttributions": [
            {
              "displayName": "Joseph Alonzo",
              "uri": "https://maps.google.com/maps/contrib/100525512622394612789",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVLcsb3A9x7yPJ-7pbH2VQeSUKgLVbMBEiD8mNg1a4kPzFJAIXq=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/photos/AdCG2DPFpjVXmj_SRjV--H1CdfAcVx7hmLR9Eqsy8yYN6mCdWVEGEbYLw7o-mKqwcsL3jY38tYTLSzodiqvYu3H6DjhUsIy0QeoVjvlk3v10AnJFghAMikeQIFNdwlmgfWaq-LX-VR91BCQzU_GaahLam2Cz6Cz1e6BU_wrB",
          "widthPx": 3637,
          "heightPx": 2252,
          "authorAttributions": [
            {
              "displayName": "Luis Martinez",
              "uri": "https://maps.google.com/maps/contrib/101531464188800511767",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocKPnU0FlVu3wwou4G__FWTaVyjUTTi8B18Dk5kM6V2icBD1GA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/photos/AdCG2DNZmEWZkdToJyJ82MEUM_iy4VgOOiCAM2Z2Qb9qZYcUx0DPgOQN9AkA2kSWrhMQhT7-QspRxpyTO3_L3FM-E92YN5HYc-P81dAvrUzUy-3rxdp3Blxmf6VlB60_LFV36W10_ioPXaT6Cb0O_olqvCItgwIewmQel15b",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Agustin Valenzuela",
              "uri": "https://maps.google.com/maps/contrib/105841946445816184273",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWl3-7_Za4kaWdQ1dAmO7bfj7SPe-YKnTn4aja2jI_dQbpfct6Rjg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/photos/AdCG2DOugszPWp99oEM3E1kkCvuSVEAAlhXdj_5vURFx_eKU7L-nUnI6DXryCerhZ22jRB-RS72b3fC_MaDsw0pxrxCULyx7JPuOjBahcxJEgixuRajFh5TyAUa_sK7osHnzzER8gorvy9JUIAFqQgl1tRNB0rRiZN0-SpAL",
          "widthPx": 4800,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "antonio caballero",
              "uri": "https://maps.google.com/maps/contrib/118003281318483003363",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVMPHOM7al0vWnY9v474jQUJ2XLtxLF8cC4k7MeXXMNJ81FmH1h=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ45QjyjTGwoARVNFElqulM0U/photos/AdCG2DOZkKyLbn-GFJgKRdoPuYuYc8YzgXYLsJlnhPPPGX0Gj60dRsBjD5W_hnltOT9frdHKdLqRKIT-cBY_qo6hfw_DlScvcA42mbKD2fzNgzmpUhZDCIKuMlZpjSMc6CP-wIOdRkY7D7MoQlsY-gON3bUXF1Mt2uWABc-C",
          "widthPx": 3072,
          "heightPx": 4080,
          "authorAttributions": [
            {
              "displayName": "Eoin O'Donoghue",
              "uri": "https://maps.google.com/maps/contrib/111091709056784240035",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXzNeGfyU4XghwNJoMJrQAkzYG3DApqTiBWvCCC3Y9UF3-JFpkN=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "liveMusic": False,
      "menuForChildren": False,
      "servesCocktails": False,
      "servesDessert": False,
      "servesCoffee": False,
      "goodForChildren": True,
      "goodForWatchingSports": False,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "parkingOptions": {
        "freeParkingLot": False,
        "paidParkingLot": True,
        "freeStreetParking": False,
        "paidStreetParking": True,
        "valetParking": False,
        "freeGarageParking": False,
        "paidGarageParking": False
      },
      "accessibilityOptions": {
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Casual spot turning out Sonoran-style tacos and burritos, plus quesadillas and chivichangas.",
          "languageCode": "en-US"
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJl4S1MsvHwoARVyXeSs0Pr4U",
            "placeId": "ChIJl4S1MsvHwoARVyXeSs0Pr4U",
            "displayName": {
              "text": "Escape Room LA",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest",
              "tourist_attraction"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 63.491146,
            "travelDistanceMeters": 64.974655
          },
          {
            "name": "places/ChIJ17EwxTTGwoARE2pmgz5d4fo",
            "placeId": "ChIJ17EwxTTGwoARE2pmgz5d4fo",
            "displayName": {
              "text": "SuitFellas",
              "languageCode": "en"
            },
            "types": [
              "clothing_store",
              "establishment",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 71.75626,
            "travelDistanceMeters": 92.27183
          },
          {
            "name": "places/ChIJd-FUvzTGwoAR_EVh_bfBC8E",
            "placeId": "ChIJd-FUvzTGwoAR_EVh_bfBC8E",
            "displayName": {
              "text": "Garment Lofts",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest",
              "real_estate_agency"
            ],
            "spatialRelationship": "ACROSS_THE_ROAD",
            "straightLineDistanceMeters": 38.951412,
            "travelDistanceMeters": 32.7439
          },
          {
            "name": "places/ChIJWQrC-crHwoARJvmB0kX7tbI",
            "placeId": "ChIJWQrC-crHwoARJvmB0kX7tbI",
            "displayName": {
              "text": "The Orpheum Theatre",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 326.9009,
            "travelDistanceMeters": 462.05588
          },
          {
            "name": "places/ChIJF6PmuTTGwoARBzEPd2uY8MA",
            "placeId": "ChIJF6PmuTTGwoARBzEPd2uY8MA",
            "displayName": {
              "text": "Ace Sewing Machine Co",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 39.69226,
            "travelDistanceMeters": 38.728283
          }
        ],
        "areas": [
          {
            "name": "places/ChIJf_9O_SzGwoARtrkWOBLCwII",
            "placeId": "ChIJf_9O_SzGwoARtrkWOBLCwII",
            "displayName": {
              "text": "Fashion District",
              "languageCode": "en"
            },
            "containment": "OUTSKIRTS"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg",
      "id": "ChIJ9xaRZ_7GwoAR2654oYfw5cg",
      "types": [
        "mexican_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 250-7600",
      "internationalPhoneNumber": "+1 213-250-7600",
      "formattedAddress": "1261 Sunset Blvd, Los Angeles, CA 90026, USA",
      "addressComponents": [
        {
          "longText": "1261",
          "shortText": "1261",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "Sunset Boulevard",
          "shortText": "Sunset Blvd",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Echo Park",
          "shortText": "Echo Park",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90026",
          "shortText": "90026",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85633PCX+3V",
        "compoundCode": "3PCX+3V Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.0702213,
        "longitude": -118.25028730000001
      },
      "viewport": {
        "low": {
          "latitude": 34.0688292697085,
          "longitude": -118.25173908029147
        },
        "high": {
          "latitude": 34.0715272302915,
          "longitude": -118.24904111970849
        }
      },
      "rating": 4.6,
      "googleMapsUri": "https://maps.google.com/?cid=14476241042572619483",
      "websiteUri": "http://www.guisados.co/",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 10,
              "minute": 0
            },
            "close": {
              "day": 1,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 10,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 10,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 10,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 5,
              "hour": 23,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 23,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 10:00 AM – 10:00 PM",
          "Tuesday: 10:00 AM – 10:00 PM",
          "Wednesday: 10:00 AM – 10:00 PM",
          "Thursday: 10:00 AM – 10:00 PM",
          "Friday: 9:00 AM – 11:00 PM",
          "Saturday: 9:00 AM – 11:00 PM",
          "Sunday: 9:00 AM – 9:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e1261 Sunset Blvd\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90026\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_INEXPENSIVE",
      "userRatingCount": 2746,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Guisados",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "reservable": False,
      "servesBreakfast": True,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": True,
      "servesWine": False,
      "servesVegetarianFood": True,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 10,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 10,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 10,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 10,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 23,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 23,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 10:00 AM – 10:00 PM",
          "Tuesday: 10:00 AM – 10:00 PM",
          "Wednesday: 10:00 AM – 10:00 PM",
          "Thursday: 10:00 AM – 10:00 PM",
          "Friday: 9:00 AM – 11:00 PM",
          "Saturday: 9:00 AM – 11:00 PM",
          "Sunday: 9:00 AM – 9:00 PM"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "1261 Sunset Blvd, Los Angeles",
      "editorialSummary": {
        "text": "Unpretentious taco spot known for its braised meat & veggie stews atop handmade tortillas.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/reviews/ChZDSUhNMG9nS0VJQ0FnSURubGZ5eVZBEAE",
          "relativePublishTimeDescription": "a week ago",
          "rating": 5,
          "text": {
            "text": "So so so good. I’ve never had tacos with stewed meats, and I was blown away by how tender and moist the fillings are. I didn’t even find myself reaching for limes! We got the special ceviche tostada too, and it was out of this world.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "So so so good. I’ve never had tacos with stewed meats, and I was blown away by how tender and moist the fillings are. I didn’t even find myself reaching for limes! We got the special ceviche tostada too, and it was out of this world.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "abnarishkin",
            "uri": "https://www.google.com/maps/contrib/106452413907571001876/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLZu1dCKNtJ_fKsoqZ6Y3OtF-M-lqfNSeFLoKzKNtIb_41-GZ0=s128-c0x00000000-cc-rp-mo-ba3"
          },
          "publishTime": "2024-10-08T04:30:02.489159Z"
        },
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/reviews/ChZDSUhNMG9nS0VJQ0FnSURicDdmQ0ZBEAE",
          "relativePublishTimeDescription": "2 months ago",
          "rating": 5,
          "text": {
            "text": "Great spot for some delicious tacos before a Dodger game, plenty of room inside and outside. The service was also amazing. The only drawback is the limited parking during games, but if you get here early, it's manageable.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Great spot for some delicious tacos before a Dodger game, plenty of room inside and outside. The service was also amazing. The only drawback is the limited parking during games, but if you get here early, it's manageable.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Edwin Alonso",
            "uri": "https://www.google.com/maps/contrib/107991225559811267421/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWLTZJKCxogr_dNi9fAS5De4So1Wf0r-s1iB_2Vz8l-KezT7eqv=s128-c0x00000000-cc-rp-mo-ba3"
          },
          "publishTime": "2024-08-10T05:48:08.101801Z"
        },
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/reviews/ChdDSUhNMG9nS0VJQ0FnSURyZzhPMDBRRRAB",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 5,
          "text": {
            "text": "Guisados is a fine spot to get authentic handmade tacos. I tried a few, and they really did burst with flavor. The tortillas were freshly made in front of you, which makes it even better. The seating space indoors and outdoors makes the place quite comfortable while enjoying the food. The bright outdoor mural brings some flair to the ambiance as well. It's also great value for the quality and taste. I would definitely recommend this to anyone who enjoys tasty, freshly made tacos!",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Guisados is a fine spot to get authentic handmade tacos. I tried a few, and they really did burst with flavor. The tortillas were freshly made in front of you, which makes it even better. The seating space indoors and outdoors makes the place quite comfortable while enjoying the food. The bright outdoor mural brings some flair to the ambiance as well. It's also great value for the quality and taste. I would definitely recommend this to anyone who enjoys tasty, freshly made tacos!",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "James L Hebert",
            "uri": "https://www.google.com/maps/contrib/108996070922741237614/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUcQAWTm1glOo6e3G2RwUTjLptdmmbEUMlGDrQbfgMIr45KAik=s128-c0x00000000-cc-rp-mo-ba3"
          },
          "publishTime": "2024-07-19T16:18:29.511634Z"
        },
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/reviews/ChZDSUhNMG9nS0VJQ0FnSURUbU1PWUhBEAE",
          "relativePublishTimeDescription": "4 months ago",
          "rating": 5,
          "text": {
            "text": "Vegetarian & Vegan friendly!!! I tried 2x Hongos con cilantro, 1 Vegan Medley, 2x Vegetarian Quesadillas and I must say their flavors were quite nice!! I really like how the tacos were made fresh - you can even see it done when you walk in. There is plenty of space to eat inside or outside, and parking in their lot or on the street",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Vegetarian & Vegan friendly!!! I tried 2x Hongos con cilantro, 1 Vegan Medley, 2x Vegetarian Quesadillas and I must say their flavors were quite nice!! I really like how the tacos were made fresh - you can even see it done when you walk in. There is plenty of space to eat inside or outside, and parking in their lot or on the street",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Victoria Thuy Vy Pham",
            "uri": "https://www.google.com/maps/contrib/115603739151394261495/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjW-ZdcELHJ_dIlCyIPtQL_JeaShG9YDd9nK8mFT5WRPm35IHuzV=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-05-22T06:15:12.438422Z"
        },
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/reviews/ChZDSUhNMG9nS0VJQ0FnSUM5N0wzaWNREAE",
          "relativePublishTimeDescription": "4 months ago",
          "rating": 5,
          "text": {
            "text": "We’ve been two Sundays in a row since first trying their tacos. The first time we stopped in for a snack and I got the hongos (mushrooms) and vegan medley tacos. The second time I got the vegetarian sampler plate of six mini tacos, which came with two hongos, two calabacitas, one quesadilla, and one frijoles tacos.\n\nMy boyfriend has tried most of their meat tacos as well and gave rave reviews on them all, saying they’re super flavorful.\n\nWe also tried their horchata with cold brew which was delicious.\n\nEverything here has been great, from the staff to the outdoor seating. Wait time is never bad, even with a line. Their salsas are delicious, everything is perfectly cooked and their tortillas!!!\n\nTheir tortillas are made fresh in house and are killer 🤩\n\nTacos are a bit on the pricey side at $4.25 for most types or $11.25 for the six mini tacos, but what isn’t nowadays.\n\nWe’ll definitely be back!\n\nFollow my adventures!\nYT & IG: @apriladventuring ✌️",
            "languageCode": "en"
          },
          "originalText": {
            "text": "We’ve been two Sundays in a row since first trying their tacos. The first time we stopped in for a snack and I got the hongos (mushrooms) and vegan medley tacos. The second time I got the vegetarian sampler plate of six mini tacos, which came with two hongos, two calabacitas, one quesadilla, and one frijoles tacos.\n\nMy boyfriend has tried most of their meat tacos as well and gave rave reviews on them all, saying they’re super flavorful.\n\nWe also tried their horchata with cold brew which was delicious.\n\nEverything here has been great, from the staff to the outdoor seating. Wait time is never bad, even with a line. Their salsas are delicious, everything is perfectly cooked and their tortillas!!!\n\nTheir tortillas are made fresh in house and are killer 🤩\n\nTacos are a bit on the pricey side at $4.25 for most types or $11.25 for the six mini tacos, but what isn’t nowadays.\n\nWe’ll definitely be back!\n\nFollow my adventures!\nYT & IG: @apriladventuring ✌️",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "April Adventuring",
            "uri": "https://www.google.com/maps/contrib/111832775147882119557/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVXwgwmeF89Yj0tv_paO7fu7L-kBd2nECrDsL6_Clbm06-RKdf3=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-06-18T20:08:31.964496Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/photos/AdCG2DNgO6YjRM8B5EgE5yROxk7NEFYh_QbfZNv6sRBubJ1mr5VTPpNigtKBf8SrH4jm4RX9z43040J95rFErDyeJ4OtadQzU1gRcozGmkAIUosS7nJuvZJv9tRbekGKTp-7k_Wo9utMiOc3fAt-UJQey3DNPhx8YgZpgPMZ",
          "widthPx": 3264,
          "heightPx": 1836,
          "authorAttributions": [
            {
              "displayName": "Shmuel Gonzales",
              "uri": "https://maps.google.com/maps/contrib/112059600297316331401",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjV66EK_cY7XMwF6pHKcj2ztqpGijjauczFHZfxeMMG34B2wYHTuUg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/photos/AdCG2DOnmWdsPs9QBZsNJkTOCMSfoK_IUMt9yN-MZJH1Gtl3UmeIfGTwnDar1OwKTi-JcFWDkTCPFTsxSkuwU11lamsmqsTb8CjQSQSN1ZUOCO1DkM_Be4jXcWKuIRJOWFauol3yQqM2524w99BkqjXkq-pOkyJDSxaGrh61",
          "widthPx": 4800,
          "heightPx": 3600,
          "authorAttributions": [
            {
              "displayName": "ゆずたそ",
              "uri": "https://maps.google.com/maps/contrib/101329440211616360058",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVcjCj7XjgiPsWim-e4iK0Nujn_PLFc370Ao3DpIMharjjh0KYo=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/photos/AdCG2DN8o2dQKVZu9idy6dKxSAFFEoJ5n14rb5t8DA_i_KuC4ZcIeVTwj8Sst7yuUhadaekAeNHn6TugLlzqiICpEZaqxNIEnq9QifHGhnU0mHa27ITWqPeYV0Ly-jmmyV-rasYL4zc4CZ5DYt42FPnl8JbFfiUNeJNOQ9Br",
          "widthPx": 4000,
          "heightPx": 3000,
          "authorAttributions": [
            {
              "displayName": "Jennifer Wallin",
              "uri": "https://maps.google.com/maps/contrib/104245938711737570320",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVD0skbbn_sQ9pd64wuEKMXHFwag4Z4qldgcNBZTD3rKhdrftEmXw=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/photos/AdCG2DNPosVWBETqu6LY5kcN52xDX2H4Q3v_AWVLwSi8CCwQXcfwNWZAC9C_80nATj7jzfVKMFGv5nrFAosuMJKI6Ye1XsOb58nu4YtBLroBfM1k7UzRNkHqyH9757AtyxHI6FnQ92S3QnPR5iMZLKXNqcdCKFVpdwAv90NX",
          "widthPx": 4032,
          "heightPx": 2268,
          "authorAttributions": [
            {
              "displayName": "Ivan Zhurbin",
              "uri": "https://maps.google.com/maps/contrib/117236385074326307727",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWG8_jlevm7WOwcOZVgooRsptHRbUBCQwfS5e_SG1MP180P3vnLvQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/photos/AdCG2DMZKyli0cXTSicjtL01KCLk7jcWJV4yMS5rYON43plrQakzkieG7Bo9iaJzEn-7qpCKTiVBeCsXErW2Hj-d5C9OZsKyK5MvbOUz3_Gb7v0horEuDbbhD3ewcJDcwp_Njcukqht1IuI1NEqWC4wQsCZroovUtfpn157q",
          "widthPx": 4080,
          "heightPx": 3072,
          "authorAttributions": [
            {
              "displayName": "Ivan Zhurbin",
              "uri": "https://maps.google.com/maps/contrib/117236385074326307727",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWG8_jlevm7WOwcOZVgooRsptHRbUBCQwfS5e_SG1MP180P3vnLvQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/photos/AdCG2DMTkDIuqwMyWtg4u51G5s8r9WBAS0TlFLFkTTUscWo22IfV7oZXNajUeWbndgmDKFg04mUrnk9NSZ_n96k-LhXTvOm5wMw6cJ85qhDMOGARNAcbp9lJXyjH7GhOqmVhmz-vOTFiP1ZrngqahB_CT3HE_iF5vlqweRqR",
          "widthPx": 4800,
          "heightPx": 3600,
          "authorAttributions": [
            {
              "displayName": "ゆずたそ",
              "uri": "https://maps.google.com/maps/contrib/101329440211616360058",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVcjCj7XjgiPsWim-e4iK0Nujn_PLFc370Ao3DpIMharjjh0KYo=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/photos/AdCG2DNi5uQJplbiZM6S-Qn3lv7e9ssIdA4r8gi2_zyzioD7v1xdVtevWCGlXrzhXkLrMUJ51pB0GTR50X-1ruXvrWOp-n1bTSPxnSbRJGBeJS-oaoW5f1QGhxbGP5p6uvmhxS1zIunCs5FCJopG1ZUTtSxuNIdMPHg-sKbC",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "John Lee",
              "uri": "https://maps.google.com/maps/contrib/117284092240499290002",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUkxfBu9d_cb-3NRxLBNnZ6bGXMoDjIZklFtAXygT2kDRfKEAUq=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/photos/AdCG2DNxl7CuALrOaAmGVAVVUj_wqMWmjA3I3u6cmKo85Ex42tweC_5enx9uOX_-l-XRM8uNzYguRoeEqOOSStwdqq6R_Iksauw3pNnja1z5OTJ63JWMloPT5JzSBQU2gexaOLxyHF3jtVNU1lkfBo77v_lrqT1zbKzq1ds",
          "widthPx": 4050,
          "heightPx": 2196,
          "authorAttributions": [
            {
              "displayName": "Edwin Suarez",
              "uri": "https://maps.google.com/maps/contrib/107776853487986969423",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVLyEyWfrhGFwd1DUKoCVVugnKWmPrFSg6gMUERrH_PAqvzpiYa=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/photos/AdCG2DPySJWwvXYgovZ2ATSA7lU-TZovjrPw7CsgRGMFTlqEFE8lNCqkvChLgMhnrjGqmIIGBIWS1k3SEBPgxHLdFOgn18ZZDtPqpy5nXFKjwweXrBDcnGR3xLz3i8vg-5t9L_XID6gDvv1_vvsLji7w4lBxb9xGTAbGdEp_",
          "widthPx": 4000,
          "heightPx": 2252,
          "authorAttributions": [
            {
              "displayName": "Edwin Alonso",
              "uri": "https://maps.google.com/maps/contrib/107991225559811267421",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWLTZJKCxogr_dNi9fAS5De4So1Wf0r-s1iB_2Vz8l-KezT7eqv=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ9xaRZ_7GwoAR2654oYfw5cg/photos/AdCG2DOahlphjy0H35-udpB1MdVErspVK_NisuUppFQ32chiur_0eKlOAwpFXf71lh5MkOj6ta_3Dgsi5pKPl2w9eRcdDwsH0iOTkt6b7b0TuBKv90NjSYbbpiimJT5YNaTbViYY5IHdBiadaVUPaKjfTI-rDGG_ebhZJByQ",
          "widthPx": 3024,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Zed Adams",
              "uri": "https://maps.google.com/maps/contrib/112622463402935791531",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjX8G8NjjDKDIttcDZfATKVeEIbhBmDOGIvd8J7AjvBQUVllhFiwwQ=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "liveMusic": False,
      "menuForChildren": False,
      "servesCocktails": False,
      "servesDessert": True,
      "servesCoffee": True,
      "goodForChildren": True,
      "restroom": True,
      "goodForGroups": True,
      "goodForWatchingSports": False,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "parkingOptions": {
        "freeParkingLot": True,
        "freeStreetParking": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleParking": True,
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleRestroom": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Cozy eatery doling out homestyle Mexican braises on handmade corn tortillas, plus cold beers.",
          "languageCode": "en-US"
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJi-ji2v_GwoARfMGQnESirqg",
            "placeId": "ChIJi-ji2v_GwoARfMGQnESirqg",
            "displayName": {
              "text": "Bob's Market",
              "languageCode": "en"
            },
            "types": [
              "convenience_store",
              "establishment",
              "food",
              "grocery_or_supermarket",
              "liquor_store",
              "point_of_interest",
              "store"
            ],
            "straightLineDistanceMeters": 331.91254,
            "travelDistanceMeters": 427.96036
          },
          {
            "name": "places/ChIJjxBGwf3GwoARaszNbZnssKg",
            "placeId": "ChIJjxBGwf3GwoARaszNbZnssKg",
            "displayName": {
              "text": "Eightfold Coffee",
              "languageCode": "en"
            },
            "types": [
              "cafe",
              "establishment",
              "food",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 117.81163,
            "travelDistanceMeters": 113.174644
          },
          {
            "name": "places/ChIJTxNVCtvHwoARP6HA_wpcSVg",
            "placeId": "ChIJTxNVCtvHwoARP6HA_wpcSVg",
            "displayName": {
              "text": "Bar Henry",
              "languageCode": "en"
            },
            "types": [
              "bar",
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 138.14932,
            "travelDistanceMeters": 126.413315
          },
          {
            "name": "places/ChIJ1-AcLWG6woARgyVeosF45s8",
            "placeId": "ChIJ1-AcLWG6woARgyVeosF45s8",
            "displayName": {
              "text": "Super 8 by Wyndham Los Angeles Downtown",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "lodging",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 299.98193,
            "travelDistanceMeters": 273.39215
          },
          {
            "name": "places/ChIJw5PtOa3HwoARGa0TiKavJ54",
            "placeId": "ChIJw5PtOa3HwoARGa0TiKavJ54",
            "displayName": {
              "text": "Charmed House",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 354.4647,
            "travelDistanceMeters": 738.63153
          }
        ],
        "areas": [
          {
            "name": "places/ChIJW0irLOfGwoARgOwMHRhRHl0",
            "placeId": "ChIJW0irLOfGwoARgOwMHRhRHl0",
            "displayName": {
              "text": "Echo Park",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U",
      "id": "ChIJOaaU_MbHwoARcKYAojw0-3U",
      "types": [
        "mexican_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "formattedAddress": "812 E 3rd St, Los Angeles, CA 90013, USA",
      "addressComponents": [
        {
          "longText": "812",
          "shortText": "812",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "East 3rd Street",
          "shortText": "E 3rd St",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90013",
          "shortText": "90013",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632QW7+7M",
        "compoundCode": "2QW7+7M Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.045731499999995,
        "longitude": -118.23582820000001
      },
      "viewport": {
        "low": {
          "latitude": 34.0444296697085,
          "longitude": -118.23719353029151
        },
        "high": {
          "latitude": 34.0471276302915,
          "longitude": -118.23449556970853
        }
      },
      "rating": 4.3,
      "googleMapsUri": "https://maps.google.com/?cid=8501446156612576880",
      "websiteUri": "http://www.chachacha.la/",
      "regularOpeningHours": {
        "openNow": False,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 12,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 16,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 0,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 12,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 16,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 12,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 16,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 12,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 16,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 12,
              "minute": 0
            },
            "close": {
              "day": 5,
              "hour": 16,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 5,
              "hour": 23,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 12,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 16,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 23,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: Closed",
          "Tuesday: 12:00 – 4:00 PM, 5:00 – 10:00 PM",
          "Wednesday: 12:00 – 4:00 PM, 5:00 – 10:00 PM",
          "Thursday: 12:00 – 4:00 PM, 5:00 – 10:00 PM",
          "Friday: 12:00 – 4:00 PM, 5:00 – 11:00 PM",
          "Saturday: 12:00 – 4:00 PM, 5:00 – 11:00 PM",
          "Sunday: 12:00 – 4:00 PM, 5:00 – 10:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e812 E 3rd St\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90013\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "userRatingCount": 457,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "LA Cha Cha Chá",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": False,
      "delivery": True,
      "dineIn": True,
      "curbsidePickup": False,
      "reservable": True,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": True,
      "servesWine": True,
      "servesBrunch": True,
      "servesVegetarianFood": True,
      "currentOpeningHours": {
        "openNow": False,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 12,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 16,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 0,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 12,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 16,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 12,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 16,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 12,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 16,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 12,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 16,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 23,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 12,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 16,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 23,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: Closed",
          "Tuesday: 12:00 – 4:00 PM, 5:00 – 10:00 PM",
          "Wednesday: 12:00 – 4:00 PM, 5:00 – 10:00 PM",
          "Thursday: 12:00 – 4:00 PM, 5:00 – 10:00 PM",
          "Friday: 12:00 – 4:00 PM, 5:00 – 11:00 PM",
          "Saturday: 12:00 – 4:00 PM, 5:00 – 11:00 PM",
          "Sunday: 12:00 – 4:00 PM, 5:00 – 10:00 PM"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "812 E 3rd St, Los Angeles",
      "editorialSummary": {
        "text": "Stylish restaurant with a terrace serving modern Mexican cuisine, tacos & cocktails.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/reviews/ChdDSUhNMG9nS0VJQ0FnSUNuZ2RqLTZ3RRAB",
          "relativePublishTimeDescription": "3 weeks ago",
          "rating": 4,
          "text": {
            "text": "Food is almost Mexican. Wonderful, if you are big parties, order to share the mains. Staff is friendly and helpful. Nice for a night out feeling you are in Mexico City! Churros are freshly made and with a great selection of dips. Melted cheese dish was not reflecting what you get in Mexico. Fish, chicken and meat were great.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Food is almost Mexican. Wonderful, if you are big parties, order to share the mains. Staff is friendly and helpful. Nice for a night out feeling you are in Mexico City! Churros are freshly made and with a great selection of dips. Melted cheese dish was not reflecting what you get in Mexico. Fish, chicken and meat were great.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "eustachio vincenzo gravela",
            "uri": "https://www.google.com/maps/contrib/110939553959279187071/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWB6DB_RgCuYHAW9vN9VEDfyBIwRV_z0jnOTGeKXa2x8w96J-H2=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-09-26T15:03:12.883682Z"
        },
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/reviews/ChdDSUhNMG9nS0VJQ0FnSUNIelBuMTNRRRAB",
          "relativePublishTimeDescription": "a month ago",
          "rating": 5,
          "text": {
            "text": "Excellent restaurant with a great vibe. The service has been amazing. Juan was our waiter and very attentive to our needs. We tried a whole bunch of different appetizers and they were all great. Our main entrée was the fish which is also great.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Excellent restaurant with a great vibe. The service has been amazing. Juan was our waiter and very attentive to our needs. We tried a whole bunch of different appetizers and they were all great. Our main entrée was the fish which is also great.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Mr. Chez",
            "uri": "https://www.google.com/maps/contrib/111022174094459657684/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXOaYrDvvlfgrymJmZW0Xqa74ilPA4RmBEP0oQDfbbvL-Tloms=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-09-02T01:54:50.600686Z"
        },
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/reviews/ChdDSUhNMG9nS0VJQ0FnSURuX2VqR3JBRRAB",
          "relativePublishTimeDescription": "a week ago",
          "rating": 4,
          "text": {
            "text": "La Cha Cha has a cool rooftop that makes you feel like you’re in Mexico City – perfect for a girls’ night. The food was good, but a bit pricey for what you get. It was busy and loud when I went, but still fun if you’re looking for a lively vibe!",
            "languageCode": "en"
          },
          "originalText": {
            "text": "La Cha Cha has a cool rooftop that makes you feel like you’re in Mexico City – perfect for a girls’ night. The food was good, but a bit pricey for what you get. It was busy and loud when I went, but still fun if you’re looking for a lively vibe!",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Saroosh Ahsan",
            "uri": "https://www.google.com/maps/contrib/100112205225912716397/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXPfp28SZWjeki6Qf4bWl3xVhoL-T_Cakd2QE6pUoKjH_g-eqgl2w=s128-c0x00000000-cc-rp-mo-ba3"
          },
          "publishTime": "2024-10-09T04:45:04.240328Z"
        },
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/reviews/ChZDSUhNMG9nS0VJQ0FnSUM3b3A2cURBEAE",
          "relativePublishTimeDescription": "2 months ago",
          "rating": 4,
          "text": {
            "text": "This place had the BEST vibe. Loved the outdoor dining and overall aesthetic. We sat at the bar, but still enjoyed good service. Enjoyed an excellent cocktail. Food was good, but not exceptional. Regardless, will still recommend this spot to others. Very fun, but not too loud or rowdy.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "This place had the BEST vibe. Loved the outdoor dining and overall aesthetic. We sat at the bar, but still enjoyed good service. Enjoyed an excellent cocktail. Food was good, but not exceptional. Regardless, will still recommend this spot to others. Very fun, but not too loud or rowdy.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Katie Bhandari",
            "uri": "https://www.google.com/maps/contrib/115334955333663329708/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUt4Zwl-jOVesD8C5Rmb1NBctvSd7ZLNrVMWgzyRK_Nz-0sScEv=s128-c0x00000000-cc-rp-mo-ba2"
          },
          "publishTime": "2024-08-14T03:12:51.378142Z"
        },
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/reviews/ChdDSUhNMG9nS0VJQ0FnSURuMHY3ZGpRRRAB",
          "relativePublishTimeDescription": "a week ago",
          "rating": 4,
          "text": {
            "text": "Great spot for date night! I had the poblano chicken and it was super tasty and flavorful. Birria was a little bland but the salsas were yummy and well made. Drinks were very well balanced and interesting. This is not a budget spot, but it’s worth the price. Rooftop views were blocked so you can’t see the city.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Great spot for date night! I had the poblano chicken and it was super tasty and flavorful. Birria was a little bland but the salsas were yummy and well made. Drinks were very well balanced and interesting. This is not a budget spot, but it’s worth the price. Rooftop views were blocked so you can’t see the city.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Ta TheWriter",
            "uri": "https://www.google.com/maps/contrib/106507064533823751750/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWG2-OHGN_-JA-F0kRJeXdQaMGN8lvmvNZVC0J6YpwZ6gWG8xpo=s128-c0x00000000-cc-rp-mo-ba3"
          },
          "publishTime": "2024-10-04T18:15:03.731977Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/photos/AdCG2DPd_NzCzqtT6EICw9b3U25PGKLFJ2GWxB1SUCdI-MXGBYyYDXu0pQaGCixVgnxwsylNbNB34Jgk7WUQuAzScPb4VmmeKxaUtHZ2hLHtr96X3TI2ZbClflKqMINhsK9F6RCozX4078RnEgvzR3dtKmvAFEE-utYCP-O7",
          "widthPx": 1280,
          "heightPx": 1280,
          "authorAttributions": [
            {
              "displayName": "LA Cha Cha Chá",
              "uri": "https://maps.google.com/maps/contrib/110979234770493746434",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVwIxDG7jq-g2_pplWMq8EoINk_Uqyr9PU8tWwzvO9qGCWo86U=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/photos/AdCG2DO1jaD6x7P7327LCQQYYxUTUnrWEh96o4zkpXIRlHe3HoZO5WLiNhuO1yWfnzG_XVuM7uuXSKTN_egQqnJbsp4cIUJI3Faej63hJ0gDyrN3FD0GCrwM7mOxV6crYLB8GXLJPbnoqFgwRbt0BqRgLydXbVtDgxKjttuQ",
          "widthPx": 1284,
          "heightPx": 857,
          "authorAttributions": [
            {
              "displayName": "Paprika Meow",
              "uri": "https://maps.google.com/maps/contrib/111635606610599291591",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWyV-LQAxn0N34gj-RDmgfs61rvA-7hV7bfVLoWbY_J4Q4WRnNS=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/photos/AdCG2DMW8cRXnDDrIpOUdTKu0jT10C0B7kj8d_kmE9A_pK_mUGQKe6VfHbrz-YcBo1Azcgwyvbwwri2dEpIBgPuqDQ2_erNeyF7gNObCThTV_rcF_6FELU0g287q-yJ7fbj9TP4mRsZxuUyEP80LIpoOjauWssfTPdyPO7ot",
          "widthPx": 1819,
          "heightPx": 3245,
          "authorAttributions": [
            {
              "displayName": "LA Cha Cha Chá",
              "uri": "https://maps.google.com/maps/contrib/110979234770493746434",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVwIxDG7jq-g2_pplWMq8EoINk_Uqyr9PU8tWwzvO9qGCWo86U=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/photos/AdCG2DMVF8cj9h23bcnSScHNSpfvO2p_44pM0eccgk4oJeql81ahIMu34RVved7tn33yJ7Yo74V-pS1PGcas9BCLjJJYfP7AZczSBCBPAuBvYhXJ9-kEcGKuS_U5qoddrFn70erLR4iQNt36AmEBUg9tsTBhoDoo7QD2UbCP",
          "widthPx": 3000,
          "heightPx": 4000,
          "authorAttributions": [
            {
              "displayName": "Mark Takeichi",
              "uri": "https://maps.google.com/maps/contrib/113474616128184790981",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLZmcg_rqY2Takt_dlxyrooXQjSHlu805cEmzFNEAddT6m8DQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/photos/AdCG2DOWFXUXv9XpLfMVqJOTczmZIHiAeUKqBKGaEOyjt2WiGcXB_zw4mn2DTpB181iXrquWurAxJ_195yS_JZU-xda9O-FtpeyrRvfstww_06MAxKqQj9jN7rEFXE96OT7H_Xqe7_jtLlg3Fy0KLKx19KUlRpCuSnCUJcmu",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Jiacheng Liu",
              "uri": "https://maps.google.com/maps/contrib/108928969211422614434",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUv_684L8BSYwFmrP-0f04HEDEz1nnFZMJEb-juFxWQpLJx7D3p=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/photos/AdCG2DMB80gvAaAkcGuG0Fc-vB1-Mc7aeea85YPz1R97UvoVc2aPAKtV75qAGpO6NHHo91Lom4S3ihyPmKgb4sl2fo9VNT0qvV7J2OvU511GwfrD0Bo28U6bz25AfnwBY0Y8a_q1sBXuhSTrvOMJTqj2AAQwws0wBr9eVh_h",
          "widthPx": 2744,
          "heightPx": 2744,
          "authorAttributions": [
            {
              "displayName": "LuLu Saleh",
              "uri": "https://maps.google.com/maps/contrib/110949073325427717036",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWRH3HtCd20T_g0Z80LYdSDm-O6NIU7otAIEWMN1W6NEO3wndWjJQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/photos/AdCG2DO9abIUCqrGE_7L0OSyYhWnKUwH8Xy2UX4qOpa2WWXvGSi9fTKkVLutBWc65HTzedqdRoXSal9xkugI9-sx77VwszBS9cD7OruWR7Qm0lpU-S0K_jNdCpKvgvqWdTZVWkefez4nIVZs7WmwgZPz10Z89YWc-juXd8BG",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Chrissy p",
              "uri": "https://maps.google.com/maps/contrib/110411695926213199361",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWzgUPmfaHj8yjft5ddsODOpNwZWc3EhmhzQCRP28SuzkdAki6Y=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/photos/AdCG2DPR_XYzmeNWv8ptKbNrZ01XUzlQ097qTjqrBFdx05Fmhj_wbqntpn2CnA1dWGB9dBjDfCkvs1vk1DfpR5xwYsqFEoMLe32e32XhwGdI--Z5muBBp0VABu6UD1NzQibtOCbU7Mf7MTkz9KyOc1wTTY6L6aF_UXzNcQR1",
          "widthPx": 4000,
          "heightPx": 3000,
          "authorAttributions": [
            {
              "displayName": "Smevin Bravis",
              "uri": "https://maps.google.com/maps/contrib/103436111892970840349",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWvpJlzV3GNMZH5NpUNJ0uIbLLnnccv9_zEJaH5NHyWj64_3kyE=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/photos/AdCG2DMJAgPCSlgPirP_TB8o9aFN1ooPisSJYFQqB_lJn1DoRGRgq_Zi0ycNkmKH5xLAl5cWDaDHfcf3LaF1dORTwfOd1-WhmUQ1DfJJnSHJwCgKPMSUNy1ccJSPrRuSiG3ayQI2Q16FSrkXwuT3uHAah_tAJEa9O2FT7v_n",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Raymond Soleimani",
              "uri": "https://maps.google.com/maps/contrib/106928131875790639389",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVVpe9eYGDDjgZ1P-TyXGwL8y6fkYCg9wSQSeBM0Fr5Jan_BYpuZg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/photos/AdCG2DNsA4JCDT-uDtYQJtkW6JRsuZnGIYbEIA4o1DCIOqXhd4q6v0B048pCtK6ncYXsBrXWh_OB_BcsoRxJD27lXqyOnelD5r-u40d6u5-6hV_IDPZV3NnbFyPjnSnSQoKv_xEiHvhapOuc6so-hJgj-lkpWw7ezX-h0dil",
          "widthPx": 3072,
          "heightPx": 4080,
          "authorAttributions": [
            {
              "displayName": "Rodney O Chadderton",
              "uri": "https://maps.google.com/maps/contrib/102742728325663545154",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUdpCu-_dZrqeVmpqr_x5ZLpvXR2KUq355qQE-PrIG-7507WXM6bQ=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "liveMusic": False,
      "menuForChildren": False,
      "servesCocktails": True,
      "servesDessert": True,
      "servesCoffee": True,
      "goodForChildren": True,
      "allowsDogs": False,
      "restroom": True,
      "goodForGroups": True,
      "goodForWatchingSports": False,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "parkingOptions": {
        "freeParkingLot": False,
        "paidParkingLot": True,
        "freeStreetParking": False,
        "valetParking": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleRestroom": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Mexican restaurant with a rooftop bar, serving tacos, tequila and mezcal, plus views of the city.",
          "languageCode": "en-US"
        },
        "description": {
          "text": "Trendy Mexican restaurant in Downtown Los Angeles' Arts District with a rooftop bar and city views.\nThe menu features small plates and vegan options. People like the guacamole, ceviche de betabel, mushroom tacos, and carne asada tacos, as well as the cocktails.\nThe space has a funky atmosphere with fun music, and is good for kids. There can be a wait; reservations are recommended for dinner. Reviews say the staff is attentive and accommodating.\nCustomers typically spend $50–100.",
          "languageCode": "en-US"
        },
        "references": {
          "reviews": [
            {
              "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/reviews/ChZDSUhNMG9nS0VJQ0FnSUNKblp6WVpREAE",
              "relativePublishTimeDescription": "a year ago",
              "rating": 3,
              "text": {
                "text": "Atmosphere was the highlight! Rooftop bar with fun music and summer vibes. Portion to price ratio was a bit off in my opinion, and the taste was fine but didn't excite us. Waiter/bussers approached us every several minutes and seemed a bit unorganized",
                "languageCode": "en"
              },
              "originalText": {
                "text": "Atmosphere was the highlight! Rooftop bar with fun music and summer vibes. Portion to price ratio was a bit off in my opinion, and the taste was fine but didn't excite us. Waiter/bussers approached us every several minutes and seemed a bit unorganized",
                "languageCode": "en"
              },
              "authorAttribution": {
                "displayName": "Lior Chatow",
                "uri": "https://www.google.com/maps/contrib/111589464907759888748/reviews",
                "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUqnYOGAvEPyyw3Lg9Z93rZC2Ytnezu0MpXu6GN3bNFLHk_0R3zZQ=s128-c0x00000000-cc-rp-mo-ba4"
              },
              "publishTime": "2023-07-03T01:10:58.143298Z"
            },
            {
              "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/reviews/ChZDSUhNMG9nS0VJQ0FnSUNKeXJ6MkRnEAE",
              "relativePublishTimeDescription": "a year ago",
              "rating": 4,
              "text": {
                "text": "Wait staff and host staff were tremendously friendly. Atmosphere is funky, eclectic,\ncultural, and chic. Food comes very quickly, left a bit to be desired. The cauliflower was the best thing we had, when I anticipated it being the tacos.",
                "languageCode": "en"
              },
              "originalText": {
                "text": "Wait staff and host staff were tremendously friendly. Atmosphere is funky, eclectic,\ncultural, and chic. Food comes very quickly, left a bit to be desired. The cauliflower was the best thing we had, when I anticipated it being the tacos.",
                "languageCode": "en"
              },
              "authorAttribution": {
                "displayName": "Damon King",
                "uri": "https://www.google.com/maps/contrib/107083752284438479225/reviews",
                "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocIy5zInNYbVpZHM_1duz3Nk703R-X1pV90fDu8zzKHyn62U3A=s128-c0x00000000-cc-rp-mo-ba2"
              },
              "publishTime": "2023-06-24T19:43:02.079426Z"
            },
            {
              "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/reviews/ChZDSUhNMG9nS0VJQ0FnSUR4dmV6bURREAE",
              "relativePublishTimeDescription": "a year ago",
              "rating": 4,
              "text": {
                "text": "The food is unusual, inventive, and tasty. The homemade chips are fabulous but the guacamole is too smooth for me. The service was attentive, up beat, and knowledgeable, which is useful here because the menu is not translated and many of the ingredients are not ones one finds in a regular Mexican restaurant. The size of the dishes is a bit small but not absurd. The rooftop setting is both attractive and very Urban.\nNow to why the restaurant was not ready to even higher. The reservation process. I wanted to let the restaurant know that we were going to be four people, not three even though I assumed that the table would be the same. There is no telephone number to call as the one listed gives a message that it is not monitored. There is a suggestion that one go to the website of Resi but there really was no help there either. Luckily, the service at the restaurant was as welcoming and helpful as the reservation process was complicated and off-putting",
                "languageCode": "en"
              },
              "originalText": {
                "text": "The food is unusual, inventive, and tasty. The homemade chips are fabulous but the guacamole is too smooth for me. The service was attentive, up beat, and knowledgeable, which is useful here because the menu is not translated and many of the ingredients are not ones one finds in a regular Mexican restaurant. The size of the dishes is a bit small but not absurd. The rooftop setting is both attractive and very Urban.\nNow to why the restaurant was not ready to even higher. The reservation process. I wanted to let the restaurant know that we were going to be four people, not three even though I assumed that the table would be the same. There is no telephone number to call as the one listed gives a message that it is not monitored. There is a suggestion that one go to the website of Resi but there really was no help there either. Luckily, the service at the restaurant was as welcoming and helpful as the reservation process was complicated and off-putting",
                "languageCode": "en"
              },
              "authorAttribution": {
                "displayName": "Andrew Rubin",
                "uri": "https://www.google.com/maps/contrib/117711869128332845470/reviews",
                "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWCm7LB8vUl0vgWUTw3ZSdOUm_C3Oa_XapIZznBxHHyj8__2k7I=s128-c0x00000000-cc-rp-mo-ba3"
              },
              "publishTime": "2023-06-14T02:01:45.051124Z"
            },
            {
              "name": "places/ChIJOaaU_MbHwoARcKYAojw0-3U/reviews/ChdDSUhNMG9nS0VJQ0FnSURPeWNidTlBRRAB",
              "relativePublishTimeDescription": "2 years ago",
              "rating": 5,
              "text": {
                "text": "Loved our rooftop experience! Summer is the Perfect time to sit at the bar to enjoy yummy bites,\nGorgeous drinks and a lively ambience. Service was great and the staff was super accommodating to get us seated in a spot that we asked for. We parked in a lot nearby and all in all it was a great evening out.",
                "languageCode": "en"
              },
              "originalText": {
                "text": "Loved our rooftop experience! Summer is the Perfect time to sit at the bar to enjoy yummy bites,\nGorgeous drinks and a lively ambience. Service was great and the staff was super accommodating to get us seated in a spot that we asked for. We parked in a lot nearby and all in all it was a great evening out.",
                "languageCode": "en"
              },
              "authorAttribution": {
                "displayName": "Lisa Munoz",
                "uri": "https://www.google.com/maps/contrib/107719523641270019893/reviews",
                "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjW8aVzAuJzsAoWCYd2qopI6kN8MJzXVKLaf6ilJDSW4q_P4aBz8MQ=s128-c0x00000000-cc-rp-mo-ba5"
              },
              "publishTime": "2022-07-08T14:31:38.524925Z"
            }
          ]
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJ0yp3zD7GwoARoWoWU4X2g8g",
            "placeId": "ChIJ0yp3zD7GwoARoWoWU4X2g8g",
            "displayName": {
              "text": "Hauser & Wirth",
              "languageCode": "en"
            },
            "types": [
              "art_gallery",
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 94.3387,
            "travelDistanceMeters": 92.35548
          },
          {
            "name": "places/ChIJ_4LzODnGwoARzVvdMH7SFXQ",
            "placeId": "ChIJ_4LzODnGwoARzVvdMH7SFXQ",
            "displayName": {
              "text": "Wurstküche",
              "languageCode": "en"
            },
            "types": [
              "bar",
              "establishment",
              "food",
              "point_of_interest",
              "restaurant"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 33.25972,
            "travelDistanceMeters": 42.207176
          },
          {
            "name": "places/ChIJx7yfNjnGwoARZWc_tonTYBs",
            "placeId": "ChIJx7yfNjnGwoARZWc_tonTYBs",
            "displayName": {
              "text": "Salt & Straw",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "food",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 41.82043,
            "travelDistanceMeters": 37.204353
          },
          {
            "name": "places/ChIJW8K3QDnGwoARQCzF7zQtpZo",
            "placeId": "ChIJW8K3QDnGwoARQCzF7zQtpZo",
            "displayName": {
              "text": "The Pie Hole",
              "languageCode": "en"
            },
            "types": [
              "bakery",
              "cafe",
              "establishment",
              "food",
              "point_of_interest",
              "restaurant",
              "store"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 65.58213,
            "travelDistanceMeters": 100.44708
          },
          {
            "name": "places/ChIJMSC0vTnGwoAREzlQ-kYSOTs",
            "placeId": "ChIJMSC0vTnGwoAREzlQ-kYSOTs",
            "displayName": {
              "text": "Little Tokyo Market Place",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "food",
              "grocery_or_supermarket",
              "point_of_interest",
              "store",
              "supermarket"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 297.96158,
            "travelDistanceMeters": 258.25552
          }
        ],
        "areas": [
          {
            "name": "places/ChIJP4e1VDrGwoAR4IoQrY1TbdQ",
            "placeId": "ChIJP4e1VDrGwoAR4IoQrY1TbdQ",
            "displayName": {
              "text": "Arts District",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJd3xCWU_GwoARBP7kXLY2T_E",
            "placeId": "ChIJd3xCWU_GwoARBP7kXLY2T_E",
            "displayName": {
              "text": "Little Tokyo",
              "languageCode": "en"
            },
            "containment": "OUTSKIRTS"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJue588rfHwoARKIjvFOu2etU",
      "id": "ChIJue588rfHwoARKIjvFOu2etU",
      "types": [
        "mexican_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 746-7750",
      "internationalPhoneNumber": "+1 213-746-7750",
      "formattedAddress": "1037 Flower St, Los Angeles, CA 90015, USA",
      "addressComponents": [
        {
          "longText": "1037",
          "shortText": "1037",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "Flower Street",
          "shortText": "Flower St",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90015",
          "shortText": "90015",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "1401",
          "shortText": "1401",
          "types": [
            "postal_code_suffix"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632PVP+FF",
        "compoundCode": "2PVP+FF Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.043659999999996,
        "longitude": -118.263863
      },
      "viewport": {
        "low": {
          "latitude": 34.0422319197085,
          "longitude": -118.26508228029148
        },
        "high": {
          "latitude": 34.0449298802915,
          "longitude": -118.2623843197085
        }
      },
      "rating": 4.3,
      "googleMapsUri": "https://maps.google.com/?cid=15382808598022162472",
      "websiteUri": "http://www.elcholo.com/",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 1,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 5,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 21,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 11:00 AM – 9:00 PM",
          "Tuesday: 11:00 AM – 9:00 PM",
          "Wednesday: 11:00 AM – 9:00 PM",
          "Thursday: 11:00 AM – 9:00 PM",
          "Friday: 11:00 AM – 9:00 PM",
          "Saturday: 11:00 AM – 9:00 PM",
          "Sunday: 11:00 AM – 9:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e1037 Flower St\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90015-1401\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_MODERATE",
      "userRatingCount": 2111,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "El Cholo",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "reservable": True,
      "servesBreakfast": True,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": True,
      "servesWine": True,
      "servesBrunch": True,
      "servesVegetarianFood": True,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 11:00 AM – 9:00 PM",
          "Tuesday: 11:00 AM – 9:00 PM",
          "Wednesday: 11:00 AM – 9:00 PM",
          "Thursday: 11:00 AM – 9:00 PM",
          "Friday: 11:00 AM – 9:00 PM",
          "Saturday: 11:00 AM – 9:00 PM",
          "Sunday: 11:00 AM – 9:00 PM"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "1037 Flower St, Los Angeles",
      "editorialSummary": {
        "text": "Local Mexican chain serving classic dishes & margaritas in a traditional setting since the 1920s.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/reviews/ChdDSUhNMG9nS0VJQ0FnSUNINXZPRnBRRRAB",
          "relativePublishTimeDescription": "a month ago",
          "rating": 1,
          "text": {
            "text": "So sad to see an iconic restaurant go downhill.... we ordered the chichen enchiladas, and the chicken was so dry, the carne asada quesadillas were super greasy, and the steak tasted gamey. The margaritas were overpowered by the mixer, at $16.00 per drink, we were expecting better drinks.\n\nThe patio area was great and our server was  nice even mentioned to give us a different dish but it was already too late.\n\nMaybe it was a slow day and the food was just sitting, unfortunately the food is not fresh.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "So sad to see an iconic restaurant go downhill.... we ordered the chichen enchiladas, and the chicken was so dry, the carne asada quesadillas were super greasy, and the steak tasted gamey. The margaritas were overpowered by the mixer, at $16.00 per drink, we were expecting better drinks.\n\nThe patio area was great and our server was  nice even mentioned to give us a different dish but it was already too late.\n\nMaybe it was a slow day and the food was just sitting, unfortunately the food is not fresh.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Waldin Gonzalez Golden Bear",
            "uri": "https://www.google.com/maps/contrib/110519467267563863868/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjX37DZJCMybMgVKBaTO_VYjektbcsuRSyLwNUwRmYWs475gkui8=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-09-04T14:08:33.580731Z"
        },
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/reviews/ChZDSUhNMG9nS0VJQ0FnSUNia2FhMUpREAE",
          "relativePublishTimeDescription": "2 months ago",
          "rating": 5,
          "text": {
            "text": "There's a reason its been around over 100 years! A pitcher of Margaritas. Carne Asada street tacos, Mariscos enchiladas, Blue Corn chicken enchiladas. Of course, the table side guacamole was great!",
            "languageCode": "en"
          },
          "originalText": {
            "text": "There's a reason its been around over 100 years! A pitcher of Margaritas. Carne Asada street tacos, Mariscos enchiladas, Blue Corn chicken enchiladas. Of course, the table side guacamole was great!",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Martin Courtney (Openplzdds)",
            "uri": "https://www.google.com/maps/contrib/108018811120628226831/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXstLbLArcfdaJOgtm-YAgJUrchmcbaJ_rVDj7GKS9lvBOS5uPv=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-07-28T04:57:43.739312Z"
        },
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/reviews/ChZDSUhNMG9nS0VJQ0FnSURIa3VUSGZREAE",
          "relativePublishTimeDescription": "a month ago",
          "rating": 3,
          "text": {
            "text": "Glad I checked this place out. I won't be coming back though. The restaurant has a great atmosphere. The best part are the drinks. The food is subpar. If you are at a hotel nearby, just eat at the hotel. I had the fish tacos. They were not flavorful. So sad to see flavorless tacos in LA.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Glad I checked this place out. I won't be coming back though. The restaurant has a great atmosphere. The best part are the drinks. The food is subpar. If you are at a hotel nearby, just eat at the hotel. I had the fish tacos. They were not flavorful. So sad to see flavorless tacos in LA.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Helena Aredo",
            "uri": "https://www.google.com/maps/contrib/109586606655337868265/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjX24iffCI1yCEDjMLF_iZOgzXk8aU0gs0cGInwyUnNbyccR8tqP=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-09-14T05:17:13.793568Z"
        },
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/reviews/ChZDSUhNMG9nS0VJQ0FnSUQ3c2ZtZVVBEAE",
          "relativePublishTimeDescription": "a month ago",
          "rating": 5,
          "text": {
            "text": "The service was great and food came in fast. My  enchiladas were cooked to perfection, delicious and generously filled. The sides that came with the plate, were also great and the house margaritas were right to the point. I strongly recommend dining there.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "The service was great and food came in fast. My  enchiladas were cooked to perfection, delicious and generously filled. The sides that came with the plate, were also great and the house margaritas were right to the point. I strongly recommend dining there.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Benjamin Borges",
            "uri": "https://www.google.com/maps/contrib/104233355007134735412/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocKt5XRv2Lej3Tcoh_Ma4xUIM2ZWL2mDunlcPPWCK1YLumL29w=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-08-25T11:07:26.404057Z"
        },
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/reviews/ChZDSUhNMG9nS0VJQ0FnSUR0LXRUcEtREAE",
          "relativePublishTimeDescription": "8 months ago",
          "rating": 2,
          "text": {
            "text": "Major disappointment 😔 food was simply bad; lettuce and avocado did look/taste fresh. Crab tacos were horrible.  The two stars is for the very good service.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Major disappointment 😔 food was simply bad; lettuce and avocado did look/taste fresh. Crab tacos were horrible.  The two stars is for the very good service.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Gatillero V.",
            "uri": "https://www.google.com/maps/contrib/116477957527011189025/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVjaciwylsK-kdawmk-VFTnDF7Kcas3AK9t1nOOB7KBKKW3yj9uUg=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-02-04T02:32:16.717428Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/photos/AdCG2DM6GxJwuSbgceXdJYcVZ2u6VN2VH1JpkIGVIypTa_pCwFl0PGyJwgIGhYbhAUCqejuDPUQjcKPleuC8Pm6LW3mmQETN248QNrHadduICnQSqEoWDA0AupEJ7iWxfYCYzFZza7evAg_ZcRXU63tRArWbTtuyNgND0z5K",
          "widthPx": 1038,
          "heightPx": 584,
          "authorAttributions": [
            {
              "displayName": "Catherine A. Montgomery",
              "uri": "https://maps.google.com/maps/contrib/101875998493251463525",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVt4c3uH37R21Ka-MtuKzcbQZQPvFYzD1DgyXujuVmUIg9tyfq30A=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/photos/AdCG2DPZqfeqfNIfgiKchCktpSZCsSRv5MqDPWp0MX7xHApn26ax9l71651FTW4tFC68dib16Xqhc83W6OI8EY8Pc5Hf-SIm4p1c8FNxr_kvPltPK6o0sn4gguSwcLrR1DQIW87HhYqz6uWqqTHjDi1qpBQtOw5cAklzzRJu",
          "widthPx": 4032,
          "heightPx": 2268,
          "authorAttributions": [
            {
              "displayName": "Ron Khoury",
              "uri": "https://maps.google.com/maps/contrib/114592238794697604522",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWEtQZzBOTXHDbyWNZMeVcbsFGKcOCe_UhG2E1NUxbAmwStDHp7=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/photos/AdCG2DPM0e7Xjo0yA0J_zGFxVnzi6UlydYZKVU2zQB_mje_QHqTcnMlZtcL1P4OBggURZgIXJVU5TWrJXD2F2-VGPXmQaxpswJ5Yj7r8fRajcwO2R21ZndJguyP_c2HGVkQaynjTYqIVo8QI1vkbgYklIkCjBnmSw1WhTf8F",
          "widthPx": 4160,
          "heightPx": 2080,
          "authorAttributions": [
            {
              "displayName": "Raffaello Allemanini",
              "uri": "https://maps.google.com/maps/contrib/109135480315820746078",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXCuxQS0zVZAbWuX3TAB4C3SWJuFVpP2lq0BVlkiufj1PyqkeJDuQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/photos/AdCG2DOrpNKlsrCIZqrCa2v65hWbvHM5wEQPgMCgdCF6w16Aq97-sEcUXn6XHtl2_uZQAX5m73rHXqjKTGiADCQyEY16akQeSDN7KxOOV2TnumI0gnDTpAq2G0A9kcwxG_NCXZiDInyBzGvQohjl94-b36pwkz5GjdMUy--7",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "D I",
              "uri": "https://maps.google.com/maps/contrib/106599822797158501188",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU-71VCzhEuWxmthe_IHEMailgmhANZn2P1VBR6t-je4TpNdmIF=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/photos/AdCG2DP7TBMjXtbVMmyWJnVuoh__oAVRxRgk_I65UZQJqTGLnOyeCbWTNlzUzKoeVq-kUunJrLUalxWmiKLzypWMDk2yOzxBGOlNDg9g1VLMc8LM1DTzVISQX8grws5wtDXifpqQRrtRzTbO9zpooslu17nrQnhlAT-6qb9b",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "P. Tran",
              "uri": "https://maps.google.com/maps/contrib/115956668707503240521",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXnKIvyj7qwZuCdnuB-Xn7hWsl5cFl5Ygsj9T3GEGLbdJq9XlEH-w=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/photos/AdCG2DPqdJw-XeexkE2QzFenf9QX0vMvVhUwRtc2AahDFnHIDmBlw0O7hdoVye0wP1X7FqOZ-LEbTBRPkco9oZtKbbueCYfadjp3aEhOKFuFCWFLI_xXMhplEo46inUyZ7q1_XsuMlDKPTI7TLrgIDktHeHG24fb1vXcxC7Z",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Anthony Formento",
              "uri": "https://maps.google.com/maps/contrib/104056828806830357460",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUIhR03XBr8Y37BtA4E48HDjux6SnR-BbeO3lpCIPAoVvTTdQVAMw=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/photos/AdCG2DPaMZMN3fV6UoZtWHB6yJ_T1zTFCtFwyyzEsW4T6_5EugDxDr3jV7fSfQN0gn07cfOUijcYL3JoshdBhAIIfKa3JO-PZAmyk4AQdc84vYydEpH6a24nZ9_lxGsnE0E6ApLP7D_TfeIPjSVC9jTsP28AvPX9JlVl-Ntn",
          "widthPx": 4800,
          "heightPx": 3600,
          "authorAttributions": [
            {
              "displayName": "Dan Roman",
              "uri": "https://maps.google.com/maps/contrib/107096834497182198333",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUbb1FLhR4I93Ai-ITuiTZHqi_6TtOBSYg42aX6Ydioohp49JNd=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/photos/AdCG2DM7kY4Rn9MXLfpDLpSQu61o-mMHTVHiqs_YVUKEutK2vJzWCtRCc14XP5qzalLc4cqmeD-5aPqcGfuOBBEmm2tGlBEntrF2r6kK-KBZjmtG-72uqsUdBCN_WhEhu1iPtJuFA4XNlrC9b4CAT4mzNjEqy1grS2EGiZdM",
          "widthPx": 4032,
          "heightPx": 2268,
          "authorAttributions": [
            {
              "displayName": "Chuck Weissman",
              "uri": "https://maps.google.com/maps/contrib/112341849488252443788",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU8zeAJ9QBJ9Q2jgoSCfqjcOa3IgmvYSEG_NNbt3RxIwfnsCDdKFA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/photos/AdCG2DMfCglI8d0K7oG_BaYiivyWKs-CDqkY0jDl-FbXbhV1Sir5nHxiRSvoYr5KlA_wspTcd5oFwmIvS-iiggYUGEPE2-en2etJpxKjREmQpZwCkUzkhsASBL-vmFaS8Cf5Y9plBxa8hmOFtMNLD53g6kfEDHa9NfaaLdSi",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Greg Garrett",
              "uri": "https://maps.google.com/maps/contrib/112472840641120455222",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU7QvURxzda7tbPoQdFeYd8elvnGCALAT4TXVXWoDQNcVA9vezKXQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJue588rfHwoARKIjvFOu2etU/photos/AdCG2DNgAX3fs45NmMM_eaSKWn8bxcoxuCmrQ19Ra91AbSJkoqK1uoe3T57VRQBCHgT8TsxHma8BAp6Z1pXSyPZaP2czbG7p14Ov7b5DAU_2Mlk1CnqMFxm8PmWeeMeiv1HiBIBTtS-XgGdusUk-KSgTwDHpYLZrfKDN7Js_",
          "widthPx": 3000,
          "heightPx": 4000,
          "authorAttributions": [
            {
              "displayName": "Bunnylicious",
              "uri": "https://maps.google.com/maps/contrib/117972639207606939476",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUNWntWz5i_yHfA05sMHlWV8ec27LbYMkMCrmWe0xWgm9JC9BnqGA=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "liveMusic": False,
      "menuForChildren": True,
      "servesCocktails": True,
      "servesDessert": True,
      "servesCoffee": True,
      "goodForChildren": True,
      "allowsDogs": False,
      "restroom": True,
      "goodForGroups": True,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "parkingOptions": {
        "paidParkingLot": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleParking": True,
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleRestroom": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Mexican fare including fajitas and enchiladas is served in a long-standing institution with a patio.",
          "languageCode": "en-US"
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJkyrqXbjHwoAR1bJ76zx89B8",
            "placeId": "ChIJkyrqXbjHwoAR1bJ76zx89B8",
            "displayName": {
              "text": "Crypto.com Arena",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest",
              "stadium"
            ],
            "straightLineDistanceMeters": 334.1258,
            "travelDistanceMeters": 292.02072
          },
          {
            "name": "places/ChIJuYQ2SbjHwoARC4aaAnD6xp0",
            "placeId": "ChIJuYQ2SbjHwoARC4aaAnD6xp0",
            "displayName": {
              "text": "L.A. Live",
              "languageCode": "en"
            },
            "types": [
              "bar",
              "establishment",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 203.92688,
            "travelDistanceMeters": 274.103
          },
          {
            "name": "places/ChIJ9WyHlLfHwoARc_0kqEVS0w4",
            "placeId": "ChIJ9WyHlLfHwoARc_0kqEVS0w4",
            "displayName": {
              "text": "Caña Rum Bar",
              "languageCode": "en"
            },
            "types": [
              "bar",
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 74.99568,
            "travelDistanceMeters": 64.255264
          },
          {
            "name": "places/ChIJG5wBgrfHwoAR9hEdmF4WsH4",
            "placeId": "ChIJG5wBgrfHwoAR9hEdmF4WsH4",
            "displayName": {
              "text": "GRAMMY Museum L.A. Live",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "museum",
              "point_of_interest",
              "tourist_attraction"
            ],
            "straightLineDistanceMeters": 151.04532,
            "travelDistanceMeters": 307.49252
          },
          {
            "name": "places/ChIJbTyah7fHwoARGltyvZT7uC4",
            "placeId": "ChIJbTyah7fHwoARGltyvZT7uC4",
            "displayName": {
              "text": "E-Central Downtown Los Angeles Hotel",
              "languageCode": "en"
            },
            "types": [
              "bar",
              "establishment",
              "food",
              "lodging",
              "point_of_interest",
              "restaurant"
            ],
            "straightLineDistanceMeters": 94.294174,
            "travelDistanceMeters": 338.02115
          }
        ],
        "areas": [
          {
            "name": "places/ChIJN28nbMjHwoAR0mBlu0518tE",
            "placeId": "ChIJN28nbMjHwoAR0mBlu0518tE",
            "displayName": {
              "text": "South Park",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA",
      "id": "ChIJf5HW3w7HwoAR0EEIlkAD5vA",
      "types": [
        "mexican_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 270-0178",
      "internationalPhoneNumber": "+1 213-270-0178",
      "formattedAddress": "2132 E 7th Pl, Los Angeles, CA 90021, USA",
      "addressComponents": [
        {
          "longText": "2132",
          "shortText": "2132",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "East 7th Place",
          "shortText": "E 7th Pl",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90021",
          "shortText": "90021",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632QMC+9C",
        "compoundCode": "2QMC+9C Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.033466,
        "longitude": -118.2289512
      },
      "viewport": {
        "low": {
          "latitude": 34.0321577197085,
          "longitude": -118.23031163029147
        },
        "high": {
          "latitude": 34.0348556802915,
          "longitude": -118.22761366970849
        }
      },
      "rating": 4.5,
      "googleMapsUri": "https://maps.google.com/?cid=17358565389676069328",
      "websiteUri": "http://www.damiandtla.com/",
      "regularOpeningHours": {
        "openNow": False,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 17,
              "minute": 30
            },
            "close": {
              "day": 1,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 17,
              "minute": 30
            },
            "close": {
              "day": 3,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 17,
              "minute": 30
            },
            "close": {
              "day": 4,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 17,
              "minute": 30
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 5:30 – 9:00 PM",
          "Tuesday: Closed",
          "Wednesday: 5:30 – 9:00 PM",
          "Thursday: 5:30 – 9:00 PM",
          "Friday: 5:30 – 10:00 PM",
          "Saturday: 5:00 – 10:00 PM",
          "Sunday: 5:00 – 9:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e2132 E 7th Pl\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90021\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "userRatingCount": 470,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Damian",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "delivery": False,
      "dineIn": True,
      "curbsidePickup": False,
      "reservable": True,
      "servesBreakfast": False,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": True,
      "servesWine": True,
      "servesBrunch": True,
      "servesVegetarianFood": True,
      "currentOpeningHours": {
        "openNow": False,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 17,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 17,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 17,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 17,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 5:30 – 9:00 PM",
          "Tuesday: Closed",
          "Wednesday: 5:30 – 9:00 PM",
          "Thursday: 5:30 – 9:00 PM",
          "Friday: 5:30 – 10:00 PM",
          "Saturday: 5:00 – 10:00 PM",
          "Sunday: 5:00 – 9:00 PM"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "2132 E 7th Pl, Los Angeles",
      "editorialSummary": {
        "text": "Polished eatery making Mexican dishes & desserts with locally sourced ingredients, plus cocktails.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/reviews/ChdDSUhNMG9nS0VJQ0FnSURub1lfUG9BRRAB",
          "relativePublishTimeDescription": "a week ago",
          "rating": 5,
          "text": {
            "text": "The back patio is an outdoor garden setting with nice trees and foliage. The mezcal Margaritas hit the spot.  Our server was super attentive and the food was top notch.  I can't explain how good the duck is.  It was a perfectly flavored carnitas of duck.  It was big too. Plenty of food for two.  Just insanely flavorful I'm good.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "The back patio is an outdoor garden setting with nice trees and foliage. The mezcal Margaritas hit the spot.  Our server was super attentive and the food was top notch.  I can't explain how good the duck is.  It was a perfectly flavored carnitas of duck.  It was big too. Plenty of food for two.  Just insanely flavorful I'm good.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Stuart Sayre",
            "uri": "https://www.google.com/maps/contrib/111378788308477496190/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVVxU56JlW5npb5M3G1Kh4ybd8nUg7_SZrVkVNBkfrTtGCp8Pmj=s128-c0x00000000-cc-rp-mo-ba3"
          },
          "publishTime": "2024-10-06T18:01:57.050715Z"
        },
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/reviews/ChZDSUhNMG9nS0VJQ0FnSUNuZzdlOGVnEAE",
          "relativePublishTimeDescription": "2 weeks ago",
          "rating": 5,
          "text": {
            "text": "Excellent service, delicious food, beautiful wines 🍷 I had a lovely solo dinner here. I enjoyed tasting a variety of items on the menu and chatting with the wait staff. My favorite dishes were the salmon tostada and the hibiscus meringue dessert.\n\nFor wine lovers, try their blend made just for the restaurant.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Excellent service, delicious food, beautiful wines 🍷 I had a lovely solo dinner here. I enjoyed tasting a variety of items on the menu and chatting with the wait staff. My favorite dishes were the salmon tostada and the hibiscus meringue dessert.\n\nFor wine lovers, try their blend made just for the restaurant.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Ashley Stewart",
            "uri": "https://www.google.com/maps/contrib/101517350774753933981/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWoM4iO81N3-a3lmt9W7Pnw17bZe00TL1sFCCwBvfNpYAo27BN2=s128-c0x00000000-cc-rp-mo-ba3"
          },
          "publishTime": "2024-09-29T06:00:16.193170Z"
        },
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/reviews/ChdDSUhNMG9nS0VJQ0FnSUNMM0pIODFBRRAB",
          "relativePublishTimeDescription": "4 months ago",
          "rating": 4,
          "text": {
            "text": "Amazing food with such fresh and refreshing flavors. Pricey but the overall experience is pretty good. What I did not like was the way the food was paced and we ended up losing our hunger because the entrees took so much time to come. We ended taking it back home which was a bummer when you pay so much for the experience.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Amazing food with such fresh and refreshing flavors. Pricey but the overall experience is pretty good. What I did not like was the way the food was paced and we ended up losing our hunger because the entrees took so much time to come. We ended taking it back home which was a bummer when you pay so much for the experience.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Alankar Naik",
            "uri": "https://www.google.com/maps/contrib/104507424451687727474/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWi3dwbL9S3D3lJc_7s-jYHeZqufkehpjkQQYqvOCtrj48XvniC6g=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-06-16T15:04:41.449732Z"
        },
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/reviews/ChdDSUhNMG9nS0VJQ0FnSUNyMVpiUHlRRRAB",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 5,
          "text": {
            "text": "From the moment we entered the restaurant to leaving out the front door after our meal, Damian was an experience.\n\nThe staff were very friendly and kind, and shared their opinions on the menu for us.\n\nMoving onto food, we had the:\n\nCeviche: flavourful lime and tender smooth fish, all the flavours blended so well into it and it was just perfect\nGuacamole: so so so fresh and smooth - probably some of the best guacamole I’ve ever had in my life\nSalmon tostada: first time we’ve had this dish, the salmon was good and nice to try but I wouldn’t get it again just because it wasn’t as wow! As other dishes\nTlayuda: can’t believe that this was so good! The mix of vegetables, beans, and the pork oil amalgamated into a dish of multiple flavours and textures\nPollito al pastor: my favorite dish of the evening, the chicken itself was nice and tender, but where it really outshined was the pineapple butter - when I first tried the butter, it was the texter of super creamy mashed potatoes but the flavour was just out of this world. Highly recommend.\n\nAt the end of the meal, our waitress brought out a small icecream and cake as my girlfriend and I were celebrating our anniversary, it was such a nice gesture from the restaurant and we greatly appreciated it.\n\nDamian felt upscale but unpretentious, an amazing establishment in the arts district and would recommend this restaurant to anyone who wants to try excellent Mexican food.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "From the moment we entered the restaurant to leaving out the front door after our meal, Damian was an experience.\n\nThe staff were very friendly and kind, and shared their opinions on the menu for us.\n\nMoving onto food, we had the:\n\nCeviche: flavourful lime and tender smooth fish, all the flavours blended so well into it and it was just perfect\nGuacamole: so so so fresh and smooth - probably some of the best guacamole I’ve ever had in my life\nSalmon tostada: first time we’ve had this dish, the salmon was good and nice to try but I wouldn’t get it again just because it wasn’t as wow! As other dishes\nTlayuda: can’t believe that this was so good! The mix of vegetables, beans, and the pork oil amalgamated into a dish of multiple flavours and textures\nPollito al pastor: my favorite dish of the evening, the chicken itself was nice and tender, but where it really outshined was the pineapple butter - when I first tried the butter, it was the texter of super creamy mashed potatoes but the flavour was just out of this world. Highly recommend.\n\nAt the end of the meal, our waitress brought out a small icecream and cake as my girlfriend and I were celebrating our anniversary, it was such a nice gesture from the restaurant and we greatly appreciated it.\n\nDamian felt upscale but unpretentious, an amazing establishment in the arts district and would recommend this restaurant to anyone who wants to try excellent Mexican food.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Eric Jin Cheng",
            "uri": "https://www.google.com/maps/contrib/114766275952459832482/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjX5Q0DVKLEqQnZEy8N4p_Ccpdlg-eVYOtyvRqNBLMSU86qMF001=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-07-09T17:46:41.224821Z"
        },
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/reviews/ChdDSUhNMG9nS0VJQ0FnSUNUcHNDUHJBRRAB",
          "relativePublishTimeDescription": "5 months ago",
          "rating": 4,
          "text": {
            "text": "Great place to have dinner. This restaurant special thing is Tostadas, which is not fried. Guacamole dish used herbs toppings that taste so  fresh. They used delicious sauce, especially Caeser Tostadas. This dish had anchovy on the top, so if you like fish smell, you should try  it. The signature dessert is Hibiscus Meringue.\nAll dishes were authentic foods but so priced.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Great place to have dinner. This restaurant special thing is Tostadas, which is not fried. Guacamole dish used herbs toppings that taste so  fresh. They used delicious sauce, especially Caeser Tostadas. This dish had anchovy on the top, so if you like fish smell, you should try  it. The signature dessert is Hibiscus Meringue.\nAll dishes were authentic foods but so priced.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Lauren Lauren",
            "uri": "https://www.google.com/maps/contrib/108860212315285309018/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLXG9sOyklL_pajEAHQ5bEVkD4qycaik2HC5ArblzDlFf1kBVhW=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-05-14T05:38:08.875569Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/photos/AdCG2DNVfGIzhLHfBpSTDKnXLY_7UxZXuilK6GHcoA-S8bzXYhpxwkAZzlkCOeUmO_zxMLDa2s7U3yuWKKrM87ww1ViseShoSqysaRcYyFJ1aO6JXrTfDpVJjDL3AzgtQzbDqMgaUivGhN5AZJCKLHju_JANpNjiwjglyU28",
          "widthPx": 4800,
          "heightPx": 3200,
          "authorAttributions": [
            {
              "displayName": "Rico Revilla",
              "uri": "https://maps.google.com/maps/contrib/108962291928132871435",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXxKVXFB6VGyeKEmmNrgtlIMSaEkMTC-MWPegBLNKdn1WwkS__tDg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/photos/AdCG2DMlCw2qtUwvbG606eKv_hEOSNAeXFCYH-Q6XdmKel6Xi1I6vTgPlw9qpPHAzo_Oucg44NbWngqHIszH2aORK-87VE-469tmOMD7lnRJecA34dZR0AUg8RcO4nzMWCNZ259YZr3aPjgS2BzhcAbwKP0CfQ8m-PJuFCHS",
          "widthPx": 3600,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Damian",
              "uri": "https://maps.google.com/maps/contrib/100848461841415767396",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXu6kQ4r7qh8aqSyABVYZtSBBoC1Ce2w8HbkmbWSzIy74Yyg4Y=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/photos/AdCG2DMiba8pAj_FXipsRvAO2_q1m4_mDGEa0vT164tTA5PQdAbCAe1JyapEWQUZlklQyJ6-snF0Ow6d2e5npFV_r8NjDAWBNif_mTQb8_hy2EUzUTSTYoJeTVqklKv38VjRR3vS1fGM-i1TOHsxsmD_KCyLfIhz9dVwRoh3",
          "widthPx": 4192,
          "heightPx": 2359,
          "authorAttributions": [
            {
              "displayName": "Damian",
              "uri": "https://maps.google.com/maps/contrib/100848461841415767396",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXu6kQ4r7qh8aqSyABVYZtSBBoC1Ce2w8HbkmbWSzIy74Yyg4Y=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/photos/AdCG2DMfEz-iX0ATMhvDYuMZcaQexrOwINO71ox7gL1kFKF1xy8il6EWpS64JdBHnA2sNAXc9NqvbQfpS76R0EiOUGp-QmrMCwBJgkbSXP-JUQFu3hX3oLWiRY4lP0mgLLTI_wlPR90rv5fQCt3vi1e9MLzxgDrYXejYqvYc",
          "widthPx": 4080,
          "heightPx": 3072,
          "authorAttributions": [
            {
              "displayName": "Koushik Roy",
              "uri": "https://maps.google.com/maps/contrib/106673473631174393882",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUFr8j8_FFqXXw9t18Di78Dgju7_xd7JMKZU-rw08hf8zHgqyU0=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/photos/AdCG2DNFwXsYdKSWVS6xcfKBhKRtggVPxsX04wjGkC0Q9WfvmXrbvS4hR4R3WThjEYWeN7rUiIMbRpwvuU52EGeAGWzg-qvNdSmYS9C4pAcu0a6Jp7OzHXqKhaiX3yK4z6L-MXeqvuPNPtcKUOycFhl58vh3VQxvj7S4MRcm",
          "widthPx": 3072,
          "heightPx": 4080,
          "authorAttributions": [
            {
              "displayName": "Jemina Ocampo-Ong",
              "uri": "https://maps.google.com/maps/contrib/104684357806474280334",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUbSF_n6wlIy6jD3-XLyXgcSAer0ec9CuFzKeu0B5j5LruzBb4WbA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/photos/AdCG2DMQ81eHvPmIT98COfdCYpy1wnwMS7-LUIEPMZCmEBHa3waPE-4PuXeL1FDeSD9JWxj-qkrJ16u3JynVW3_tfKJ92XKEGonKRDesflUHugD3owK_4PC97w46a5Ivwv91LcQOQTrik627k3YD5LXPqh9O757_CkXEvQa2",
          "widthPx": 4000,
          "heightPx": 1868,
          "authorAttributions": [
            {
              "displayName": "Ed Hu",
              "uri": "https://maps.google.com/maps/contrib/103951344105373574062",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWFl-rfNFbdgnuvwcrYqns7F-0OLwgaBMU2EszYI5VW7mWKGNgz8Q=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/photos/AdCG2DOVTWs4PhQddFWo0OtlyDABgWFygHq8fiXe1SP-6OX8opLlxOCdd-u9kU_knfZKjpbFDtFcNI2iZBxfURKqj_DP_4qgzjFimLYNMWfsZr8YLnkC-Z57fA49id-I1iLFbUUd_O_mPZElGhrJtdhUOSfP1FZO0o-b2t-9",
          "widthPx": 4080,
          "heightPx": 3072,
          "authorAttributions": [
            {
              "displayName": "Jenna Park",
              "uri": "https://maps.google.com/maps/contrib/101945293537844958960",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWCIbmet2t3f657EGV5-ueE_AQWb0duQKz7YRmWKITkJK5f4DDS=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/photos/AdCG2DNm9ZTFd_7TZoleTR0KCc25k7G-8G0lzfBk0PJlDIdVa5AVTlPrsZlFEgoJ9KSKP3fOk-Nt-vHPoATak4Xzq-HfyF_voclM9GJ1K3k8G7w_mqFJnPLzidDApXkgZdGV9f9ccS9IHQlAMxo39LqlBPkpqqHTNcTl2w39",
          "widthPx": 4032,
          "heightPx": 2268,
          "authorAttributions": [
            {
              "displayName": "Ivy Barrera (ivy99)",
              "uri": "https://maps.google.com/maps/contrib/115448697125444202452",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUH4IaWYQzP8LVexH2v4iOwUqUKUW3GG3t04Y8XYFwR2L1EozxoAA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/photos/AdCG2DPcLFFKzEDcEpRt52upFCeZu2ScgNcvxpfrq48-6JZFshfjB6xlGIXwdtf2Sxil_0nyqG2jIOB-_INk4m9k6P4gDc4eeLnSLai-A_pSdUy8ZG8cG-7qMj-Zx9MjpXy_96LYjZ5lQqJlI06Yt-IrfvyTJ1xC0f6OzexK",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Floriana Martinez",
              "uri": "https://maps.google.com/maps/contrib/106022718164478264328",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVeHN71ZE2b-ybi9Epe7kAKP2G46YZM5LIHVpohP_IyKXUlSRxD=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJf5HW3w7HwoAR0EEIlkAD5vA/photos/AdCG2DOo_QAliX2QRwmVmt9-5wyQxYscoJZK29ff5FvqMBjHxYrhVjf57oT70Ps2P6DYiGpzAiPhOdGb1iBzNRnbv3KDpYflRl2Aa248KTq9rNfyaTahVuPP_wNlYPVo5XrDzIf4vVRmSDAyEJti_FClJf4rFPSxBfvMrkEB",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Bill Sanchez",
              "uri": "https://maps.google.com/maps/contrib/101546662787376177936",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUVav8-Va37Vm57FztaSOJlN_ZZ7_NiJGGByu4kVrfF3UybNM7X=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "liveMusic": False,
      "menuForChildren": False,
      "servesCocktails": True,
      "servesDessert": True,
      "servesCoffee": True,
      "goodForChildren": False,
      "restroom": True,
      "goodForGroups": True,
      "goodForWatchingSports": False,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": False
      },
      "parkingOptions": {
        "freeStreetParking": True,
        "valetParking": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleParking": True,
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleRestroom": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Seasonal, California-inspired Mexican dishes and drink menu served in a trendy space.",
          "languageCode": "en-US"
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJSRvZ1yHGwoARcLrfvc-APl4",
            "placeId": "ChIJSRvZ1yHGwoARcLrfvc-APl4",
            "displayName": {
              "text": "Bestia",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "food",
              "point_of_interest",
              "restaurant"
            ],
            "spatialRelationship": "ACROSS_THE_ROAD",
            "straightLineDistanceMeters": 32.480812,
            "travelDistanceMeters": 26.49078
          },
          {
            "name": "places/ChIJYVMipY7HwoARuFUHGW2WzII",
            "placeId": "ChIJYVMipY7HwoARuFUHGW2WzII",
            "displayName": {
              "text": "Soho Warehouse",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "lodging",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 237.13405,
            "travelDistanceMeters": 260.83563
          },
          {
            "name": "places/ChIJrRWRQ8_HwoARuVtp3s0hobA",
            "placeId": "ChIJrRWRQ8_HwoARuVtp3s0hobA",
            "displayName": {
              "text": "Warner Music Group",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 127.39789,
            "travelDistanceMeters": 172.00362
          },
          {
            "name": "places/ChIJ9WC65yHGwoARQN22YZVcCyk",
            "placeId": "ChIJ9WC65yHGwoARQN22YZVcCyk",
            "displayName": {
              "text": "Bread Lounge",
              "languageCode": "en"
            },
            "types": [
              "bakery",
              "cafe",
              "establishment",
              "food",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 120.6596,
            "travelDistanceMeters": 188.55672
          },
          {
            "name": "places/ChIJx5C3EB_GwoARreind37V4DI",
            "placeId": "ChIJx5C3EB_GwoARreind37V4DI",
            "displayName": {
              "text": "7th Street Bridge",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 203.27367,
            "travelDistanceMeters": 475.81192
          }
        ],
        "areas": [
          {
            "name": "places/ChIJf_9O_SzGwoARtrkWOBLCwII",
            "placeId": "ChIJf_9O_SzGwoARtrkWOBLCwII",
            "displayName": {
              "text": "Fashion District",
              "languageCode": "en"
            },
            "containment": "OUTSKIRTS"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "OUTSKIRTS"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc",
      "id": "ChIJVfNmkUrGwoARPoiVkasCkqc",
      "types": [
        "mexican_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 627-7656",
      "internationalPhoneNumber": "+1 213-627-7656",
      "formattedAddress": "541 S Spring St UNIT 101, Los Angeles, CA 90013, USA",
      "addressComponents": [
        {
          "longText": "UNIT 101",
          "shortText": "UNIT 101",
          "types": [
            "subpremise"
          ],
          "languageCode": "en"
        },
        {
          "longText": "541",
          "shortText": "541",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "South Spring Street",
          "shortText": "S Spring St",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90013",
          "shortText": "90013",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632PWX+JP",
        "compoundCode": "2PWX+JP Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.0465944,
        "longitude": -118.25065279999998
      },
      "viewport": {
        "low": {
          "latitude": 34.045202269708504,
          "longitude": -118.25190208029149
        },
        "high": {
          "latitude": 34.0479002302915,
          "longitude": -118.24920411970851
        }
      },
      "rating": 4.6,
      "googleMapsUri": "https://maps.google.com/?cid=12074716486838880318",
      "websiteUri": "http://www.guisados.co/",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 1,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 1,
              "minute": 30
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 1,
              "minute": 30
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 9:00 AM – 10:00 PM",
          "Tuesday: 9:00 AM – 10:00 PM",
          "Wednesday: 9:00 AM – 10:00 PM",
          "Thursday: 9:00 AM – 10:00 PM",
          "Friday: 9:00 AM – 1:30 AM",
          "Saturday: 9:00 AM – 1:30 AM",
          "Sunday: 9:00 AM – 9:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e541 S Spring St UNIT 101\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90013\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_INEXPENSIVE",
      "userRatingCount": 2184,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Guisados",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "reservable": False,
      "servesBreakfast": True,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": True,
      "servesWine": False,
      "servesBrunch": True,
      "servesVegetarianFood": True,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 6,
              "hour": 1,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 0,
              "hour": 1,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 9:00 AM – 10:00 PM",
          "Tuesday: 9:00 AM – 10:00 PM",
          "Wednesday: 9:00 AM – 10:00 PM",
          "Thursday: 9:00 AM – 10:00 PM",
          "Friday: 9:00 AM – 1:30 AM",
          "Saturday: 9:00 AM – 1:30 AM",
          "Sunday: 9:00 AM – 9:00 PM"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "BROADWAY ARCADE BUILDING, 541 S Spring St UNIT 101, Los Angeles",
      "editorialSummary": {
        "text": "Unpretentious taco spot known for its braised meat & veggie stews atop handmade tortillas.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/reviews/ChZDSUhNMG9nS0VJQ0FnSUNyLV9QQUlnEAE",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 5,
          "text": {
            "text": "This was the first Guisados I visited many years ago so I have fond memories of it. It's not as busy as it was back then but it's still just as good. The consistency in quality regardless of location makes Guisados a reliable place for a great meal. There's basically no taco I don't like from here but I usually go with the two different types of steak tacos and the quesadilla with chorizo. The horchata is great as well. The sampler is a great choice to try a little bit of several different types of tacos and is a good value.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "This was the first Guisados I visited many years ago so I have fond memories of it. It's not as busy as it was back then but it's still just as good. The consistency in quality regardless of location makes Guisados a reliable place for a great meal. There's basically no taco I don't like from here but I usually go with the two different types of steak tacos and the quesadilla with chorizo. The horchata is great as well. The sampler is a great choice to try a little bit of several different types of tacos and is a good value.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Eric Azevedo",
            "uri": "https://www.google.com/maps/contrib/106861128263907029681/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocJH1Qy0O-9N08Scu-R8v4DDm0XcQ2cPC3UzKWle-4WgFMTGEg=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-07-11T16:16:58.847018Z"
        },
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/reviews/ChdDSUhNMG9nS0VJQ0FnSUM3Z3JxX3NBRRAB",
          "relativePublishTimeDescription": "2 months ago",
          "rating": 5,
          "text": {
            "text": "We just left fight night and Eminem concert at BMO Stadium and were so hungry. My friend recommended this place and said they had the best tacos so we decided to try it. Once we got out of the car the smell of urine and homeless people was all around us. Normally that's a deterrent for me, but it is dtla and it was late so not many options.\n\nWalking in you can tell it was filled with customers who just came from a late night event. The staff was very friendly and some didn't really speak English.\n\nI got 2 orders of the taco sampler for me and my bf which included 1 steak picado taco, 1 bistek roja, 1 mole (I switched mine out for 1chuleta since I don't like mole), 1 tinga, 1 cochinita, and 1 chorizo. I also ordered ceviche and sangria. Everything was delicious! The tacos were really good along with the salsa they gave. They are small but filling. The sangria was definitely authentic and the ceviche was just ok, I could have done without that. I was still hungry and then ordered the Camerones tacos which were really good and bigger than the last tacos. I left really full but satisfied. Anytime I am in the area, I a coming back to this spot for cheap tasty tacos.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "We just left fight night and Eminem concert at BMO Stadium and were so hungry. My friend recommended this place and said they had the best tacos so we decided to try it. Once we got out of the car the smell of urine and homeless people was all around us. Normally that's a deterrent for me, but it is dtla and it was late so not many options.\n\nWalking in you can tell it was filled with customers who just came from a late night event. The staff was very friendly and some didn't really speak English.\n\nI got 2 orders of the taco sampler for me and my bf which included 1 steak picado taco, 1 bistek roja, 1 mole (I switched mine out for 1chuleta since I don't like mole), 1 tinga, 1 cochinita, and 1 chorizo. I also ordered ceviche and sangria. Everything was delicious! The tacos were really good along with the salsa they gave. They are small but filling. The sangria was definitely authentic and the ceviche was just ok, I could have done without that. I was still hungry and then ordered the Camerones tacos which were really good and bigger than the last tacos. I left really full but satisfied. Anytime I am in the area, I a coming back to this spot for cheap tasty tacos.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Nicole Steen",
            "uri": "https://www.google.com/maps/contrib/106825767474042559011/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUZ4E-hmCI-U81iSHkYYo29ESXDrMrbF_zK6sbL0quh_eP2OjDF=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-08-13T21:52:42.022093Z"
        },
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/reviews/ChdDSUhNMG9nS0VJQ0FnSUNMNjU2Q3lRRRAB",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 4,
          "text": {
            "text": "The taco sampler at this Mexican restaurant is great because you can choose from six different flavors on the menu and enjoy a variety of flavors. The portions are just right. I also enjoy it with beer. It's really delicious.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "The taco sampler at this Mexican restaurant is great because you can choose from six different flavors on the menu and enjoy a variety of flavors. The portions are just right. I also enjoy it with beer. It's really delicious.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "DAISUKE OKAMOTO (OKAINA IMAGE)",
            "uri": "https://www.google.com/maps/contrib/111301496954922241173/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjV34YFRQhuF_lRpG0IRFvNG81Fc6Q8lufJXazrHOh6eeFtWIlUP=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-06-23T07:51:26.057483Z"
        },
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/reviews/ChZDSUhNMG9nS0VJQ0FnSUNId0t2MVpBEAE",
          "relativePublishTimeDescription": "a month ago",
          "rating": 5,
          "text": {
            "text": "This is a mandatory stop whenever I come to the LA jewelry mart! The chorizo quesadillas are sinfully delicious 😋 I'm glad I live 1100 miles away because I would not be able to control my cravings if I lived closer.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "This is a mandatory stop whenever I come to the LA jewelry mart! The chorizo quesadillas are sinfully delicious 😋 I'm glad I live 1100 miles away because I would not be able to control my cravings if I lived closer.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Nina B",
            "uri": "https://www.google.com/maps/contrib/113800956174632129740/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWc4-rcmFGHpqbfoWriFjNJ90TskS-YlikjbZ-UYm7nK0SfU4vibA=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-09-03T18:30:36.854717Z"
        },
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/reviews/ChdDSUhNMG9nS0VJQ0FnSURMZ1kyUW9BRRAB",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 5,
          "text": {
            "text": "My husband introduced me to this spot. It’s perfect for breakfast, lunch, dinner and as a late night option on weekends.\nTheir breakfast tacos are bomb, and come with sausage, bacon, cheese and eggs.\nTortillas are handmade ✅\nMy kid gets their quesadilla with cheese only. It’s a fresh cheese that has a wonderful milky taste. I was surprised they carry tamales and tostadas topped with ceviche cause my husband always get their tacos.\nThe vibe is friendly and casual, and they have a bunch of art work by local artists on their walls.\nEasy to order food to go, and they have plenty of seating inside and outside. Everyone working there was super nice! I want to come back on a hungry day to try their breakfast burrito.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "My husband introduced me to this spot. It’s perfect for breakfast, lunch, dinner and as a late night option on weekends.\nTheir breakfast tacos are bomb, and come with sausage, bacon, cheese and eggs.\nTortillas are handmade ✅\nMy kid gets their quesadilla with cheese only. It’s a fresh cheese that has a wonderful milky taste. I was surprised they carry tamales and tostadas topped with ceviche cause my husband always get their tacos.\nThe vibe is friendly and casual, and they have a bunch of art work by local artists on their walls.\nEasy to order food to go, and they have plenty of seating inside and outside. Everyone working there was super nice! I want to come back on a hungry day to try their breakfast burrito.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Jenae Lien",
            "uri": "https://www.google.com/maps/contrib/106054869305142744230/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVoJYypztcBd9NdGVMNGK7lVD1dHhUSKqfg6F7wi_Nas8owE1WDLg=s128-c0x00000000-cc-rp-mo-ba7"
          },
          "publishTime": "2024-06-28T05:59:46.875194Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/photos/AdCG2DNDbTEkrGCWMlaExA10FNBZod84VXzi10nyotKAi0XhlLdZu-Vut-IDkMv5zAwA8FbJyrEe0PW1DivgFHc4j0S0D4nGUKZxgyZkksvc9X90KLsqZCLQml2x0hw9cqVXdpAxZBWaeXhhTsrapwjwGJkVrC37PAJXAA5T",
          "widthPx": 3840,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Matt Leonard",
              "uri": "https://maps.google.com/maps/contrib/108791823693982137331",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU7UAGq8gnfvEXSY2ZAUsR8OP_CzIPY8vUd_6y3gF6y8MI-TIo0=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/photos/AdCG2DNzUrYckhxSoRa-dhqqk7H8WF9_EdQzWm55OqZG-bDBeHRhHv3RcGRaMTJc37EhLUovxHDXz-lmNz-jgTNO9dP6Mnp0MQNgrv9v1ritDHF18nvVPlpUC70mV3JN12ZbifjFYpV7z3taqZC0g13b-cmObbBPJKEdkOdv",
          "widthPx": 4000,
          "heightPx": 3000,
          "authorAttributions": [
            {
              "displayName": "Charlie",
              "uri": "https://maps.google.com/maps/contrib/106626322048443564823",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUkuIoyD4ndTy12-b-34OmQqBPGRIrmAO1a5A6qsU_p0tkmkX8Nrg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/photos/AdCG2DP07x90X8GMieQB97TtDSAOOiG87Qn5gbbxJOWBRwu5pdjY_IPuxk0qKwOZKaAWjpy1Wv2fkY14nlvFjOdRwNN4BDtDJhJsytNeOfRaCjW2QfjXq5r6wU1DZJ0b1DQuz00kj_CrJsdGyh2j4-9H05lRQRAGXJCXdSpd",
          "widthPx": 800,
          "heightPx": 600,
          "authorAttributions": [
            {
              "displayName": "محمود شهاب",
              "uri": "https://maps.google.com/maps/contrib/107182343019467928487",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocIqvgI8Z4-Li07wBqP-nxAInheSvo4zbmjRwVIiRKYn4w7TNA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/photos/AdCG2DP_O-IoSw2H3LFLbTGmYEQQaQnV_N8rNt8MJ0_sVzus-nsUhCu1oSzVK8wf4YSdh448u70u62NB-_ntFd-0OLACL8KQUOyz4dEYi8fRZDoZ_FHbFsRjiCtMcwy7TIqcQtvmVQanyD9brd-g5zinfITQCRy0zEBPiebB",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Anthony Lopez",
              "uri": "https://maps.google.com/maps/contrib/113664163768913179190",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUDmPgGDdYrrdo2yemr_TUmJ3h3o4X1a1sUIbHQQOekdpxNXs_9=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/photos/AdCG2DNxzAVUFLDI01zizFVmNIrulKmvAT0KVez9_e3MnujOcQe6gIosWuX6_V8yBt1UuBB7LHMMjJDYulrRKqJb1BUE__oozgZmwtgmGdS34Ksv96y5xxldWojFoRQCp8e7fov4rn-GZlVucFlmV_FkhcuKN1QHYOoeTps9",
          "widthPx": 2992,
          "heightPx": 2992,
          "authorAttributions": [
            {
              "displayName": "Jeffrey Alvarez",
              "uri": "https://maps.google.com/maps/contrib/108658323151750637888",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjW562oiDiyz99JYi7qW_UJFty_VRK06FOdSnY1nbUOQwQwtiXs=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/photos/AdCG2DOvuby4_28At8vU6Makz-XSYUWVvOm5FRXfzBnWj6JuHrv9pBFQ5_HGLlrG-vZEWcd3cf8scwMOHd_pA5zXfGqrNSgCWpj3xJj9FjayKTYYHDKWwXO2v0lLOARiVv1-ZGgD8e6lQDnzhJt3kdgKEkR3rPWkKfEZbeIs",
          "widthPx": 4800,
          "heightPx": 3600,
          "authorAttributions": [
            {
              "displayName": "Anthony Lopez",
              "uri": "https://maps.google.com/maps/contrib/113664163768913179190",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUDmPgGDdYrrdo2yemr_TUmJ3h3o4X1a1sUIbHQQOekdpxNXs_9=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/photos/AdCG2DOtQgXhJizPH_ac_o-Jgu0hT5Aq2fr4eWGF6RnW-sk2jJ51TXSEEaqrWk4udBo6yo5mEHos_KFeTq3ZaI1HAeo-HirbH1nLSTudf8FZVOT1RefVzA3e4J5SxqEDwYeaGAcAizTyJlpaXvAIEkKZE-MZuZJN83eGhA0W",
          "widthPx": 3000,
          "heightPx": 4000,
          "authorAttributions": [
            {
              "displayName": "Joselin Fuller",
              "uri": "https://maps.google.com/maps/contrib/111902297950082664866",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXmnSe7dZfyiKUvXfEsgJWOjkxk7yYUCqKhOA8Mkqd3OKkJrSBi=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/photos/AdCG2DOyisdTgCxmhWfXBiS-zPgjmUvocDRCwvxaHC_83wbPuY1JlSE4RNc8L5GTNh7LUcDEIfYyyIhr98SG1PrhUp855PlIFQmxYE7MhuIMNijdGdiOywB-xdr48sAf9DQ_F2IyrwCoXnYbwX-XkKRO_NuvX7N_pD7mtPhA",
          "widthPx": 3492,
          "heightPx": 4656,
          "authorAttributions": [
            {
              "displayName": "Eddie",
              "uri": "https://maps.google.com/maps/contrib/115030550033768869161",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWp_i3Ux4w2nLWjXu7yn_1zpFN-nAl8pDw1zDujLpsFRwxA6sA1RA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/photos/AdCG2DNCdFZladgvl6W-1eDQcQymvinH_Q2LYlZwDCDYtlaqWvmkM0icBRrMtF1G91eG1Ty6V3CKki7jKeROLmNgXS6AVoj7QKp3r6hV9go_FrjXLkE7AhZFGnujKm9LaJi2_Ef6qnQhpTr3Mv2iB5LbT2JYrqI_lLFEIGZL",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Tereza Bartonova",
              "uri": "https://maps.google.com/maps/contrib/100831284454470387578",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXDtl2cqJfqDU0bw_DjHE6X5fcz2vOLPBlkNfW6HwWosE3lGv8=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVfNmkUrGwoARPoiVkasCkqc/photos/AdCG2DNswp8Sq85klEyOmk_M-E3qzfg4jRjI1M4yUt_1EkDgNEKCHF9Ma9iUpoyCi7KnMAuLFDQOfR60nbxXRAVCzwJ0UNnlK6Ry1F0tl0C9-86NXS1UT8oYAA21T49Ro-I0FB2dvxyxEmT_fCPLcNNuQielv329BYsHcWlF",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Angie Swan",
              "uri": "https://maps.google.com/maps/contrib/115857410872959768039",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjV91rQwMipLW2ADN6lXky2Dr_kLlzf3CM88wuJPKlZ9Cwizk_dzhg=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "liveMusic": False,
      "menuForChildren": False,
      "servesCocktails": False,
      "servesDessert": False,
      "servesCoffee": True,
      "goodForChildren": True,
      "goodForGroups": True,
      "goodForWatchingSports": False,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "parkingOptions": {
        "freeParkingLot": True,
        "paidParkingLot": True,
        "freeStreetParking": True,
        "paidStreetParking": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleParking": False,
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Homemade corn tortillas are used for tacos at this casual, kid-friendly Mexican spot.",
          "languageCode": "en-US"
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJ7YJ_IkrGwoARNak4CDihkYU",
            "placeId": "ChIJ7YJ_IkrGwoARNak4CDihkYU",
            "displayName": {
              "text": "The Last Bookstore",
              "languageCode": "en"
            },
            "types": [
              "book_store",
              "establishment",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 140.48868,
            "travelDistanceMeters": 162.78096
          },
          {
            "name": "places/ChIJfYYjikrGwoARbpipFfLpMMI",
            "placeId": "ChIJfYYjikrGwoARbpipFfLpMMI",
            "displayName": {
              "text": "The Los Angeles Theatre Center",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 74.02995,
            "travelDistanceMeters": 53.79597
          },
          {
            "name": "places/ChIJVfNmkUrGwoARgj67xhkTa7E",
            "placeId": "ChIJVfNmkUrGwoARgj67xhkTa7E",
            "displayName": {
              "text": "Spring Arcade Building",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "BESIDE",
            "straightLineDistanceMeters": 63.770557,
            "travelDistanceMeters": 23.988262
          },
          {
            "name": "places/ChIJZ-tMZzXGwoARelLmZjoL4Eo",
            "placeId": "ChIJZ-tMZzXGwoARelLmZjoL4Eo",
            "displayName": {
              "text": "Exchange LA",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "night_club",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 149.81705,
            "travelDistanceMeters": 148.04565
          },
          {
            "name": "places/ChIJq4xmkUrGwoARbtp4kMBURz8",
            "placeId": "ChIJq4xmkUrGwoARbtp4kMBURz8",
            "displayName": {
              "text": "Blu Jam Cafe",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "food",
              "point_of_interest",
              "restaurant"
            ],
            "spatialRelationship": "ACROSS_THE_ROAD",
            "straightLineDistanceMeters": 107.81294,
            "travelDistanceMeters": 23.988262
          }
        ],
        "areas": [
          {
            "name": "places/ChIJw2qwSkrGwoARg4ZFCHwosJg",
            "placeId": "ChIJw2qwSkrGwoARg4ZFCHwosJg",
            "displayName": {
              "text": "Historic Core",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA",
      "id": "ChIJJw2qMIDIwoARwd_Lj1RgZNA",
      "types": [
        "mexican_restaurant",
        "fast_food_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 742-6677",
      "internationalPhoneNumber": "+1 213-742-6677",
      "formattedAddress": "1900 S Central Ave, Los Angeles, CA 90011, USA",
      "addressComponents": [
        {
          "longText": "1900",
          "shortText": "1900",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "South Central Avenue",
          "shortText": "S Central Ave",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "South Los Angeles",
          "shortText": "South Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90011",
          "shortText": "90011",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632PFX+JQ",
        "compoundCode": "2PFX+JQ Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.0241067,
        "longitude": -118.2505209
      },
      "viewport": {
        "low": {
          "latitude": 34.0227921697085,
          "longitude": -118.25187208029148
        },
        "high": {
          "latitude": 34.025490130291494,
          "longitude": -118.24917411970848
        }
      },
      "rating": 4.3,
      "googleMapsUri": "https://maps.google.com/?cid=15016232973866098625",
      "websiteUri": "https://tacosgavilan.com/",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 8,
              "minute": 0
            },
            "close": {
              "day": 1,
              "hour": 1,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 8,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 1,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 8,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 1,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 8,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 1,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 8,
              "minute": 0
            },
            "close": {
              "day": 5,
              "hour": 2,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 8,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 3,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 8,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 3,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 8:00 AM – 1:00 AM",
          "Tuesday: 8:00 AM – 1:00 AM",
          "Wednesday: 8:00 AM – 1:00 AM",
          "Thursday: 8:00 AM – 2:00 AM",
          "Friday: 8:00 AM – 3:00 AM",
          "Saturday: 8:00 AM – 3:00 AM",
          "Sunday: 8:00 AM – 1:00 AM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e1900 S Central Ave\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90011\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_INEXPENSIVE",
      "userRatingCount": 4628,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Tacos Gavilan",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "reservable": False,
      "servesBreakfast": True,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": False,
      "servesWine": False,
      "servesBrunch": False,
      "servesVegetarianFood": False,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 8,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 1,
              "hour": 1,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 8,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 2,
              "hour": 1,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 8,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 3,
              "hour": 1,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 8,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 23,
              "minute": 59,
              "truncated": True,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 0,
              "minute": 0,
              "truncated": True,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 1,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 8,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 5,
              "hour": 2,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 8,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 6,
              "hour": 3,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 8,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 0,
              "hour": 3,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 8:00 AM – 1:00 AM",
          "Tuesday: 8:00 AM – 1:00 AM",
          "Wednesday: 8:00 AM – 1:00 AM",
          "Thursday: 8:00 AM – 2:00 AM",
          "Friday: 8:00 AM – 3:00 AM",
          "Saturday: 8:00 AM – 3:00 AM",
          "Sunday: 8:00 AM – 1:00 AM"
        ]
      },
      "currentSecondaryOpeningHours": [
        {
          "openNow": True,
          "periods": [
            {
              "open": {
                "day": 0,
                "hour": 8,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 20
                }
              },
              "close": {
                "day": 1,
                "hour": 2,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 21
                }
              }
            },
            {
              "open": {
                "day": 1,
                "hour": 8,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 21
                }
              },
              "close": {
                "day": 2,
                "hour": 2,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 22
                }
              }
            },
            {
              "open": {
                "day": 2,
                "hour": 8,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 22
                }
              },
              "close": {
                "day": 3,
                "hour": 2,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 23
                }
              }
            },
            {
              "open": {
                "day": 3,
                "hour": 8,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 23
                }
              },
              "close": {
                "day": 3,
                "hour": 23,
                "minute": 59,
                "truncated": True,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 23
                }
              }
            },
            {
              "open": {
                "day": 4,
                "hour": 0,
                "minute": 0,
                "truncated": True,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 17
                }
              },
              "close": {
                "day": 4,
                "hour": 2,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 17
                }
              }
            },
            {
              "open": {
                "day": 4,
                "hour": 8,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 17
                }
              },
              "close": {
                "day": 5,
                "hour": 3,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 18
                }
              }
            },
            {
              "open": {
                "day": 5,
                "hour": 8,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 18
                }
              },
              "close": {
                "day": 6,
                "hour": 4,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 19
                }
              }
            },
            {
              "open": {
                "day": 6,
                "hour": 8,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 19
                }
              },
              "close": {
                "day": 0,
                "hour": 4,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 20
                }
              }
            }
          ],
          "weekdayDescriptions": [
            "Monday: 8:00 AM – 2:00 AM",
            "Tuesday: 8:00 AM – 2:00 AM",
            "Wednesday: 8:00 AM – 2:00 AM",
            "Thursday: 8:00 AM – 3:00 AM",
            "Friday: 8:00 AM – 4:00 AM",
            "Saturday: 8:00 AM – 4:00 AM",
            "Sunday: 8:00 AM – 2:00 AM"
          ],
          "secondaryHoursType": "DRIVE_THROUGH"
        }
      ],
      "regularSecondaryOpeningHours": [
        {
          "openNow": True,
          "periods": [
            {
              "open": {
                "day": 0,
                "hour": 8,
                "minute": 0
              },
              "close": {
                "day": 1,
                "hour": 2,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 1,
                "hour": 8,
                "minute": 0
              },
              "close": {
                "day": 2,
                "hour": 2,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 2,
                "hour": 8,
                "minute": 0
              },
              "close": {
                "day": 3,
                "hour": 2,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 3,
                "hour": 8,
                "minute": 0
              },
              "close": {
                "day": 4,
                "hour": 2,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 4,
                "hour": 8,
                "minute": 0
              },
              "close": {
                "day": 5,
                "hour": 3,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 5,
                "hour": 8,
                "minute": 0
              },
              "close": {
                "day": 6,
                "hour": 4,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 6,
                "hour": 8,
                "minute": 0
              },
              "close": {
                "day": 0,
                "hour": 4,
                "minute": 0
              }
            }
          ],
          "weekdayDescriptions": [
            "Monday: 8:00 AM – 2:00 AM",
            "Tuesday: 8:00 AM – 2:00 AM",
            "Wednesday: 8:00 AM – 2:00 AM",
            "Thursday: 8:00 AM – 3:00 AM",
            "Friday: 8:00 AM – 4:00 AM",
            "Saturday: 8:00 AM – 4:00 AM",
            "Sunday: 8:00 AM – 2:00 AM"
          ],
          "secondaryHoursType": "DRIVE_THROUGH"
        }
      ],
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "1900 S Central Ave, Los Angeles",
      "editorialSummary": {
        "text": "Busy local chain eatery for quick-serve Mexican cooking, from tacos to mulitas, plus a salsa bar.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/reviews/ChZDSUhNMG9nS0VJQ0FnSUREc2JMU1lBEAE",
          "relativePublishTimeDescription": "6 months ago",
          "rating": 5,
          "text": {
            "text": "I like that this place has enough parking. And a lot of tables to eat. The torta cubana was good. I enjoyed it. The agua de piña was ok too. The green sauce was ok it could be better though I could not taste the spicy flavor from it.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "I like that this place has enough parking. And a lot of tables to eat. The torta cubana was good. I enjoyed it. The agua de piña was ok too. The green sauce was ok it could be better though I could not taste the spicy flavor from it.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "AUTO TUB3",
            "uri": "https://www.google.com/maps/contrib/106871053066991045502/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjX5oNNpnutyDtr8IDlV6XlZPqRdtIU82ZcWmgvONHJDmrsOuqz_=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-04-11T00:41:03.500297Z"
        },
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/reviews/ChZDSUhNMG9nS0VJQ0FnSURUeFp6T05REAE",
          "relativePublishTimeDescription": "4 months ago",
          "rating": 5,
          "text": {
            "text": "I never write reviews but this place deserves it! Clean, great service and great atmosphere.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "I never write reviews but this place deserves it! Clean, great service and great atmosphere.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Mister cuellar",
            "uri": "https://www.google.com/maps/contrib/115979211743539940140/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVjZrZ00Ewx5_85NnSlm31r_vD1eTbII656xltjLnpJka5t3ShZ=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-05-26T05:43:09.494525Z"
        },
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/reviews/ChdDSUhNMG9nS0VJQ0FnSURuMjVER213RRAB",
          "relativePublishTimeDescription": "a week ago",
          "rating": 2,
          "text": {
            "text": "They are remodeling but still clean service was great but the meat was no bueno. In every bite they was chewy piece of meat that I had to spit out and I had to take small bites because the meat was not tender. I wasn't going to waste money so I ate what I could and threw the rest away. Disappointed",
            "languageCode": "en"
          },
          "originalText": {
            "text": "They are remodeling but still clean service was great but the meat was no bueno. In every bite they was chewy piece of meat that I had to spit out and I had to take small bites because the meat was not tender. I wasn't going to waste money so I ate what I could and threw the rest away. Disappointed",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Nishea Beyatch",
            "uri": "https://www.google.com/maps/contrib/109643416719914362604/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUuoWRgKIiMmZFi-w8fVWkPhDRrfYKFU8Dls2m4doSlDHyQboZQqw=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-10-10T11:30:00.298981Z"
        },
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/reviews/ChZDSUhNMG9nS0VJQ0FnSURacHRURExBEAE",
          "relativePublishTimeDescription": "a year ago",
          "rating": 3,
          "text": {
            "text": "Tasty Burrito and Nachos 3 1/2 stars, I  had the burrito and nachos at this place and found them to be tasty. The burrito was packed with flavorful ingredients, though a bit more seasoning would have elevated the taste. The nachos de al pastor were delicious, the cheese was actually nacho cheese flavor the chips were round like movie theater chips. Overall, a good option for taco, burrito , nacho food lovers, with a little room for improvement.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Tasty Burrito and Nachos 3 1/2 stars, I  had the burrito and nachos at this place and found them to be tasty. The burrito was packed with flavorful ingredients, though a bit more seasoning would have elevated the taste. The nachos de al pastor were delicious, the cheese was actually nacho cheese flavor the chips were round like movie theater chips. Overall, a good option for taco, burrito , nacho food lovers, with a little room for improvement.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "J V",
            "uri": "https://www.google.com/maps/contrib/118090450594430447731/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVaIjHYjcDG9LQ3I827Y5AAqTj-rmNrhy1Hb99Ov3dnsQYukBj0sg=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2023-09-29T21:52:30.229698Z"
        },
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/reviews/ChZDSUhNMG9nS0VJQ0FnSURScGVEQmJBEAE",
          "relativePublishTimeDescription": "a year ago",
          "rating": 4,
          "text": {
            "text": "I've been here a few times since 2019 and have always had a good experience. I've had tortas and nachos so far. I believe they make their own chips because they have a unique fresh taste. They have an employee almost always keeping the dining room clean. A clean dining area represents a clean line and kitchen, so I recommend this place for those who love food establishments that keep their dining area clean. This location sits on what was once an old style McDonald's that had arches on the establishment (Google map this as far as 2007). I consider this corner part of DTLA despite the fact it actually sits on the South L.A. side of Washington Blvd. Washington Blvd. borderlines DTLA and South L.A. at Central Ave. 🌯 🚲",
            "languageCode": "en"
          },
          "originalText": {
            "text": "I've been here a few times since 2019 and have always had a good experience. I've had tortas and nachos so far. I believe they make their own chips because they have a unique fresh taste. They have an employee almost always keeping the dining room clean. A clean dining area represents a clean line and kitchen, so I recommend this place for those who love food establishments that keep their dining area clean. This location sits on what was once an old style McDonald's that had arches on the establishment (Google map this as far as 2007). I consider this corner part of DTLA despite the fact it actually sits on the South L.A. side of Washington Blvd. Washington Blvd. borderlines DTLA and South L.A. at Central Ave. 🌯 🚲",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Armando Bello",
            "uri": "https://www.google.com/maps/contrib/103517010553096700047/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVGXZUe7v0YEhGyymvfJ-mobhzq0O7fk3-9ymWPIqGT-ohO69c6sw=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2023-04-29T19:46:18.496962Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/photos/AdCG2DMpduUwM75_BMb_rW-xve1LU16r0f_fasC-v2dj2yAq0jh8u_McYVc586rjY32KOzN0yUbT8II9FV0rFdgBfF8iQWJSfCnEK7tMrl8g_frJ1jubCYcQBF88ykXgBqrAg1Su3llzzuePku1hK1zKDgZg7neseT3NFvLQ",
          "widthPx": 1449,
          "heightPx": 1719,
          "authorAttributions": [
            {
              "displayName": "Tawny Valdez",
              "uri": "https://maps.google.com/maps/contrib/107915963037960084951",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVOVbLFalUU0eFQJrp6ojzvePOKHZkMpc031VotQuuBe8QGyHIc=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/photos/AdCG2DPvQ9Qmfso87xzOVXjMPI7tHxFVivLVEuJJj36CY8THcLqJWZDPWXfqW51I0Y6H9Z0NIhkbWzeIjEpxKe-56K9t8VTlTI-hxsnbaReiMC9BoikGLZ2dEygtBPNj2o6FzD6FRW6OS_Ry2W9m622ybTtQ9gBLpJqm5oj4",
          "widthPx": 1000,
          "heightPx": 1212,
          "authorAttributions": [
            {
              "displayName": "Tacos Gavilan",
              "uri": "https://maps.google.com/maps/contrib/109034014451024594397",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUVh4UWh4kBgZljaggwZqAXxjgJv3IfWKu0qg_36hIf_UXyQGM=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/photos/AdCG2DNA5j5MfVqpdApritpM7oU00YkG844f7qJjzi22E7LUX8Sc6kZknwdhisYm1pJsDqqX_NfbCkByOGr47zNibt-pkdr64-p6x9Me1Aii3Z2CLzE3Zu4Y5oJYeie_A3l4roAQflHz95LFEPPGUC82ip2B8N8EzRiBAHVi",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Mister cuellar",
              "uri": "https://maps.google.com/maps/contrib/115979211743539940140",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVjZrZ00Ewx5_85NnSlm31r_vD1eTbII656xltjLnpJka5t3ShZ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/photos/AdCG2DMCuKXIitqNxU2Db-fjlVx0E00JgsdmVxu_f2jst_aOc8Je9IPvI1OX5omLJtyWlG70BSSoXOxQ0TmBL07ET7AYWX8bs_NeOb2uGDWxGatn2OWFMfAItlUnQnhM7hKuZBmOq0bljh96PUlhkj2VIO2HWACBTAOIZHRb",
          "widthPx": 4000,
          "heightPx": 3000,
          "authorAttributions": [
            {
              "displayName": "Cleona Bautista",
              "uri": "https://maps.google.com/maps/contrib/111275097663921881335",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWTEs7OlB39uO-DJAHmZsd3Xtr51kdTf8FxM8YOlhoFH7GMHnkZtg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/photos/AdCG2DMxvi36oGeqlopGXh0lwAOwqlF5UgVzmj2HV5cuZxp74VP3tSb4Ue41DZlmYv-Tp8zyP88AwKu6aGxBY4EADJ80LLpCQ1y6u27IB2W9UroInWctIo9MlDgKIJ1cZjq-Z5kYklteyU8MaTEV2-xaJWx1_lWl0GsNmgAU",
          "widthPx": 3000,
          "heightPx": 4000,
          "authorAttributions": [
            {
              "displayName": "Yoli yolanda",
              "uri": "https://maps.google.com/maps/contrib/104744514572124367699",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWL05R11Qcfdd00XQHANTWL6RUCNqJWHmgLetJzqnWoDIiY6fuv=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/photos/AdCG2DOGvkDwjhzJN830Qa_exXZ0QEY8ChwK5mOw_C1iWnaWG0N9prBrwn3mI5bSYcmL1q8I8MgAeJDULdVfHyG_OBHV8YrnrTsgN4j4HIVvWF6-k3i41U44yMWF9G4BeILbnbkqWW4mjJOld4xngm7DzvcwOwXTeE2wVj3o",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Scott Semilla",
              "uri": "https://maps.google.com/maps/contrib/107795285238811210098",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVQfFp1ulIzIilm1GNkFbKC00UGGV6LenYuyVhAPba_b7OhDgCF=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/photos/AdCG2DPIm2H6OCQLS2zguxwrNqA3eqg-ijtpPBYFFdn10UljQQII6MaU_kFmbJ-bW-InRQbF2Ekib3nOe9Y64UnJpvQujta4_9TAF9tk4ESmXXn-A4RAFBuaHsqMBD2DnZhiJL0vXxGLVb5bbjzHW-JexReJVbUkZzNfNByd",
          "widthPx": 4080,
          "heightPx": 3072,
          "authorAttributions": [
            {
              "displayName": "Robert Rael",
              "uri": "https://maps.google.com/maps/contrib/112792759444568871268",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWczQD9vieLUF8yWcPQb9fn0k3wbZY-0-H0_ygNAyWgJ9-rjepHLA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/photos/AdCG2DOv3YACmQd6Z-z0gEua3MpmAKa7KET_IvvSi8Os60iATJrlTQXBBruuvqE9nUJ0fNOSjR3ecNCtqVIHI39oTaIC1hP5XEg85uzQpgJt8Ct5tZrkzi09xf3TTROD7KVy4GzOkQSM8_l791HCKIYNb0qnWbfSZBClW09s",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Luis Golx",
              "uri": "https://maps.google.com/maps/contrib/110380698897636376458",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWI3R4kBkGSuintnj5Apny2H2CIiQ7ryAaKYTpFsfYVSh_rm_2V=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/photos/AdCG2DMQ-jAjUm_zQZP0gJDienzkHEUblHzkujWGpGl8E3lGyHgvk6P8lXljGSfVSm7l5VmMYmzZZZCFHITZL6Z3JQv1tYzofPMdSPlkC4NGjZ0O45hrIs-Khzo0MZpc6MhIAw4891SPe0NA8vODp2rstxQ5djlPkFEE8Yj3",
          "widthPx": 1640,
          "heightPx": 2727,
          "authorAttributions": [
            {
              "displayName": "chekelin Valtierra",
              "uri": "https://maps.google.com/maps/contrib/116183478574321654650",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWjU-fhLK5p7NRjrvCX0_Ji9wKoBkQ9j7i6GjFBWk4rihD-M7hl7Q=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJJw2qMIDIwoARwd_Lj1RgZNA/photos/AdCG2DO_a4ymyoPQRHUD4LiDaN6DicPsy_N4uTcL-cezh434tr_po8kihmp_kvIpD9cji0eqVFV0aaCbidqzu7EI9ve0-BAxBlZIVr3CmW-9Z_CyT8h6vimsy9psTwKi3_rwzXD3o0TJOyUkLKX2HccitrRciSb2CZT4DsCT",
          "widthPx": 954,
          "heightPx": 519,
          "authorAttributions": [
            {
              "displayName": "Tacos Gavilan",
              "uri": "https://maps.google.com/maps/contrib/109034014451024594397",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUVh4UWh4kBgZljaggwZqAXxjgJv3IfWKu0qg_36hIf_UXyQGM=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": False,
      "liveMusic": False,
      "menuForChildren": False,
      "servesCocktails": False,
      "servesDessert": True,
      "servesCoffee": True,
      "goodForChildren": True,
      "allowsDogs": False,
      "restroom": True,
      "goodForGroups": True,
      "goodForWatchingSports": True,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "parkingOptions": {
        "freeParkingLot": True,
        "freeStreetParking": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleParking": True,
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleRestroom": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Tacos, burritos and other classic Mexican staples served in a relaxed space with a drive-thru.",
          "languageCode": "en-US"
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJ9RtnNIDIwoARU5tOehyudpI",
            "placeId": "ChIJ9RtnNIDIwoARU5tOehyudpI",
            "displayName": {
              "text": "Shell",
              "languageCode": "en"
            },
            "types": [
              "atm",
              "car_wash",
              "convenience_store",
              "establishment",
              "finance",
              "food",
              "gas_station",
              "point_of_interest",
              "store"
            ],
            "straightLineDistanceMeters": 64.69487,
            "travelDistanceMeters": 151.96895
          },
          {
            "name": "places/ChIJdYQQTNXHwoARyUl4-WWDZkg",
            "placeId": "ChIJdYQQTNXHwoARyUl4-WWDZkg",
            "displayName": {
              "text": "Planet Fitness",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "gym",
              "health",
              "point_of_interest",
              "spa"
            ],
            "straightLineDistanceMeters": 166.90509,
            "travelDistanceMeters": 276.49527
          },
          {
            "name": "places/ChIJo7kmb4DIwoAR702FeJkPx00",
            "placeId": "ChIJo7kmb4DIwoAR702FeJkPx00",
            "displayName": {
              "text": "Superior Grocers",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "food",
              "grocery_or_supermarket",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 193.94562,
            "travelDistanceMeters": 212.21971
          },
          {
            "name": "places/ChIJCzuyM4DIwoARIKS6erhv2z8",
            "placeId": "ChIJCzuyM4DIwoARIKS6erhv2z8",
            "displayName": {
              "text": "7-Eleven",
              "languageCode": "en"
            },
            "types": [
              "convenience_store",
              "establishment",
              "food",
              "point_of_interest",
              "store"
            ],
            "straightLineDistanceMeters": 80.94533,
            "travelDistanceMeters": 139.66891
          },
          {
            "name": "places/ChIJm3DrLIDIwoARx0fdg1WLwT8",
            "placeId": "ChIJm3DrLIDIwoARx0fdg1WLwT8",
            "displayName": {
              "text": "El Delfin",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "food",
              "point_of_interest",
              "restaurant"
            ],
            "straightLineDistanceMeters": 120.4916,
            "travelDistanceMeters": 167.61224
          }
        ],
        "areas": [
          {
            "name": "places/ChIJBTfoNffIwoAR8DphwuKKK6I",
            "placeId": "ChIJBTfoNffIwoAR8DphwuKKK6I",
            "displayName": {
              "text": "Central-Alameda",
              "languageCode": "en"
            },
            "containment": "OUTSKIRTS"
          },
          {
            "name": "places/ChIJ6bcf1Nu3woARGCYveWr_oiQ",
            "placeId": "ChIJ6bcf1Nu3woARGCYveWr_oiQ",
            "displayName": {
              "text": "South Los Angeles",
              "languageCode": "en"
            },
            "containment": "OUTSKIRTS"
          },
          {
            "name": "places/ChIJj_6lM4DIwoARzR-10Xh3OM8",
            "placeId": "ChIJj_6lM4DIwoARzR-10Xh3OM8",
            "displayName": {
              "text": "Shell",
              "languageCode": "en"
            },
            "containment": "NEAR"
          }
        ]
      }
    },
    {
      "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU",
      "id": "ChIJvQRXWpy5woARXF1TL3dFJAU",
      "types": [
        "mexican_restaurant",
        "seafood_restaurant",
        "vegetarian_restaurant",
        "bar",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 375-3300",
      "internationalPhoneNumber": "+1 213-375-3300",
      "formattedAddress": "2000 E 7th St, Los Angeles, CA 90021, USA",
      "addressComponents": [
        {
          "longText": "2000",
          "shortText": "2000",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "East 7th Street",
          "shortText": "E 7th St",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90021",
          "shortText": "90021",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632QM9+Q4",
        "compoundCode": "2QM9+Q4 Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.0344519,
        "longitude": -118.23213
      },
      "viewport": {
        "low": {
          "latitude": 34.033153319708504,
          "longitude": -118.2335260302915
        },
        "high": {
          "latitude": 34.0358512802915,
          "longitude": -118.23082806970851
        }
      },
      "rating": 4.5,
      "googleMapsUri": "https://maps.google.com/?cid=370497447548640604",
      "websiteUri": "http://www.guerrillatacos.com/?y_source=1_NzU1NzcwODAtNzE1LWxvY2F0aW9uLndlYnNpdGU%3D",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 12,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 12,
              "minute": 0
            },
            "close": {
              "day": 1,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 12,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 12,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 12,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 12,
              "minute": 0
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 12,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 12:00 – 9:00 PM",
          "Tuesday: 12:00 – 9:00 PM",
          "Wednesday: 12:00 – 9:00 PM",
          "Thursday: 12:00 – 9:00 PM",
          "Friday: 12:00 – 10:00 PM",
          "Saturday: 12:00 – 10:00 PM",
          "Sunday: 12:00 – 9:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e2000 E 7th St\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90021\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_MODERATE",
      "userRatingCount": 1258,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Guerrilla Tacos",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "reservable": True,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": True,
      "servesWine": True,
      "servesBrunch": True,
      "servesVegetarianFood": True,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 12,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 12,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 12,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 12,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 12,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 12,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 12,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 12:00 – 9:00 PM",
          "Tuesday: 12:00 – 9:00 PM",
          "Wednesday: 12:00 – 9:00 PM",
          "Thursday: 12:00 – 9:00 PM",
          "Friday: 12:00 – 10:00 PM",
          "Saturday: 12:00 – 10:00 PM",
          "Sunday: 12:00 – 9:00 PM"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "2000 E 7th St, Los Angeles",
      "editorialSummary": {
        "text": "Contemporary restaurant originating from a food truck plating tacos with local ingredients & a bar.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/reviews/ChZDSUhNMG9nS0VJQ0FnSUNYeEltVGZ3EAE",
          "relativePublishTimeDescription": "in the last week",
          "rating": 3,
          "text": {
            "text": "Nice corner spot! Nice vibe ambience! The food. Ordered mushroom and cheese taco, sweet potato taco and the potato taquitos. Def not a fan of the potato taquitos.. no flavor at all for the potato which is a huge downfall.. a very flavorless dish even with the green sauce and cheese.   Not a fan of the sweet potato taco either. The best part of the meal was the mushroom cheese taco. Maybe next time.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Nice corner spot! Nice vibe ambience! The food. Ordered mushroom and cheese taco, sweet potato taco and the potato taquitos. Def not a fan of the potato taquitos.. no flavor at all for the potato which is a huge downfall.. a very flavorless dish even with the green sauce and cheese.   Not a fan of the sweet potato taco either. The best part of the meal was the mushroom cheese taco. Maybe next time.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "PJ",
            "uri": "https://www.google.com/maps/contrib/107001906764178680685/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXRLyETzsWc2_-nYffMoa3wVen3ukgS3RoQtQhr-EMgMXFLHL_I=s128-c0x00000000-cc-rp-mo-ba6"
          },
          "publishTime": "2024-10-13T09:52:38.398082Z"
        },
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/reviews/ChZDSUhNMG9nS0VJQ0FnSURMdl9qcktREAE",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 5,
          "text": {
            "text": "Very good, delicious, creative tacos. Good value for a meal of this caliber.\n\nMain downside — quite empty for a Friday night when I went, did not make for a great ambience though I realize that’s not totally within the restaurant’s control. Makes for an easy table to get though",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Very good, delicious, creative tacos. Good value for a meal of this caliber.\n\nMain downside — quite empty for a Friday night when I went, did not make for a great ambience though I realize that’s not totally within the restaurant’s control. Makes for an easy table to get though",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Albert Phan",
            "uri": "https://www.google.com/maps/contrib/108933470425355572855/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocJcXfsgsrvyHrikwNTzjXVVzZYwTmq0wYMbeqmsQObKO7I0MQ=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-07-02T19:07:08.593077Z"
        },
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/reviews/ChZDSUhNMG9nS0VJQ0FnSURuM1oyWGVREAE",
          "relativePublishTimeDescription": "a week ago",
          "rating": 5,
          "text": {
            "text": "Food was really delicious and fresh. I ordered the potato and cheese taquitos, sweet potato taco and Baja fish taco. The cucumber radish slaw and habanero onions really elevated the fish taco.  To drink I had the passion fruit margarita. Tuesday during happy hour offered great deals. Josh, was very friendly and helpful as a server.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Food was really delicious and fresh. I ordered the potato and cheese taquitos, sweet potato taco and Baja fish taco. The cucumber radish slaw and habanero onions really elevated the fish taco.  To drink I had the passion fruit margarita. Tuesday during happy hour offered great deals. Josh, was very friendly and helpful as a server.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Kelvina Doss",
            "uri": "https://www.google.com/maps/contrib/111858178540358637110/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjV0HSjlqZrjbxV4meKWtEw24bz6omF3Cle9Ti1iYIIuWK_SU-wi=s128-c0x00000000-cc-rp-mo-ba2"
          },
          "publishTime": "2024-10-09T01:15:57.085031Z"
        },
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/reviews/ChdDSUhNMG9nS0VJQ0FnSURid2RYNHFBRRAB",
          "relativePublishTimeDescription": "2 months ago",
          "rating": 5,
          "text": {
            "text": "This was the second time we have eaten at Guerrilla Tacos. The first time we ate here was soon after they opened and honestly we did not find it that impressive. We were down in this area of LA shopping and decided to give Guerrilla Tacos another try… we are glad we did!! Food was excellent, service solid and a good atmosphere.\nThe mole on the Chicken Mole Quesadilla was excellent. The Scallop Strawberry Morita Aguachile flavorful and refreshing, scallops were very fresh. The Cucumber Radish\nSlaw and Pickled Red Onions on the Baja Fish Taco added great flavor and texture. We also had the Sweet Potato Taco and Calabasitas Taco which would order again. The Tres Leches dessert was not to sweet which was good, great flavor.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "This was the second time we have eaten at Guerrilla Tacos. The first time we ate here was soon after they opened and honestly we did not find it that impressive. We were down in this area of LA shopping and decided to give Guerrilla Tacos another try… we are glad we did!! Food was excellent, service solid and a good atmosphere.\nThe mole on the Chicken Mole Quesadilla was excellent. The Scallop Strawberry Morita Aguachile flavorful and refreshing, scallops were very fresh. The Cucumber Radish\nSlaw and Pickled Red Onions on the Baja Fish Taco added great flavor and texture. We also had the Sweet Potato Taco and Calabasitas Taco which would order again. The Tres Leches dessert was not to sweet which was good, great flavor.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Michael Pentzer",
            "uri": "https://www.google.com/maps/contrib/114544436591962071547/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocI7wbXZ2QdWMf7TiJd4OcFVZ3H3AaONFduCguA_wtoN3UtTHw=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-08-06T06:43:27.987035Z"
        },
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/reviews/ChZDSUhNMG9nS0VJQ0FnSUN6ODR2U1NREAE",
          "relativePublishTimeDescription": "4 months ago",
          "rating": 4,
          "text": {
            "text": "Decent place. More hip/ster feeling than I expected it to be\n\nDrinks were ok- we got 2 and not super memorable; I remember them being packed with ice. Tacos we got (short ribs, sweet potato, and octopus) were really tasty & a very different blend of flavors! The best one was the octopus taco.\n\nMy friend liked this place better than Etta (in Culver City) we went to the next day, given the more creative flavors",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Decent place. More hip/ster feeling than I expected it to be\n\nDrinks were ok- we got 2 and not super memorable; I remember them being packed with ice. Tacos we got (short ribs, sweet potato, and octopus) were really tasty & a very different blend of flavors! The best one was the octopus taco.\n\nMy friend liked this place better than Etta (in Culver City) we went to the next day, given the more creative flavors",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Jenna RxTravelBug",
            "uri": "https://www.google.com/maps/contrib/111054879152752803419/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVPgLkhwF6yxAhKQW9PlgIjK6jLOmHZSOiUxbtzB7A1SAuApJaB=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-06-05T01:52:42.541157Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/photos/AdCG2DNGEDSTJEDT5x7T_UFyJY9wTwG5buqvlM-59NmflFVJybaKQv9q5tMKxAVmCDaiqwaOrmmuy-DFC3k7HEzGfXrsNAte5iOOxb3su3fr_eJSspQRJ3sS-1NC_ACgxL9Am12JBgn9dkqZZoVkIthdwsqXoWPb9C6wj8G7",
          "widthPx": 1537,
          "heightPx": 2049,
          "authorAttributions": [
            {
              "displayName": "Guerrilla Tacos",
              "uri": "https://maps.google.com/maps/contrib/102785621621391257844",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWUrAmyObdeR0EVGr7iL8dp-VbfsFwTquoKVLw3pVttVRyUcUQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/photos/AdCG2DPLYjdL7xF7ghjrNHJYiuKE-lDr2Ti83mbe8TD_y42UtJEbSfFp7S54DoFOxQXngwj7BW6aj5-JcLFXChCy__UINxwpaE0Oh3tYeuLY_RJkBTKLYb1wYSgbLjs2mRTD2GMDHO_H70iY816JV0M5xfpCgjYDsKE2xodQ",
          "widthPx": 593,
          "heightPx": 592,
          "authorAttributions": [
            {
              "displayName": "Guerrilla Tacos",
              "uri": "https://maps.google.com/maps/contrib/102785621621391257844",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWUrAmyObdeR0EVGr7iL8dp-VbfsFwTquoKVLw3pVttVRyUcUQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/photos/AdCG2DNTOwzRP-r09P2guCqF27H7DZqj3uXveWGenHZ3ftaFv3v5E1KcjcLI-yMX5xJFqS2q52RbPyH2RfpsL-ti17pYGVWpaXwZOD0KmSkXp0ukkN6lzRtT5xi0WsnG5IPTfM-3wQ2owlOHzXozrqhKBiKaRql-RymBZOip",
          "widthPx": 3600,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Arthur Bouffard",
              "uri": "https://maps.google.com/maps/contrib/104000580830693724711",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVuDm8_iTy3AurwTwT6hEww-FnCpPBPlIjiinhdVdray9lIWp0Y4Q=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/photos/AdCG2DNXStS2eMhXU-jN8a6G9IuqfeM0EWb91ujA5RAEqe5cPCKgzMgje5G8qtxrOsjEzsSykYUhffE5lpAxPqgGoPhki87zm_QzsEAW1HCkDSXSgz62hVda5Bp-kICSmjwJoOkf4eVxB9TR11pyZmDL5K0w71D2tgzL6i__",
          "widthPx": 4000,
          "heightPx": 3000,
          "authorAttributions": [
            {
              "displayName": "Uri nun",
              "uri": "https://maps.google.com/maps/contrib/115254453532652688548",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjV5LYjGNVAqi8b24K7ZNdxpmv8lWmSCFH7tAqwTi5OTNzUqOYh3=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/photos/AdCG2DMtRQSDqed_gOebB3XvpMfQiBlF10S1GZdrlkq-QSJ9jG6BG2_J_OgIY-vy5fAvrIPnSjE9VEdCOke-BS7htbH7Px6Kro49LE6bYXlBZEzvMJgGn4T-Els8GoCNe_vOzdgUuynUic5fV7vV-fXQ5Qh8mgh0HbbmTGKY",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Christopher Roman",
              "uri": "https://maps.google.com/maps/contrib/100570445930209480166",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocILCm_gODaARHbB9vIAQ9UjmsNs4WBMVtn1MipkcqK7lqaXKA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/photos/AdCG2DOgEE4qaaSqpGzUyws7WS3NnqySXlLiAPwY4VWRVXoIkkTsRCKp1QJOOibThHjUYve-XMkgYfHBS9T8Orb5OB7uYZQmfUnqlx2o96SbY63Gb3nt3zFMnRvCqoUKBntF4AKcac2DqP5QXx2Py5rW0a9UT8QCiQR8Hb23",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Mike Won",
              "uri": "https://maps.google.com/maps/contrib/110701937973155646980",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU2WKJVMSd5PgKdlJcefYgw65uVl6FUnQO4YrJ4gzJpUbeNmtJy=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/photos/AdCG2DON3dMvWHfnVBFQqPNB4QRIN-2mnoIFvUakym4MoVTSQVmZRKx2f_QP_OXlDhkg7xeMTFn8rfPiXOD4jHwCf6dV0fhe00qU9EDy0HWXyazKyNdcUu1r72FTG7G9KtDt3efOTMb4mp658KsZCGpomBCCrs1WOARNt4GZ",
          "widthPx": 3024,
          "heightPx": 3648,
          "authorAttributions": [
            {
              "displayName": "May Xoxooo",
              "uri": "https://maps.google.com/maps/contrib/100498337643327877349",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVMdp8SAQOupP4RFYi88Yy5xfBI_kv0DcMwzoYMhyy4g9fI0TTA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/photos/AdCG2DOgzTFvww-A6cxfcr_RzGaome1jMOiZNK-eWwSBd-DMovm6YwGX7VGi-Dv9_p8DC1iAvI-v-Kwm_2FQTLXRMDhKcPzKZZ2r8SHPKJbzJRrcmuR389x3LXMcEorIZMIQzkXx2LuXMrntjB2COmy4lK12BUIv4rt9_vE3",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "EAM Vibing",
              "uri": "https://maps.google.com/maps/contrib/116229455988403294354",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjX4fG2pLeYKg5liz5pDDej_sGJp5IFloXotL4Y5JKxH20-rxmSe=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/photos/AdCG2DPiTXDPiOvN9-irEWyK8QAmEkH0kRQldiGhaJOhGQIj3Go9Dy6HFB2tDW16OR_EthLcUmCx6CXVpUsgQP4UB9vkolLJrS8KM2JcOMroa8JsRMEle_FksHNEhB-3yOoAuQYWWqp6NbRkiYPukl4Vf5qKhiDVqlzmH-gQ",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "C B",
              "uri": "https://maps.google.com/maps/contrib/107331235241330308808",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjV8FFRMveL_9iDkK-gnXq6M6_zBlmZINbsAMcb93RVLEokYe4rWOw=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/photos/AdCG2DML152orjenSJadERLJJcorBQqgrakMI6eMSEkmh5b8aWu8zDEO4zjDiL2pu436CU-VExx-h7-nH1TQgI30eNeVMHMfhU7yH3C0SDs4AFHRjMRKX7O8VfOBpHwjKQrnYB8aDNyLZk1sEc-Htap9zMMPrACdCrKghTYu",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Armand",
              "uri": "https://maps.google.com/maps/contrib/105289569007774415774",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVbg4Rvl2zwKm6h5kybPyCvsATX4uiUsxjnYvyFetT0Ui6AMMTD=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "liveMusic": False,
      "menuForChildren": False,
      "servesCocktails": True,
      "servesDessert": True,
      "servesCoffee": True,
      "goodForChildren": True,
      "restroom": True,
      "goodForGroups": True,
      "goodForWatchingSports": False,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "parkingOptions": {
        "paidParkingLot": True,
        "freeStreetParking": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleRestroom": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Cozy spot with a full bar offering gourmet tacos plus beer, cocktails and wine.",
          "languageCode": "en-US"
        },
        "description": {
          "text": "Beloved Fashion District taco restaurant offering elevated Mexican comfort food, plus vegetarian and organic items.\nPeople love the unique taco offerings, which include sweet potato, cod, and wild boar, as well as the potato taquitos and the pork belly tacos. The drinks menu features cocktails like the horchata-inspired Bachata.\nThe cozy, quaint setting is good for kids and solo diners, and the service is generally fast.\nCustomers typically spend $20–30.",
          "languageCode": "en-US"
        },
        "references": {
          "reviews": [
            {
              "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/reviews/ChZDSUhNMG9nS0VJQ0FnSUN4M19IcmVnEAE",
              "relativePublishTimeDescription": "a year ago",
              "rating": 5,
              "text": {
                "text": "The taste of the tacos is incomparable, the place is very clean and the service is super fast.",
                "languageCode": "en"
              },
              "originalText": {
                "text": "The taste of the tacos is incomparable, the place is very clean and the service is super fast.",
                "languageCode": "en"
              },
              "authorAttribution": {
                "displayName": "Tanya Padro",
                "uri": "https://www.google.com/maps/contrib/116169296875404315968/reviews",
                "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWLKw8IeLouKMBPb4sQ54WiU6DIJAkzZQfpjUrJ-hbmxTBvSi4T=s128-c0x00000000-cc-rp-mo"
              },
              "publishTime": "2023-05-29T17:19:32.594672Z"
            },
            {
              "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/reviews/ChZDSUhNMG9nS0VJQ0FnSUNKNGJYSlFBEAE",
              "relativePublishTimeDescription": "a year ago",
              "rating": 4,
              "text": {
                "text": "Elevated tacos. Interesting choices like wild boar. However, not worth $8 apiece.\n\nBachata cocktail was delicious. Like an alcoholic horchata with mint.",
                "languageCode": "en"
              },
              "originalText": {
                "text": "Elevated tacos. Interesting choices like wild boar. However, not worth $8 apiece.\n\nBachata cocktail was delicious. Like an alcoholic horchata with mint.",
                "languageCode": "en"
              },
              "authorAttribution": {
                "displayName": "Graham Helmich",
                "uri": "https://www.google.com/maps/contrib/111678305330291302833/reviews",
                "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWCDJw6CJhiHq9wcdNpYp1sF7aO5kmjehwIWxA6FrmoldmHLnw=s128-c0x00000000-cc-rp-mo-ba3"
              },
              "publishTime": "2023-06-29T01:29:35.012873Z"
            },
            {
              "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/reviews/ChZDSUhNMG9nS0VJQ0FnSURKemNPM1VnEAE",
              "relativePublishTimeDescription": "a year ago",
              "rating": 5,
              "text": {
                "text": "10 out of 10 for sure! Very quaint, food was exceptional and the service was top notch. It’s recommended by Michelin for a reason, highly recommend this spot!",
                "languageCode": "en"
              },
              "originalText": {
                "text": "10 out of 10 for sure! Very quaint, food was exceptional and the service was top notch. It’s recommended by Michelin for a reason, highly recommend this spot!",
                "languageCode": "en"
              },
              "authorAttribution": {
                "displayName": "Eyris Polzine",
                "uri": "https://www.google.com/maps/contrib/105713224093570286848/reviews",
                "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjW9lmcI7UhisjisMe_MT_KgRCngOvOgX8WLKCjBaUoFuDJZktUrBA=s128-c0x00000000-cc-rp-mo-ba4"
              },
              "publishTime": "2023-07-22T00:05:38.954267Z"
            },
            {
              "name": "places/ChIJvQRXWpy5woARXF1TL3dFJAU/reviews/ChZDSUhNMG9nS0VJQ0FnSUR4NE5hc2Z3EAE",
              "relativePublishTimeDescription": "a year ago",
              "rating": 5,
              "text": {
                "text": "This is what I'm talking about really Mexican food great\nWe need something like this in Dallas",
                "languageCode": "en"
              },
              "originalText": {
                "text": "This is what I'm talking about really Mexican food great\nWe need something like this in Dallas",
                "languageCode": "en"
              },
              "authorAttribution": {
                "displayName": "Hector Gomez",
                "uri": "https://www.google.com/maps/contrib/101043639280034127420/reviews",
                "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU71BWHQUmbyr0yi-3eu-aW_PFyrcLXtqVRj-9ql7QtMAU-99Hj=s128-c0x00000000-cc-rp-mo"
              },
              "publishTime": "2023-05-30T15:39:49.055390Z"
            }
          ]
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJISSAeSHGwoARcYfGTQ9ryy4",
            "placeId": "ChIJISSAeSHGwoARcYfGTQ9ryy4",
            "displayName": {
              "text": "Everson Royce Bar",
              "languageCode": "en"
            },
            "types": [
              "bar",
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 35.720715,
            "travelDistanceMeters": 33.133247
          },
          {
            "name": "places/ChIJMRSMhSHGwoAR5UrfQ8NW9Qo",
            "placeId": "ChIJMRSMhSHGwoAR5UrfQ8NW9Qo",
            "displayName": {
              "text": "PIZZANISTA! DTLA Arts District",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "food",
              "point_of_interest",
              "restaurant"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 61.59515,
            "travelDistanceMeters": 86.00065
          },
          {
            "name": "places/ChIJERRXhiHGwoARglmCKcSc30o",
            "placeId": "ChIJERRXhiHGwoARglmCKcSc30o",
            "displayName": {
              "text": "Tony's Saloon",
              "languageCode": "en"
            },
            "types": [
              "bar",
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 57.983463,
            "travelDistanceMeters": 74.24549
          },
          {
            "name": "places/ChIJ0eakYiHGwoARtqqGBaRMaCM",
            "placeId": "ChIJ0eakYiHGwoARtqqGBaRMaCM",
            "displayName": {
              "text": "Artist & Craftsman Supply Downtown LA",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 90.88179,
            "travelDistanceMeters": 96.80329
          },
          {
            "name": "places/ChIJewJ2Uk7HwoAReFuG3E07u-s",
            "placeId": "ChIJewJ2Uk7HwoAReFuG3E07u-s",
            "displayName": {
              "text": "Seventh/Place",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 119.94509,
            "travelDistanceMeters": 129.6657
          }
        ],
        "areas": [
          {
            "name": "places/ChIJf_9O_SzGwoARtrkWOBLCwII",
            "placeId": "ChIJf_9O_SzGwoARtrkWOBLCwII",
            "displayName": {
              "text": "Fashion District",
              "languageCode": "en"
            },
            "containment": "OUTSKIRTS"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA",
      "id": "ChIJ-7gl0h3HwoARk2xsigncEmA",
      "types": [
        "mexican_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 536-5287",
      "internationalPhoneNumber": "+1 213-536-5287",
      "formattedAddress": "800 W Olympic Blvd, Los Angeles, CA 90015, USA",
      "addressComponents": [
        {
          "longText": "800",
          "shortText": "800",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "West Olympic Boulevard",
          "shortText": "W Olympic Blvd",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90015",
          "shortText": "90015",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632PVP+X2",
        "compoundCode": "2PVP+X2 Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.044997599999995,
        "longitude": -118.26498049999998
      },
      "viewport": {
        "low": {
          "latitude": 34.0434992697085,
          "longitude": -118.26686363029147
        },
        "high": {
          "latitude": 34.0461972302915,
          "longitude": -118.26416566970849
        }
      },
      "rating": 4.6,
      "googleMapsUri": "https://maps.google.com/?cid=6922837510757051539",
      "websiteUri": "http://www.solagave.com/",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 1,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 11:00 AM – 10:00 PM",
          "Tuesday: 11:00 AM – 10:00 PM",
          "Wednesday: 11:00 AM – 10:00 PM",
          "Thursday: 11:00 AM – 10:00 PM",
          "Friday: 11:00 AM – 10:00 PM",
          "Saturday: 11:00 AM – 10:00 PM",
          "Sunday: 11:00 AM – 10:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e800 W Olympic Blvd\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90015\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_MODERATE",
      "userRatingCount": 645,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Sol Agave LA LIVE",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "reservable": True,
      "servesBreakfast": True,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": True,
      "servesWine": True,
      "servesBrunch": True,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 11:00 AM – 10:00 PM",
          "Tuesday: 11:00 AM – 10:00 PM",
          "Wednesday: 11:00 AM – 10:00 PM",
          "Thursday: 11:00 AM – 10:00 PM",
          "Friday: 11:00 AM – 10:00 PM",
          "Saturday: 11:00 AM – 10:00 PM",
          "Sunday: 11:00 AM – 10:00 PM"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "Lucky Strike Bowling - Los Angeles, 800 W Olympic Blvd, Los Angeles",
      "editorialSummary": {
        "text": "Laid-back outlet supplying cocktails & Mexican provisions in an airy dining room.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/reviews/ChZDSUhNMG9nS0VJQ0FnSUNubmEzdlFnEAE",
          "relativePublishTimeDescription": "2 weeks ago",
          "rating": 4,
          "text": {
            "text": "Recently went here for a work dinner. The atmosphere was nice. Unfortunately all of our food was only so-so for various reasons. The chips/salsa/ guacamole were good. My margarita was decent. Still a decent option when dining over by crypto.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Recently went here for a work dinner. The atmosphere was nice. Unfortunately all of our food was only so-so for various reasons. The chips/salsa/ guacamole were good. My margarita was decent. Still a decent option when dining over by crypto.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Kim",
            "uri": "https://www.google.com/maps/contrib/103100373618904984367/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWjvQrdl6SV3DJ_7adBO3igGJ3MSp0nO3vCMp9v3D-QTIjgxp-I=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-09-28T20:16:12.034733Z"
        },
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/reviews/ChZDSUhNMG9nS0VJQ0FnSUNUaFozTkdnEAE",
          "relativePublishTimeDescription": "5 months ago",
          "rating": 5,
          "text": {
            "text": "I had a photo gig at Nova Theatre and needed to grab a quick bite to eat to soothe the hungry demon inside my body. I did a full lap around LA Live looking for a happy hour deal. After navigating through a bunch of exuberant priced options ($19.99 for a Smash Burger, eh, no thanks) I found Sol Agave. Not only did they have happy hour, but they had amazing options with great prices (and free chips and salsa). Needless to say one chips and salsa, two soda waters and two chicken taquitos later I was satisfied and ready for work. I highly recommend this spot, if I was drinking I would’ve taken full advantage of their $9 margarita or $7 beers. The food was great, the happy hour menu was incredible, and the vibes were on point. Not sure we I’ll be back to LA Live, but when I do this will be the place to go.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "I had a photo gig at Nova Theatre and needed to grab a quick bite to eat to soothe the hungry demon inside my body. I did a full lap around LA Live looking for a happy hour deal. After navigating through a bunch of exuberant priced options ($19.99 for a Smash Burger, eh, no thanks) I found Sol Agave. Not only did they have happy hour, but they had amazing options with great prices (and free chips and salsa). Needless to say one chips and salsa, two soda waters and two chicken taquitos later I was satisfied and ready for work. I highly recommend this spot, if I was drinking I would’ve taken full advantage of their $9 margarita or $7 beers. The food was great, the happy hour menu was incredible, and the vibes were on point. Not sure we I’ll be back to LA Live, but when I do this will be the place to go.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "chris m",
            "uri": "https://www.google.com/maps/contrib/100897155122826938582/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUGzgkhZJJpEal1BuGm4eFtp8DkO2FhdHTa58yqLVudMnzKCSs=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-05-17T01:11:55.406988Z"
        },
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/reviews/ChdDSUhNMG9nS0VJQ0FnSURINGNMUnV3RRAB",
          "relativePublishTimeDescription": "a month ago",
          "rating": 5,
          "text": {
            "text": "The food and atmosphere were great! We had Jose helping us and he gave us excellent service. I ordered the sugar cane filet and we shared a margarita flight. I was unsure what to think of the filet at first bite (I’ve never had anything like it) but it was delicious! I finished it all! The margarita flight was tasty and the mango drink was definitely the winner. Would come again ☺️",
            "languageCode": "en"
          },
          "originalText": {
            "text": "The food and atmosphere were great! We had Jose helping us and he gave us excellent service. I ordered the sugar cane filet and we shared a margarita flight. I was unsure what to think of the filet at first bite (I’ve never had anything like it) but it was delicious! I finished it all! The margarita flight was tasty and the mango drink was definitely the winner. Would come again ☺️",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Kathy C",
            "uri": "https://www.google.com/maps/contrib/102686263646088774866/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocI3gbikNWoPZamP0Z7l0hKonBYxyegQg3gHLrylN16eaoaqHA=s128-c0x00000000-cc-rp-mo-ba2"
          },
          "publishTime": "2024-09-16T22:00:29.369532Z"
        },
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/reviews/ChdDSUhNMG9nS0VJQ0FnSUNUN2VMQzNnRRAB",
          "relativePublishTimeDescription": "5 months ago",
          "rating": 5,
          "text": {
            "text": "February 16, 2024-\n#latepost\nWe had Veggie Aztech Quesadilla, Pollo Al Gusto with Spicy mole sauce, and Spicy Mango Sol Agave Margarita. Everything was really good. The place had a party vibe. The staff were super nice and respectful.\n\nI'm very happy to see the vegetarian column in the menu🥹",
            "languageCode": "en"
          },
          "originalText": {
            "text": "February 16, 2024-\n#latepost\nWe had Veggie Aztech Quesadilla, Pollo Al Gusto with Spicy mole sauce, and Spicy Mango Sol Agave Margarita. Everything was really good. The place had a party vibe. The staff were super nice and respectful.\n\nI'm very happy to see the vegetarian column in the menu🥹",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Sri Lekha",
            "uri": "https://www.google.com/maps/contrib/103918899362796134847/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjV7KLbEniKtEsoVeSblpHEkbCdmsETLBrQpYA708MA0FVYZ2Qxgdw=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-05-17T23:22:18.548366Z"
        },
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/reviews/ChZDSUhNMG9nS0VJQ0FnSURyeFBpYVBBEAE",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 4,
          "text": {
            "text": "The food was good. Chips were warm and seasoned with a chipotle salsa and refried beans with cheese! 👌👌 My girls liked their chicken tenders, which were grilled not fried. I had the Mar y Tierra Enchiladas; 2 Filet Mignon filled enchiladas with 2 grilled shrimp and a side rice. The enchiladas were delicious! They had a very yummy sauce on them 😋 and the rice was 🔥🔥🔥 My wife had the Sugar Cane Filet's, which are on the appetizer part of the menu, but boy we're these GOOOOOD!!! 🙌🔥🔥🔥 These were 3 filet cuts with an actual sugar cane and tamarindo marinade on them, definitely a must taste! We drank them down with a Frozen Coconut Margarita 😱😎👌 and a Tamarindo Margarita with a Tajin rim 👍👍 we were here on a slow Sunday afternoon, so the food came out fairly quick and the atmosphere was very chill and easy going. There was a live mariachi playing when we walked in, but we caught the tail end of their performance. The music continued with a mix of Spanish music the rest of the time. It's a nice place to eat, not a party vibe type of environment. Everything is kept very simple. Will give it 4 stars ⭐⭐⭐⭐",
            "languageCode": "en"
          },
          "originalText": {
            "text": "The food was good. Chips were warm and seasoned with a chipotle salsa and refried beans with cheese! 👌👌 My girls liked their chicken tenders, which were grilled not fried. I had the Mar y Tierra Enchiladas; 2 Filet Mignon filled enchiladas with 2 grilled shrimp and a side rice. The enchiladas were delicious! They had a very yummy sauce on them 😋 and the rice was 🔥🔥🔥 My wife had the Sugar Cane Filet's, which are on the appetizer part of the menu, but boy we're these GOOOOOD!!! 🙌🔥🔥🔥 These were 3 filet cuts with an actual sugar cane and tamarindo marinade on them, definitely a must taste! We drank them down with a Frozen Coconut Margarita 😱😎👌 and a Tamarindo Margarita with a Tajin rim 👍👍 we were here on a slow Sunday afternoon, so the food came out fairly quick and the atmosphere was very chill and easy going. There was a live mariachi playing when we walked in, but we caught the tail end of their performance. The music continued with a mix of Spanish music the rest of the time. It's a nice place to eat, not a party vibe type of environment. Everything is kept very simple. Will give it 4 stars ⭐⭐⭐⭐",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Gilbert Ayon",
            "uri": "https://www.google.com/maps/contrib/111282548864909885463/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWJKHt9FQy0g-3z5yD7a6dpicNFCzkZNht7CUQFZXv1crxG9NLb=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-07-14T22:28:22.895031Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/photos/AdCG2DPPSM36d9dguj6jgvs55caxZDee3Y8UAh_f57t7r2Vv1ZjbGcwWhG5n7SeHeJdxY60uf-9dUx9HxCops7Xm5C03r37b4lI5NfwLtYwpFLXBecAosp5D0orvGoAJYySndrYs5edHXHKyZjoNzsBVLXAcVBk8EhleuiI2",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Sol Agave LA LIVE",
              "uri": "https://maps.google.com/maps/contrib/107274768802810830572",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjViQNP73jCL74pKqZTITIWe8wZu8pgUsQa3cyNev1cgB6ZUvko=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/photos/AdCG2DP9ocfhTtTKwYfjn84WPvILWmYhlIhNxUnI9b-ex1pKJTjPawByBNw64UdF487GdX80u--qLuUlNAEnrCH97g9svlj4pqcH4LSCcBvghwX7W3i6VwmuhaEHf2N6ta98B29qm5grWsfQqQVgPqUOrmmkvFmNR7XbCzmF",
          "widthPx": 1170,
          "heightPx": 773,
          "authorAttributions": [
            {
              "displayName": "Sol Agave LA LIVE",
              "uri": "https://maps.google.com/maps/contrib/107274768802810830572",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjViQNP73jCL74pKqZTITIWe8wZu8pgUsQa3cyNev1cgB6ZUvko=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/photos/AdCG2DP4BRoDbaXADynsH_eRtpo0yh48iXUHOEWKU_-BBibVFogiL0M5sxU1hMYEWkuiP7QDqz6gF8uhKjyKR8MZ_kfbyr9LDKAqvvyYZ7i3K9x3sSya9T-m2I55V-jNhBmdtsBSYJPrPpwqjU5ajFGU3nXfu4jws86VCcxV",
          "widthPx": 4624,
          "heightPx": 2608,
          "authorAttributions": [
            {
              "displayName": "Norma Edith Aguilar",
              "uri": "https://maps.google.com/maps/contrib/112472043715351947433",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjX7ifNtS7E65Zxwg8WDUR8Cy3JRG3LcGYugtNvTdMCNO0q6sa4MPQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/photos/AdCG2DN14t_WU6B78PL5_D7J8xJif_PKuKf43Jdl9U9n9GdKwG_tRENbHDcLUFJuWSOriHw98Z1rqUyqyvABvvUDi0932ToRP_pF2LJCWRVsVKfMuHpABZDer68k6HtV19ngkR1XZrcKRlKFrmpaknS2yv4lfirNQ59qdIjq",
          "widthPx": 4800,
          "heightPx": 3600,
          "authorAttributions": [
            {
              "displayName": "Kathy C",
              "uri": "https://maps.google.com/maps/contrib/102686263646088774866",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocI3gbikNWoPZamP0Z7l0hKonBYxyegQg3gHLrylN16eaoaqHA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/photos/AdCG2DNx84S4WcZdn2ypR1BkDdpQhb3V9wmSO0A4Kafm_l8te4odiXo_JYevft4TtBckIOt7_CyidfWy9G7iNS4dPCLhqS2N4uMp5ZwlGksJg_g5Ad5IxmoF6KMuyER8LNGLwhZg6Rzr5wXO7dDJnHk4RiH4DLaplNdSAhv5",
          "widthPx": 1848,
          "heightPx": 2655,
          "authorAttributions": [
            {
              "displayName": "Sri Lekha",
              "uri": "https://maps.google.com/maps/contrib/103918899362796134847",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjV7KLbEniKtEsoVeSblpHEkbCdmsETLBrQpYA708MA0FVYZ2Qxgdw=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/photos/AdCG2DOKqXedpoJeF-ADZdfbZSSah3LoT-W-yymxVT9v9qApP7b_QU4UaL9a3oLwlXJ7bMddWlSIU5gqcnfwx4WDLKPG4F2tqMHToyPnoYmgiZp-wIYPUSvUqiNM2hYF63XTDvwhIapEx8sxeCRTLHxoO2fczgrf8Ni8BzMJ",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Halé Richardson",
              "uri": "https://maps.google.com/maps/contrib/113673504028689320241",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjW2FG-h3ny7fm27YPBMxWMtQ7pMFNz-astT4033bJxbBJibjCY3=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/photos/AdCG2DNy-V-PrFp17HL-rSn8WVGEDtM0PU3XMowhr9V-TrltMTz4ORO0uXwgdPqNoJwBbBnrIl_ItXolCrYfYmNzLlc7My8NObJ6aqahN07tTstOIlBtrsHXwhVt9TmJHePSjBd83wZRDb04tAVy-pZaleZDXR5-gsoP12iC",
          "widthPx": 4800,
          "heightPx": 3600,
          "authorAttributions": [
            {
              "displayName": "Krishna R",
              "uri": "https://maps.google.com/maps/contrib/114158597563997625039",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocIrmWPhWgPYDVlJ6-d-l99908enpOe4653q37WOfddPzNtSrw=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/photos/AdCG2DNZ7ycneQ_HPN68EPfbjpTebSl75sz3ic2dFNtxoQrQ3jhWPJb-NR6qVP_y8isR4GaBv_szKgVUq3k7PzvXN3l2fmMP0VkL1r8Am7BHSGfDosQ9RJZCTD2LBH23fRLbgTGH1ZX72AfK9DtoJSARsW9rdX1_JUc4_HJu",
          "widthPx": 4080,
          "heightPx": 3072,
          "authorAttributions": [
            {
              "displayName": "Domin Lee",
              "uri": "https://maps.google.com/maps/contrib/100337154999618996858",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWCg106cH187DP6iUWEg6GWa3Ml2wcHu2dDx7gdrX3WT4Fkd1tBAg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/photos/AdCG2DMvHVzK1BPhT6BfkeJTEds4tcLn318Hso8SbSNXxC3KCC9pntzmyiqrVU2tBG1Nw-1BDlx4zms49WXJcklzN3_-quQPcLEkGtCQuT2XfL1qGeOsSRnYHxr4NYxTVopesZJdaVGvUP0NrLSz5CDbt_BIqn5s9SxT0t6r",
          "widthPx": 3024,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Hannah Lin",
              "uri": "https://maps.google.com/maps/contrib/117610017957737354338",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLqQz2NZ4co2R_oMk5Fj4sO-BIJP9IU0va7HAQtvEtZElAJ2dY=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ-7gl0h3HwoARk2xsigncEmA/photos/AdCG2DMbUO3lHVmFFWqSsHFyhTRwBgyI-PxC7bbo3AbltsJtL4ErpRaeKVsQNiwuCHAzKadpUj2VmH9XpQ8pbQ4tyN8JArkvcdeUr4VU7fbEF6Vw0cGyUw-_WGooU4w8igly64XvBa1j0NeBFZq2YR8ilLWSNvozEUDrByfZ",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Jose Soto",
              "uri": "https://maps.google.com/maps/contrib/114580282812929050791",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXGmdOTOdRzXy4fzTA1Fwh_YrNbNZG6f8rSOwT2oxJENtcC9O9G=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "liveMusic": False,
      "menuForChildren": True,
      "servesCocktails": True,
      "servesDessert": True,
      "servesCoffee": True,
      "goodForChildren": True,
      "restroom": True,
      "goodForGroups": True,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "parkingOptions": {
        "paidParkingLot": True,
        "paidStreetParking": True,
        "paidGarageParking": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleParking": True,
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleRestroom": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Authentic Mexican dishes get a contemporary tweak at this trendy restaurant and bar.",
          "languageCode": "en-US"
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJuYQ2SbjHwoARC4aaAnD6xp0",
            "placeId": "ChIJuYQ2SbjHwoARC4aaAnD6xp0",
            "displayName": {
              "text": "L.A. Live",
              "languageCode": "en"
            },
            "types": [
              "bar",
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "WITHIN",
            "straightLineDistanceMeters": 44.75406,
            "travelDistanceMeters": 186.07777
          },
          {
            "name": "places/ChIJG5wBgrfHwoAR9hEdmF4WsH4",
            "placeId": "ChIJG5wBgrfHwoAR9hEdmF4WsH4",
            "displayName": {
              "text": "GRAMMY Museum L.A. Live",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "museum",
              "point_of_interest",
              "tourist_attraction"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 48.988808,
            "travelDistanceMeters": 75.55821
          },
          {
            "name": "places/ChIJkyrqXbjHwoAR1bJ76zx89B8",
            "placeId": "ChIJkyrqXbjHwoAR1bJ76zx89B8",
            "displayName": {
              "text": "Crypto.com Arena",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest",
              "stadium"
            ],
            "straightLineDistanceMeters": 303.90988,
            "travelDistanceMeters": 312.06473
          },
          {
            "name": "places/ChIJzcQQfbfHwoAREpay4PPzicU",
            "placeId": "ChIJzcQQfbfHwoAREpay4PPzicU",
            "displayName": {
              "text": "Hotel Figueroa - The Unbound Collection by Hyatt",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "lodging",
              "point_of_interest"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 108.582436,
            "travelDistanceMeters": 134.77448
          },
          {
            "name": "places/ChIJG5wBgrfHwoARMDbFw76Fl9o",
            "placeId": "ChIJG5wBgrfHwoARMDbFw76Fl9o",
            "displayName": {
              "text": "The Novo",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 44.06758,
            "travelDistanceMeters": 131.89201
          }
        ],
        "areas": [
          {
            "name": "places/ChIJN28nbMjHwoAR0mBlu0518tE",
            "placeId": "ChIJN28nbMjHwoAR0mBlu0518tE",
            "displayName": {
              "text": "South Park",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY",
      "id": "ChIJwwLzhN_HwoARrpfr7VNhGuY",
      "types": [
        "mexican_restaurant",
        "steak_house",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 988-7053",
      "internationalPhoneNumber": "+1 213-988-7053",
      "formattedAddress": "800 W 6th St, Los Angeles, CA 90017, USA",
      "addressComponents": [
        {
          "longText": "800",
          "shortText": "800",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "West 6th Street",
          "shortText": "W 6th St",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90017",
          "shortText": "90017",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "2704",
          "shortText": "2704",
          "types": [
            "postal_code_suffix"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85633P2R+2R",
        "compoundCode": "3P2R+2R Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.0500173,
        "longitude": -118.25789290000002
      },
      "viewport": {
        "low": {
          "latitude": 34.0487862697085,
          "longitude": -118.25909633029148
        },
        "high": {
          "latitude": 34.0514842302915,
          "longitude": -118.25639836970849
        }
      },
      "rating": 3.7,
      "googleMapsUri": "https://maps.google.com/?cid=16580671991219722158",
      "websiteUri": "https://www.mamapordios.com/",
      "regularOpeningHours": {
        "openNow": False,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 1,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 0,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 17,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 0,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 5:00 – 10:00 PM",
          "Tuesday: 5:00 – 10:00 PM",
          "Wednesday: 5:00 – 10:00 PM",
          "Thursday: 5:00 – 10:00 PM",
          "Friday: 5:00 PM – 12:00 AM",
          "Saturday: 5:00 PM – 12:00 AM",
          "Sunday: 5:00 – 10:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e800 W 6th St\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90017-2704\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_MODERATE",
      "userRatingCount": 241,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Mama Por Dios - DTLA",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "curbsidePickup": False,
      "reservable": True,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": True,
      "servesWine": True,
      "currentOpeningHours": {
        "openNow": False,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 6,
              "hour": 0,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 17,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 0,
              "hour": 0,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 5:00 – 10:00 PM",
          "Tuesday: 5:00 – 10:00 PM",
          "Wednesday: 5:00 – 10:00 PM",
          "Thursday: 5:00 – 10:00 PM",
          "Friday: 5:00 PM – 12:00 AM",
          "Saturday: 5:00 PM – 12:00 AM",
          "Sunday: 5:00 – 10:00 PM"
        ]
      },
      "currentSecondaryOpeningHours": [
        {
          "openNow": False,
          "periods": [
            {
              "open": {
                "day": 0,
                "hour": 11,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 20
                }
              },
              "close": {
                "day": 0,
                "hour": 14,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 20
                }
              }
            },
            {
              "open": {
                "day": 6,
                "hour": 11,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 19
                }
              },
              "close": {
                "day": 6,
                "hour": 14,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 19
                }
              }
            }
          ],
          "weekdayDescriptions": [
            "Monday: Closed",
            "Tuesday: Closed",
            "Wednesday: Closed",
            "Thursday: Closed",
            "Friday: Closed",
            "Saturday: 11:00 AM – 2:00 PM",
            "Sunday: 11:00 AM – 2:00 PM"
          ],
          "secondaryHoursType": "LUNCH"
        }
      ],
      "regularSecondaryOpeningHours": [
        {
          "openNow": False,
          "periods": [
            {
              "open": {
                "day": 0,
                "hour": 11,
                "minute": 0
              },
              "close": {
                "day": 0,
                "hour": 14,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 6,
                "hour": 11,
                "minute": 0
              },
              "close": {
                "day": 6,
                "hour": 14,
                "minute": 0
              }
            }
          ],
          "weekdayDescriptions": [
            "Monday: Closed",
            "Tuesday: Closed",
            "Wednesday: Closed",
            "Thursday: Closed",
            "Friday: Closed",
            "Saturday: 11:00 AM – 2:00 PM",
            "Sunday: 11:00 AM – 2:00 PM"
          ],
          "secondaryHoursType": "LUNCH"
        }
      ],
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "800 W 6th St, Los Angeles",
      "reviews": [
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/reviews/ChZDSUhNMG9nS0VJQ0FnSUNuMnBEWmNnEAE",
          "relativePublishTimeDescription": "3 weeks ago",
          "rating": 2,
          "text": {
            "text": "We went expecting Mama x Dios vibe, and is not, sadly!. It's a whole different restaurant, with part of the same menu.\n\nService was great!. Marcos was very attentive. Classic and Tamarindo Margaritas were great!, food as well. Guacamole with chicharon and ribeye, tacos de birria,  and tacos de asada prime...were exceptional!.\nFor dessert we had the lemon mousse, and the tres leches...$19.50 each. Lemon mousse had a great flavor and texture,  but the portion is pretty small. Tres leches was dry and flavorless.\n\nThe salon is spacious, well decorated; an upscale restaurant,  but music was atrocious,  we listened regueton for more than an hour...the least genre i want to hear when I'm going to pay $200 to eat. That simple detail ruined my experience.\nIf you're looking for the True Mama x Dios Vibe, visit Rancho Cucamonga.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "We went expecting Mama x Dios vibe, and is not, sadly!. It's a whole different restaurant, with part of the same menu.\n\nService was great!. Marcos was very attentive. Classic and Tamarindo Margaritas were great!, food as well. Guacamole with chicharon and ribeye, tacos de birria,  and tacos de asada prime...were exceptional!.\nFor dessert we had the lemon mousse, and the tres leches...$19.50 each. Lemon mousse had a great flavor and texture,  but the portion is pretty small. Tres leches was dry and flavorless.\n\nThe salon is spacious, well decorated; an upscale restaurant,  but music was atrocious,  we listened regueton for more than an hour...the least genre i want to hear when I'm going to pay $200 to eat. That simple detail ruined my experience.\nIf you're looking for the True Mama x Dios Vibe, visit Rancho Cucamonga.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "G Quiñones",
            "uri": "https://www.google.com/maps/contrib/113907372669690435254/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocIGuyCVIcMfgGbT6YzcyHnGMWkHAeoq18bfPcBxfMKwAnBzww=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-09-25T05:10:11.028562Z"
        },
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/reviews/ChZDSUhNMG9nS0VJQ0FnSUNuaUxfd1VBEAE",
          "relativePublishTimeDescription": "3 weeks ago",
          "rating": 5,
          "text": {
            "text": "Mama Por Dios offers an unforgettable dining experience with its vibrant atmosphere and delectable food. From the moment you step in, you’re greeted by a lively ambiance filled with the sounds of live Mariachi music and the beats of a great Dj. The decor is a beautiful blend of traditional Mexican art and modern elegance, creating a festive yet sophisticated setting.\n\nThe food is nothing short of spectacular. Each dish is a celebration of Mexican flavors, with highlights including the Lamb Chops Zarandeados and the Enchiladas de Camaron2. The service is top-notch, with friendly and attentive staff ensuring that every guest feels special.\n\nWhether you’re there for a special occasion or just a night out, Mama Por Dios promises a memorable experience with its great atmosphere and mouth-watering cuisine.\n\nI hope this captures the essence of your experience! Would you like to add or change anything?",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Mama Por Dios offers an unforgettable dining experience with its vibrant atmosphere and delectable food. From the moment you step in, you’re greeted by a lively ambiance filled with the sounds of live Mariachi music and the beats of a great Dj. The decor is a beautiful blend of traditional Mexican art and modern elegance, creating a festive yet sophisticated setting.\n\nThe food is nothing short of spectacular. Each dish is a celebration of Mexican flavors, with highlights including the Lamb Chops Zarandeados and the Enchiladas de Camaron2. The service is top-notch, with friendly and attentive staff ensuring that every guest feels special.\n\nWhether you’re there for a special occasion or just a night out, Mama Por Dios promises a memorable experience with its great atmosphere and mouth-watering cuisine.\n\nI hope this captures the essence of your experience! Would you like to add or change anything?",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Vince Trilogy",
            "uri": "https://www.google.com/maps/contrib/116967312430164552601/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXB_XWJa5Ise4tqF8ofwLNQRkmrlDEaU8C4_pvvuGnDsk1YupdwNw=s128-c0x00000000-cc-rp-mo-ba3"
          },
          "publishTime": "2024-09-22T05:53:20.493842Z"
        },
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/reviews/ChZDSUhNMG9nS0VJQ0FnSUM3LWV6eWZnEAE",
          "relativePublishTimeDescription": "2 months ago",
          "rating": 1,
          "text": {
            "text": "If you want a epileptic seizure while you eat food that tastes like 2 day old chinese take out this is your place!! While my waiter was excellent the Tempura Shrimp is soggy and drenched in High Fructose Syrup sauce.\n\nMusic and Lights\n\nNot sure if they are Rave or Burning Man Festival inspired but be prepared to listen to a horrible house mix from 2005 while you struggle to see the menu or speak to the waiter over the loud tasteless and repetitive music.\n\nThough the atmosphere was nice it was a merge of Gaudy Classic Spanish with a overload of tacky mid 2000 night club.\n\nIf you like the things above this is your place",
            "languageCode": "en"
          },
          "originalText": {
            "text": "If you want a epileptic seizure while you eat food that tastes like 2 day old chinese take out this is your place!! While my waiter was excellent the Tempura Shrimp is soggy and drenched in High Fructose Syrup sauce.\n\nMusic and Lights\n\nNot sure if they are Rave or Burning Man Festival inspired but be prepared to listen to a horrible house mix from 2005 while you struggle to see the menu or speak to the waiter over the loud tasteless and repetitive music.\n\nThough the atmosphere was nice it was a merge of Gaudy Classic Spanish with a overload of tacky mid 2000 night club.\n\nIf you like the things above this is your place",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Luciane Brown",
            "uri": "https://www.google.com/maps/contrib/116935446040547011203/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWoWoTmS_misgY2HafmU55pApgtBdbJdd9etHE48kA29jtGgCED=s128-c0x00000000-cc-rp-mo-ba2"
          },
          "publishTime": "2024-08-17T18:49:38.462612Z"
        },
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/reviews/ChZDSUhNMG9nS0VJQ0FnSURMdEtfNE5BEAE",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 5,
          "text": {
            "text": "Showed up here since it was down the street from the hotel. Did not know what to expect. The food and service was fantastic. Be prepared for a club atmosphere while dining. If loud music and club lights are not your vibe then I would not recommend it. Decor was also amazing",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Showed up here since it was down the street from the hotel. Did not know what to expect. The food and service was fantastic. Be prepared for a club atmosphere while dining. If loud music and club lights are not your vibe then I would not recommend it. Decor was also amazing",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Turner Binkley",
            "uri": "https://www.google.com/maps/contrib/100669599873995920128/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLaFrqA-knlfUIhFc77wGJnq8ioP_hlQozga6mlHnygOc0HSg=s128-c0x00000000-cc-rp-mo-ba6"
          },
          "publishTime": "2024-06-25T20:41:46.222683Z"
        },
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/reviews/ChdDSUhNMG9nS0VJQ0FnSUR6dDhpdHFnRRAB",
          "relativePublishTimeDescription": "4 months ago",
          "rating": 5,
          "text": {
            "text": "This was my 1st time coming here. It was request by my High School Grad that she wanted to come here. We def loved the decor of the place. It was a vibe. We had Birria Tacos, Green Enchiladas and Ribeye for dinner. The lobster mac was a hit. And we also tried the Costa Azul Shrimp ‐ Yum. The whole presentation of the food and drinks were awesome. We had mezcal mango flavored drinks. We got to see how the swrvers interact when its someones special occassion like a birthday. We will come back for sure.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "This was my 1st time coming here. It was request by my High School Grad that she wanted to come here. We def loved the decor of the place. It was a vibe. We had Birria Tacos, Green Enchiladas and Ribeye for dinner. The lobster mac was a hit. And we also tried the Costa Azul Shrimp ‐ Yum. The whole presentation of the food and drinks were awesome. We had mezcal mango flavored drinks. We got to see how the swrvers interact when its someones special occassion like a birthday. We will come back for sure.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Jazmyne M.",
            "uri": "https://www.google.com/maps/contrib/107502713384617229644/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXDnP6aIkvjWPq1kGItKD_gfBecRwPSyi61Uwuyh0a72kw_xSl6=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-06-13T06:25:09.765992Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/photos/AdCG2DP5t2kAciNzk877DNyECJ4ZuNJkUWVnDURDvsF5qhNa43Q6Dk3UGO5GVVZUTTs5sjDL70dnpLjgsdv900Ya2B3dYpA_7affnohGB3pHBKLRLZ-9102BCSKy-r6XMn6dnC526hlOfFyEj7pGoWhmfCyBnW0Hw1JCsh2K",
          "widthPx": 3072,
          "heightPx": 4080,
          "authorAttributions": [
            {
              "displayName": "Elijah Novoa",
              "uri": "https://maps.google.com/maps/contrib/108130799961587083557",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVJS5e5LJInR-rxnVP4m4tMQkO86fXKpL2Fp9Ayaw1WwRysPEo=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/photos/AdCG2DN5m0rMwoYYuZp7-MowdHUYWf5Yb9O3zJvq4tQj1uHUdkedPPnPwpo7eXsfZ9fyfLbhBPMQGclk2iYXYIv7yC_t3G2dySeobWh_MQouBCBkCQ7NL9b0nOosuNcdO8YVME8_H_o6ym7fQmVLbFIDO7MQVIDgXQLkA3SA",
          "widthPx": 1600,
          "heightPx": 1040,
          "authorAttributions": [
            {
              "displayName": "Mama Por Dios - DTLA",
              "uri": "https://maps.google.com/maps/contrib/102919582654297084299",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVk5NhWveTPO9gi6L-uGmFkoh3PcOuQT3nt9GToOaQUe-98BNFQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/photos/AdCG2DPFD8AWHVNuSp1Gafqx0JioRq4o00G0BZjKr2hLMB7opxjp8sdg0XPmRrDEFgibzS2PjNEpzxpeSVa015PqPFcVSdssZWsh4hwiPWFsmftnm-BVfgf_1CzEQVemRr1mv1XQ3DBvCIshmIdsVUtlsnT1QrnPts9x-7Uy",
          "widthPx": 4000,
          "heightPx": 2252,
          "authorAttributions": [
            {
              "displayName": "Vince Trilogy",
              "uri": "https://maps.google.com/maps/contrib/116967312430164552601",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXB_XWJa5Ise4tqF8ofwLNQRkmrlDEaU8C4_pvvuGnDsk1YupdwNw=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/photos/AdCG2DPyNObUhRV3lGAe05bERFPckS38NLFsOh4jvjTVgJ7SpiVBZB3BxFmo_vbBvad2CoAvXONzWLn4w3XABGN7nUApzyTOVE6B9EgB9788-k4gJa3i3A7EHJuuj8sR5co45qSpph8m_6ffYJOunNg5ZEFS-2-rRtnIoolm",
          "widthPx": 3840,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Mama Por Dios - DTLA",
              "uri": "https://maps.google.com/maps/contrib/102919582654297084299",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVk5NhWveTPO9gi6L-uGmFkoh3PcOuQT3nt9GToOaQUe-98BNFQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/photos/AdCG2DPRhDVN9QbviIzCjI5faDjNJJPpjbspIkk-Bkl4JbZF9D5IOjIrcJ41eSyI5w7agi3dzejes1gIA2HDkfiluAW4mhBDFHXxnJGZouAi4XBb5qCjz3pZzxb6rpxYzQHsaYSj0oUaVk5VUv2gtzRqSCzY49HCg4WJIjyz",
          "widthPx": 3600,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "G Quiñones",
              "uri": "https://maps.google.com/maps/contrib/113907372669690435254",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocIGuyCVIcMfgGbT6YzcyHnGMWkHAeoq18bfPcBxfMKwAnBzww=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/photos/AdCG2DNQkKDU9a3T3LD3dGw2mka-RzQ1yPQwgbZemuYV6aYiXti9nvg8ZWlVdehYsMzkXtc85eBIum6GQwh-Xi_29FIzSXKVNXdfYKPbhgjdX4HjQzcUjcVuRQ6kVujklNkayNIRUCGc4dTCpnUtQVfrPSbZjfcMU6uStZKc",
          "widthPx": 3840,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Mama Por Dios - DTLA",
              "uri": "https://maps.google.com/maps/contrib/102919582654297084299",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVk5NhWveTPO9gi6L-uGmFkoh3PcOuQT3nt9GToOaQUe-98BNFQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/photos/AdCG2DPEhT8IBxmF6crwpgioYAG1uFqKRh2QAOiNsWzqE2oa6Qq8ssliYiIweiNKUQyRRM2v2lQ2mM-zTCPdMwkagr1kSwDmBoMTyYuG3icDiO_5XgVYnMvuE6nfRUxBR0nnR1jY_9_4jaM85Q1UOE6DqS8aJvXigXlr0Aou",
          "widthPx": 3839,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Mama Por Dios - DTLA",
              "uri": "https://maps.google.com/maps/contrib/102919582654297084299",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVk5NhWveTPO9gi6L-uGmFkoh3PcOuQT3nt9GToOaQUe-98BNFQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/photos/AdCG2DODFqNAE1bFJW6IAHFdr0vlDGJBAuL1ZPETbMkBXGxIpUixVo1znOJm_MKNq5hssow8GLxVnevmOW1KzAY32icCGOYyVm9VpHC65FSRUemVxnP8yv6i-cXLWYom0HP97sAmIx8i5OlP3SyPu32Z4yShIFtlOxpNuYE4",
          "widthPx": 3839,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Mama Por Dios - DTLA",
              "uri": "https://maps.google.com/maps/contrib/102919582654297084299",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVk5NhWveTPO9gi6L-uGmFkoh3PcOuQT3nt9GToOaQUe-98BNFQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/photos/AdCG2DNma0LaCWHWg0tqXWaLEB_oi3T0cZmbDfdtP6O-amAIcdoLej96jVVZpzdHPLWhKJ7CuxnoKIxOSGgX7EKrMvQzk3VYo6x28noqByCVQ-moEN6cG6SSjsdcRXJPq_TxcRlPYjoWFyFuTk2BUWrlmoGVrd4z9zSVsc_l",
          "widthPx": 3600,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "G Quiñones",
              "uri": "https://maps.google.com/maps/contrib/113907372669690435254",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocIGuyCVIcMfgGbT6YzcyHnGMWkHAeoq18bfPcBxfMKwAnBzww=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJwwLzhN_HwoARrpfr7VNhGuY/photos/AdCG2DMf8kXpgtAcvlI7Tc6xNPLNYFJtqHnIxrgWz93X0bsruHn46aYikXEijv5n5Id_11FYV_-T7cGTcrZg-ovD_EyoVPp2u0xlh9V1jJfpjthmkHQIGtDUrQZRLGjJgn2HpQ4r2hmfhQIYlSjPFaRKkA1fEeDyhHWmoYYt",
          "widthPx": 3840,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Mama Por Dios - DTLA",
              "uri": "https://maps.google.com/maps/contrib/102919582654297084299",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVk5NhWveTPO9gi6L-uGmFkoh3PcOuQT3nt9GToOaQUe-98BNFQ=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "servesCocktails": True,
      "servesDessert": True,
      "servesCoffee": True,
      "restroom": True,
      "goodForGroups": True,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsCashOnly": False
      },
      "parkingOptions": {
        "valetParking": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleRestroom": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Sizzling fajitas, ceviches and other Mexican staples are served in a warm and inviting setting.",
          "languageCode": "en-US"
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJ_62lvrPHwoAR7Bt3kqK9jNk",
            "placeId": "ChIJ_62lvrPHwoAR7Bt3kqK9jNk",
            "displayName": {
              "text": "The California Club",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 102.963135,
            "travelDistanceMeters": 86.69834
          },
          {
            "name": "places/ChIJO1QZtrPHwoARgt2CrT72juU",
            "placeId": "ChIJO1QZtrPHwoARgt2CrT72juU",
            "displayName": {
              "text": "City National Plaza",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 85.32459,
            "travelDistanceMeters": 93.35381
          },
          {
            "name": "places/ChIJJ8s_8LPHwoAR18VJqMWY6Tc",
            "placeId": "ChIJJ8s_8LPHwoAR18VJqMWY6Tc",
            "displayName": {
              "text": "Pegasus Apartments",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 69.24144,
            "travelDistanceMeters": 76.96094
          },
          {
            "name": "places/ChIJ71dGk7PHwoARHWr_QGbZIGU",
            "placeId": "ChIJ71dGk7PHwoARHWr_QGbZIGU",
            "displayName": {
              "text": "Standard",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "lodging",
              "point_of_interest"
            ],
            "spatialRelationship": "ACROSS_THE_ROAD",
            "straightLineDistanceMeters": 43.808666,
            "travelDistanceMeters": 44.41737
          },
          {
            "name": "places/ChIJC3_R2rPHwoARAk6Rf6JEeZM",
            "placeId": "ChIJC3_R2rPHwoARAk6Rf6JEeZM",
            "displayName": {
              "text": "City Club LA",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "ACROSS_THE_ROAD",
            "straightLineDistanceMeters": 58.411903,
            "travelDistanceMeters": 5.252592
          }
        ],
        "areas": [
          {
            "name": "places/ChIJFxgUlrPHwoARoUK2qWd6P9g",
            "placeId": "ChIJFxgUlrPHwoARoUK2qWd6P9g",
            "displayName": {
              "text": "Financial District",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY",
      "id": "ChIJAw8ZT7THwoARJXGw3rjYMWY",
      "types": [
        "mexican_restaurant",
        "fast_food_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 283-2058",
      "internationalPhoneNumber": "+1 213-283-2058",
      "formattedAddress": "601 W 7th St, Los Angeles, CA 90017, USA",
      "addressComponents": [
        {
          "longText": "601",
          "shortText": "601",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "West 7th Street",
          "shortText": "W 7th St",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90017",
          "shortText": "90017",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632PXV+28",
        "compoundCode": "2PXV+28 Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.0475961,
        "longitude": -118.25664719999999
      },
      "viewport": {
        "low": {
          "latitude": 34.0461726197085,
          "longitude": -118.25798538029149
        },
        "high": {
          "latitude": 34.0488705802915,
          "longitude": -118.25528741970851
        }
      },
      "rating": 4.1,
      "googleMapsUri": "https://maps.google.com/?cid=7363905154249158949",
      "websiteUri": "https://locations.chipotle.com/ca/los-angeles/601-w-7th-st?utm_source=google&utm_medium=yext&utm_campaign=yext_listings",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 10,
              "minute": 30
            },
            "close": {
              "day": 0,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 10,
              "minute": 30
            },
            "close": {
              "day": 1,
              "hour": 23,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 10,
              "minute": 30
            },
            "close": {
              "day": 2,
              "hour": 23,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 10,
              "minute": 30
            },
            "close": {
              "day": 3,
              "hour": 23,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 10,
              "minute": 30
            },
            "close": {
              "day": 4,
              "hour": 23,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 10,
              "minute": 30
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 10,
              "minute": 30
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 10:30 AM – 11:00 PM",
          "Tuesday: 10:30 AM – 11:00 PM",
          "Wednesday: 10:30 AM – 11:00 PM",
          "Thursday: 10:30 AM – 11:00 PM",
          "Friday: 10:30 AM – 10:00 PM",
          "Saturday: 10:30 AM – 10:00 PM",
          "Sunday: 10:30 AM – 10:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e601 W 7th St\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90017\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_INEXPENSIVE",
      "userRatingCount": 1349,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Chipotle Mexican Grill",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "reservable": False,
      "servesBreakfast": False,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": True,
      "servesWine": False,
      "servesBrunch": False,
      "servesVegetarianFood": True,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 10,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 10,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 23,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 10,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 23,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 10,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 23,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 10,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 23,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 10,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 10,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 10:30 AM – 11:00 PM",
          "Tuesday: 10:30 AM – 11:00 PM",
          "Wednesday: 10:30 AM – 11:00 PM",
          "Thursday: 10:30 AM – 11:00 PM",
          "Friday: 10:30 AM – 10:00 PM",
          "Saturday: 10:30 AM – 10:00 PM",
          "Sunday: 10:30 AM – 10:00 PM"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "601 W 7th St, Los Angeles",
      "editorialSummary": {
        "text": "Fast-food chain offering Mexican fare, including design-your-own burritos, tacos & bowls.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/reviews/ChZDSUhNMG9nS0VJQ0FnSUQ3LTRETlZnEAE",
          "relativePublishTimeDescription": "a month ago",
          "rating": 5,
          "text": {
            "text": "I had a fantastic experience at Chipotle thanks to Andrew! From the moment I approached the counter, he greeted me with a warm smile and was incredibly patient while I decided what to order. He offered helpful suggestions without being pushy, which made the whole process enjoyable. When it came time to build my bowl, Andrew made sure I received generous portions of everything I wanted, showing that he takes pride in his work. Overall, his excellent service and attention to detail made my visit memorable. Thank you, Andrew, for going above and beyond—I’ll definitely be back!",
            "languageCode": "en"
          },
          "originalText": {
            "text": "I had a fantastic experience at Chipotle thanks to Andrew! From the moment I approached the counter, he greeted me with a warm smile and was incredibly patient while I decided what to order. He offered helpful suggestions without being pushy, which made the whole process enjoyable. When it came time to build my bowl, Andrew made sure I received generous portions of everything I wanted, showing that he takes pride in his work. Overall, his excellent service and attention to detail made my visit memorable. Thank you, Andrew, for going above and beyond—I’ll definitely be back!",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Mohit Khetarpal",
            "uri": "https://www.google.com/maps/contrib/100257486460069293659/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocJk1v_Ks9Dg-zIJpDJrvZRc2J0IcISdYqnOVt9ll49QVj17Yw=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-08-29T01:36:52.244241Z"
        },
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/reviews/ChZDSUhNMG9nS0VJQ0FnSUNkeEwyS0t3EAE",
          "relativePublishTimeDescription": "8 months ago",
          "rating": 3,
          "text": {
            "text": "Chipotle has been consistently good at every chain spot that they have.\n\nI ordered a salad bowl greens, grilled vegetables, no rice, no beans, half chicken, half beef, light sour cream, light cheese, and finished off guacamole. It was delicious and a good dinner to keep me filled.\n\nI’d definitely come back to this spot again when I need a quick bite. Parking is limited to street or paid parking at a lot nearby.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Chipotle has been consistently good at every chain spot that they have.\n\nI ordered a salad bowl greens, grilled vegetables, no rice, no beans, half chicken, half beef, light sour cream, light cheese, and finished off guacamole. It was delicious and a good dinner to keep me filled.\n\nI’d definitely come back to this spot again when I need a quick bite. Parking is limited to street or paid parking at a lot nearby.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Rodrigo “funning”",
            "uri": "https://www.google.com/maps/contrib/117621384126831676862/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU66q7s69xnIgG16vNq6uvDZaMF9tEXwzGs7WPIbqyH1YCNbsEXUA=s128-c0x00000000-cc-rp-mo-ba7"
          },
          "publishTime": "2024-02-12T02:52:27.051961Z"
        },
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/reviews/ChZDSUhNMG9nS0VJQ0FnSUN6bHNPdUVBEAE",
          "relativePublishTimeDescription": "4 months ago",
          "rating": 1,
          "text": {
            "text": "Incredibly disappointed that the employee who prepared my order definitely noticed they burnt my food and still decided to pack it and hand it to me. Since it was an app pick up by the time I opened my food to notice it was burnt, it was not feasible to go back and complain/request it to be remade.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Incredibly disappointed that the employee who prepared my order definitely noticed they burnt my food and still decided to pack it and hand it to me. Since it was an app pick up by the time I opened my food to notice it was burnt, it was not feasible to go back and complain/request it to be remade.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Carlos Zaragoza",
            "uri": "https://www.google.com/maps/contrib/117855870014960836447/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocKvPwFl0lNmwUTXTxocu-Z6nU1nl89ngR2_3K5Wz7arH4vZgA=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-06-01T21:19:59.987797Z"
        },
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/reviews/ChdDSUhNMG9nS0VJQ0FnSURGdGY3OF9BRRAB",
          "relativePublishTimeDescription": "11 months ago",
          "rating": 4,
          "text": {
            "text": "We travelled to US from India and we found this good option for indians too.. We has with rice chicken and beans.. If you are vegetarian you can try this ans ask them not to mix meat.. This was my favorite.. But they need to maintain time to time cleaning of tables and floor.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "We travelled to US from India and we found this good option for indians too.. We has with rice chicken and beans.. If you are vegetarian you can try this ans ask them not to mix meat.. This was my favorite.. But they need to maintain time to time cleaning of tables and floor.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "harsh raj",
            "uri": "https://www.google.com/maps/contrib/117211895109265412744/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocJakRjfWGo0RQgtyMNuSdB7fRa7MZOCJY1z-c9ZKvE78uNuZg=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2023-11-09T00:47:43.444716Z"
        },
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/reviews/ChZDSUhNMG9nS0VJQ0FnSUNGNjZmYUtREAE",
          "relativePublishTimeDescription": "11 months ago",
          "rating": 5,
          "text": {
            "text": "One of the best Mexican grill ever in downtown LA. The food was premium quality, the staff were friendly and supportive. The place is clean tidy and organized. They deserve all the best.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "One of the best Mexican grill ever in downtown LA. The food was premium quality, the staff were friendly and supportive. The place is clean tidy and organized. They deserve all the best.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Garo Torossian",
            "uri": "https://www.google.com/maps/contrib/100036022187885801721/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXdHXMmBrnvx4I7-uyd8cEkJ2Xd1XIKGhJCSO0KACMn_E8VKvo=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2023-11-02T18:31:04.942164Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/photos/AdCG2DM1IAPcHNXjkthaMjmA4pe3wkiVhkLHaOFRB_f6j2f86M81f1twzsZmh-ePCFxcpMvXdtBurm8F8gcRioI2M74yuvEB-QLPLVlY14VFK5mJVGWGW_GlhmpPuHmFRfkPcx7i3opSD6Y1DwiYOX6lsa3sSbnMUviKDI-n",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "플라잉캠퍼",
              "uri": "https://maps.google.com/maps/contrib/102438308804243999390",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVMA4C3r_DqE5tx_9eB5J3Ce21UN9tpcN1CXQVYHRagFTE6HI84=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/photos/AdCG2DPIyPxF4b7UETZAIIQzijEtpiYqFb1FNIJzTCVwi2LKh2ov2lFQHERUUvWX1tdQjtoESeB2X7Yc4DOTIStblsLEKEb_mSxuz0R79n5s6mPU30CAsieSLGcSMHA6bXBHuJHWZsZz774CKZhoIJqvWIq39w3DuT1wL6Nc",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Rodrigo “funning”",
              "uri": "https://maps.google.com/maps/contrib/117621384126831676862",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU66q7s69xnIgG16vNq6uvDZaMF9tEXwzGs7WPIbqyH1YCNbsEXUA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/photos/AdCG2DPz8nSWBmQx7oGhiIgOBM0pQQoFstha9_f8MCRr99TqCKtHCmX_E1oemFh4Oe5229QVoEiZ85RERlytbQoaa_gqOxskJLrN79QwdoDwUcVsMQKTbvMaDs7T7754znsLMPQTUcr_AVQLAIAaBiu9IXTzqjQgLQaxCs0G",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "andrew O",
              "uri": "https://maps.google.com/maps/contrib/102325908322126841266",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUSqpVWq8wcMsP6SJ4Cf5r31O3LhBRV_9v_CNezYh1wD8ycs9HcLg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/photos/AdCG2DMo4AAO1wEYUowUNWeIqAitbbOTf1RkIz0cHl76--Q3Y4Z9--4cSL5Bx-kWL7JlaZOX4RKXrX6tNyOYlNU15tzAurGPXlz77G_94oyt-WYQLYAqRxYeDqArVq3U-m3gWEjEkdskwjtYEqO5LBbCLgkwnQ7-82-5jOJ_",
          "widthPx": 4800,
          "heightPx": 3600,
          "authorAttributions": [
            {
              "displayName": "jerry Z",
              "uri": "https://maps.google.com/maps/contrib/101055588710013728856",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjViN7m5b5QVQE2DOYHKof8LhWc4GR3QaFvvEIIAaWVNjw_UfG0Kfw=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/photos/AdCG2DMPQ9SDy7gyYJWerEvKuYyU0dazkM0WPGdbg58dgtFj9ECRXm5OswzAW3Kf_1bc2xB6-tpYkcd9iNpeXa7l7pKqmaSJv3TdDY8NVcw-jIN9dwk-bFoUgN-yCJWUmtsAploLfmRunyVgZ7ej3yTMdTLYAXsugxjT_6rL",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "플라잉캠퍼",
              "uri": "https://maps.google.com/maps/contrib/102438308804243999390",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVMA4C3r_DqE5tx_9eB5J3Ce21UN9tpcN1CXQVYHRagFTE6HI84=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/photos/AdCG2DOW4LxF2YHNGV0JltLVIB2ZMLZ_lem9ElZmecX_6BfJr0L3OgBrKB4l-8I9LEr8kFxeeVwD9P_IV7jw0nRK3gEBtAwHMzOjWCJ2DuX0lZ6mPRsxTLZiySH1ddAAF_piMUAfy2Lv6nBuTZ_jbRgHpwvN83OMig0sDnh3",
          "widthPx": 3600,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Rodrigo “funning”",
              "uri": "https://maps.google.com/maps/contrib/117621384126831676862",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU66q7s69xnIgG16vNq6uvDZaMF9tEXwzGs7WPIbqyH1YCNbsEXUA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/photos/AdCG2DNK1MZHjVcK43GW6z7nhqm89Gg-5asFL5t6Zgh8UzNt9EKSpFHNw6UoUa-z0NyTSIeZBHcaHpcf0GfIqyEOq6jNTTujEo_cWIGqk9A13rqCyNDHwkxHEE23xFJgubfF273rAcbDgaOJENCbxfujYrHXTeqobWhXfvIm",
          "widthPx": 4000,
          "heightPx": 2252,
          "authorAttributions": [
            {
              "displayName": "Nathan Maloney",
              "uri": "https://maps.google.com/maps/contrib/112417521331158770964",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocJ94ga8NVLtW9KboDvO-4cnQY7LfthUTddO7dsmi1o-DYmJw-U=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/photos/AdCG2DONeqOLxg7bdkLUW8rOo8PsRfu1pPXfFA5D09h6g3tdrpbY28KMKublfF9zAI5jC9iQkKgEuH-ePoRUGahMWmePWF4ai1K_WtQYlK0MIM-1HUMK6_YEE855tcQiz6RPzkWG1M2aGsj6wAG8Le7sVY_tTXyz01PKPnTo",
          "widthPx": 1225,
          "heightPx": 786,
          "authorAttributions": [
            {
              "displayName": "Benjamin Shifrin",
              "uri": "https://maps.google.com/maps/contrib/100499879798367208309",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVQVdlA2ZmsjTAWCMeiDMfjSiq1Y6-icQhdcvq02Cz5WTmvYL5T=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/photos/AdCG2DOzRoSyxk7-UmMi_VmFdOlgnLAoZTi9PyRB2TPiC4feKDdaOlRHR99tiSI8RIR1_67azKF1jEupFZzZvq96BmAVPhD7aKaNo3Ta0ywxy4IbEVHNSnZzbXJYMYgMlTVtHsu4qCx34WiG1_E-hM3Q5vROKqH0lYWTCFbZ",
          "widthPx": 1920,
          "heightPx": 1080,
          "authorAttributions": [
            {
              "displayName": "harsh raj",
              "uri": "https://maps.google.com/maps/contrib/117211895109265412744",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocJakRjfWGo0RQgtyMNuSdB7fRa7MZOCJY1z-c9ZKvE78uNuZg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJAw8ZT7THwoARJXGw3rjYMWY/photos/AdCG2DMC9tEa4V1-j8MQP-VhOYJt5pocuYX9uRewCxE7knw4nZpup9SnNJKk1f85Hcjln3KyMY76A57WRKi64V2Gcpt3Oy0XpulHeqg-LiA7xhvM60VDSbmia4jdIYzlhK4sVeHihRMqw1m1gg_UayKLxeMz4ru27PQNE7aV",
          "widthPx": 4032,
          "heightPx": 2268,
          "authorAttributions": [
            {
              "displayName": "Ku K",
              "uri": "https://maps.google.com/maps/contrib/109141939036413659133",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocIspeCTOhoub-vfuS3C4WIIWuPpNwgsUoe0T6ynDnUIL-0tKw=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": False,
      "liveMusic": False,
      "menuForChildren": True,
      "servesCocktails": False,
      "servesDessert": False,
      "servesCoffee": False,
      "goodForChildren": True,
      "allowsDogs": False,
      "restroom": True,
      "goodForGroups": True,
      "goodForWatchingSports": False,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleRestroom": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Fast-food chain restaurant in Downtown Los Angeles' Financial District serving Mexican comfort food for lunch and dinner.",
          "languageCode": "en-US"
        },
        "description": {
          "text": "Fast-food chain restaurant in Downtown Los Angeles' Financial District serving Mexican comfort food for lunch and dinner.\nThe menu includes burritos, burrito bowls, and salads. There are vegetarian, vegan, and gluten-free options. Beer is available.\nThe space is casual and popular for solo lunchtime dining. It can accommodate children, and there's a kids' menu.\nCustomers can order ahead, but there's usually a wait. Service is fast.\nCustomers typically spend $10–20.",
          "languageCode": "en-US"
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJ_yXhTrTHwoARU36hVDFInhg",
            "placeId": "ChIJ_yXhTrTHwoARU36hVDFInhg",
            "displayName": {
              "text": "Bottega Louie",
              "languageCode": "en"
            },
            "types": [
              "bakery",
              "cafe",
              "establishment",
              "food",
              "point_of_interest",
              "restaurant",
              "store"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 61.20133,
            "travelDistanceMeters": 41.341087
          },
          {
            "name": "places/ChIJi2n_QrTHwoARkgY9DE5o8q0",
            "placeId": "ChIJi2n_QrTHwoARkgY9DE5o8q0",
            "displayName": {
              "text": "Karl Strauss Brewing Company",
              "languageCode": "en"
            },
            "types": [
              "bar",
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 49.939476,
            "travelDistanceMeters": 85.73096
          },
          {
            "name": "places/ChIJ4xmOHbTHwoARd2FMCc2gmek",
            "placeId": "ChIJ4xmOHbTHwoARd2FMCc2gmek",
            "displayName": {
              "text": "Macy's",
              "languageCode": "en"
            },
            "types": [
              "clothing_store",
              "department_store",
              "establishment",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 182.6797,
            "travelDistanceMeters": 212.33978
          },
          {
            "name": "places/ChIJ651wFbTHwoARKmX3zYSD_tY",
            "placeId": "ChIJ651wFbTHwoARKmX3zYSD_tY",
            "displayName": {
              "text": "Walgreens Pharmacy",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "health",
              "pharmacy",
              "point_of_interest",
              "store"
            ],
            "straightLineDistanceMeters": 57.075783,
            "travelDistanceMeters": 164.35298
          },
          {
            "name": "places/ChIJWwgVP7THwoARlStUVdfwh8A",
            "placeId": "ChIJWwgVP7THwoARlStUVdfwh8A",
            "displayName": {
              "text": "Walgreens",
              "languageCode": "en"
            },
            "types": [
              "clothing_store",
              "convenience_store",
              "drugstore",
              "establishment",
              "food",
              "health",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 84.298935,
            "travelDistanceMeters": 136.1791
          }
        ],
        "areas": [
          {
            "name": "places/ChIJFxgUlrPHwoARoUK2qWd6P9g",
            "placeId": "ChIJFxgUlrPHwoARoUK2qWd6P9g",
            "displayName": {
              "text": "Financial District",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto",
      "id": "ChIJRfplRKvHwoARS6jKeJrLLto",
      "types": [
        "mexican_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 944-5795",
      "internationalPhoneNumber": "+1 213-944-5795",
      "formattedAddress": "888 Wilshire Blvd, Los Angeles, CA 90017, USA",
      "addressComponents": [
        {
          "longText": "888",
          "shortText": "888",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "Wilshire Boulevard",
          "shortText": "Wilshire Blvd",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90017",
          "shortText": "90017",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "2668",
          "shortText": "2668",
          "types": [
            "postal_code_suffix"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632PXR+W8",
        "compoundCode": "2PXR+W8 Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.0497927,
        "longitude": -118.2591948
      },
      "viewport": {
        "low": {
          "latitude": 34.0485306697085,
          "longitude": -118.26051248029148
        },
        "high": {
          "latitude": 34.0512286302915,
          "longitude": -118.25781451970849
        }
      },
      "rating": 3.8,
      "googleMapsUri": "https://maps.google.com/?cid=15721727213508929611",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 11,
              "minute": 30
            },
            "close": {
              "day": 1,
              "hour": 2,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 11,
              "minute": 30
            },
            "close": {
              "day": 2,
              "hour": 2,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 11,
              "minute": 30
            },
            "close": {
              "day": 3,
              "hour": 2,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 11,
              "minute": 30
            },
            "close": {
              "day": 4,
              "hour": 2,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 11,
              "minute": 30
            },
            "close": {
              "day": 5,
              "hour": 2,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 11,
              "minute": 30
            },
            "close": {
              "day": 6,
              "hour": 2,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 11,
              "minute": 30
            },
            "close": {
              "day": 0,
              "hour": 2,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 11:30 AM – 2:00 AM",
          "Tuesday: 11:30 AM – 2:00 AM",
          "Wednesday: 11:30 AM – 2:00 AM",
          "Thursday: 11:30 AM – 2:00 AM",
          "Friday: 11:30 AM – 2:00 AM",
          "Saturday: 11:30 AM – 2:00 AM",
          "Sunday: 11:30 AM – 2:00 AM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e888 Wilshire Blvd\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90017-2668\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_MODERATE",
      "userRatingCount": 408,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "El Patron Cantina",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": False,
      "dineIn": True,
      "reservable": True,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": True,
      "servesWine": True,
      "servesVegetarianFood": True,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 11,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 1,
              "hour": 2,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 11,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 2,
              "hour": 2,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 11,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 3,
              "hour": 2,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 11,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 23,
              "minute": 59,
              "truncated": True,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 0,
              "minute": 0,
              "truncated": True,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 2,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 11,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 5,
              "hour": 2,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 11,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 6,
              "hour": 2,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 11,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 0,
              "hour": 2,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 11:30 AM – 2:00 AM",
          "Tuesday: 11:30 AM – 2:00 AM",
          "Wednesday: 11:30 AM – 2:00 AM",
          "Thursday: 11:30 AM – 2:00 AM",
          "Friday: 11:30 AM – 2:00 AM",
          "Saturday: 11:30 AM – 2:00 AM",
          "Sunday: 11:30 AM – 2:00 AM"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "888 Wilshire Blvd, Los Angeles",
      "reviews": [
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/reviews/ChdDSUhNMG9nS0VJQ0FnSURMNl9YZ2pBRRAB",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 4,
          "text": {
            "text": "This place is right next door to Intercontinental. So we dropped by for dinner. We were very sceptical having read the reviews. But this place was a pleasant surprise in many ways. The ambience is great and has a lively party atmosphere. The food and cocktails are nice. The margarita flight is a great experience and well made. The nachos, tacos were also tasty, fresh and good portions. The churros were the best way to end the dinner. Great place for some fab cocktails and dinner.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "This place is right next door to Intercontinental. So we dropped by for dinner. We were very sceptical having read the reviews. But this place was a pleasant surprise in many ways. The ambience is great and has a lively party atmosphere. The food and cocktails are nice. The margarita flight is a great experience and well made. The nachos, tacos were also tasty, fresh and good portions. The churros were the best way to end the dinner. Great place for some fab cocktails and dinner.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Ashok Hatwar",
            "uri": "https://www.google.com/maps/contrib/111236990385940564322/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLf7azbPout_bUX8a48pBh9CztLQRzAO_Al8o91BmRb08-cFA=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-07-01T05:03:28.942206Z"
        },
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/reviews/ChdDSUhNMG9nS0VJQ0FnSURIeEtLRDV3RRAB",
          "relativePublishTimeDescription": "a month ago",
          "rating": 3,
          "text": {
            "text": "UPDATE: Had to come back and take away some stars because we went to the restaurant today and the waiter made a mistake with our order. It wouldn’t have been a problem if he didn’t try to argue with us that he didn’t get our order wrong. He didn’t write anything down when he took our order to begin with (which isn’t a deal breaker, we’ve gone to plenty of restaurants where they don’t write things dwn and memorize it) BUT…… when we say hey this is wrong, this is not what we asked for. Instead of apologizing to us…..he begins to argue and he was rude. This is unfortunate because we love coming here. The food is amazing and we love the atmosphere, the ambience.  They need to do better with the service here honestly! That was uncalled for and extremely unprofessional!!! I had to diffuse the situation by just saying he misunderstood what we said and it’s ok…. He finally walked away from our table. That’s disheartening!!!! Anyway, our food was great as usual. I’ve seen reviews here speaking about the service being bad or a problem. I concur.\n\nThis place was AMAZING!!!! It was our first time and we truly enjoyed it. The food is top tier, service was great and atmosphere 1000!!!! You won’t be disappointed visiting El Patron Cantina….Come with your dancing shoes. Lol!!!! 😍😍😍 (Chicken Tortilla Soup and Chips and Guacamole).",
            "languageCode": "en"
          },
          "originalText": {
            "text": "UPDATE: Had to come back and take away some stars because we went to the restaurant today and the waiter made a mistake with our order. It wouldn’t have been a problem if he didn’t try to argue with us that he didn’t get our order wrong. He didn’t write anything down when he took our order to begin with (which isn’t a deal breaker, we’ve gone to plenty of restaurants where they don’t write things dwn and memorize it) BUT…… when we say hey this is wrong, this is not what we asked for. Instead of apologizing to us…..he begins to argue and he was rude. This is unfortunate because we love coming here. The food is amazing and we love the atmosphere, the ambience.  They need to do better with the service here honestly! That was uncalled for and extremely unprofessional!!! I had to diffuse the situation by just saying he misunderstood what we said and it’s ok…. He finally walked away from our table. That’s disheartening!!!! Anyway, our food was great as usual. I’ve seen reviews here speaking about the service being bad or a problem. I concur.\n\nThis place was AMAZING!!!! It was our first time and we truly enjoyed it. The food is top tier, service was great and atmosphere 1000!!!! You won’t be disappointed visiting El Patron Cantina….Come with your dancing shoes. Lol!!!! 😍😍😍 (Chicken Tortilla Soup and Chips and Guacamole).",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Tracey Pugh",
            "uri": "https://www.google.com/maps/contrib/118383806506922188448/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLpOjdL9XyZjt7kl34glYn8O4f5MnMHphKPKYlvSGIFEEZKCQ=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-09-16T22:55:47.633232Z"
        },
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/reviews/ChZDSUhNMG9nS0VJQ0FnSUM3b3M2TldnEAE",
          "relativePublishTimeDescription": "2 months ago",
          "rating": 5,
          "text": {
            "text": "First time visiting from AZ. Loved the Pazole, Chips & Salsa. It was sooo good! Friendly staff, reasonably priced, great atmosphere. Definitely will be back & recommend. Also they have free dancing & music on Fri & Sat nights! Love this place ❤️",
            "languageCode": "en"
          },
          "originalText": {
            "text": "First time visiting from AZ. Loved the Pazole, Chips & Salsa. It was sooo good! Friendly staff, reasonably priced, great atmosphere. Definitely will be back & recommend. Also they have free dancing & music on Fri & Sat nights! Love this place ❤️",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Laura Jane",
            "uri": "https://www.google.com/maps/contrib/115442580808574292505/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLa2y1TYvL0z0bKBnfJtgotVy_xtOVhoRtbnvrnNTV3NCAWJA=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-08-14T03:08:41.613179Z"
        },
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/reviews/ChZDSUhNMG9nS0VJQ0FnSURINU1TVmF3EAE",
          "relativePublishTimeDescription": "a month ago",
          "rating": 2,
          "text": {
            "text": "I dined here last night with my friend and it’s safe to say we won’t be back. When we arrived we were told to pick any table, all of them were dirty with cups and food from the last guests except one. We waited 20 minutes for the waitress and ended up going to the bar to ask what’s the process to order. The restaurant was pretty much empty besides a group of maybe 5 aside from the two of us. The food was good there’s a limited menu after 10 I think, which was fine for us. The margarita flight simply not good and we had to ask to have two of the drinks changed because it was just not drinkable. There were patrons in casual clothes going behind the bar and grabbing the candy from the jars on the bar that’s used for the drinks!!?!! People we saw outside smoking came in and went behind the bar and in the kitchen window… it’s unsanitary and gross. We had no idea who worked there or not. The host who is supposed to seat you even went outside to join the group smoking. Around 12:30 we were told it was last call but watched several of the outside smokers order shots and a variety of drinks. Unpleasant experience so we just payed and left most of our food/drinks unfinished.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "I dined here last night with my friend and it’s safe to say we won’t be back. When we arrived we were told to pick any table, all of them were dirty with cups and food from the last guests except one. We waited 20 minutes for the waitress and ended up going to the bar to ask what’s the process to order. The restaurant was pretty much empty besides a group of maybe 5 aside from the two of us. The food was good there’s a limited menu after 10 I think, which was fine for us. The margarita flight simply not good and we had to ask to have two of the drinks changed because it was just not drinkable. There were patrons in casual clothes going behind the bar and grabbing the candy from the jars on the bar that’s used for the drinks!!?!! People we saw outside smoking came in and went behind the bar and in the kitchen window… it’s unsanitary and gross. We had no idea who worked there or not. The host who is supposed to seat you even went outside to join the group smoking. Around 12:30 we were told it was last call but watched several of the outside smokers order shots and a variety of drinks. Unpleasant experience so we just payed and left most of our food/drinks unfinished.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Dionnica Tolliver",
            "uri": "https://www.google.com/maps/contrib/116159023219960308379/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocJgbUbX8VVc3lXTBPfHsSnR96rATeBcHY_ZXtcob1b_Hqs0=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-09-12T18:23:04.876648Z"
        },
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/reviews/ChdDSUhNMG9nS0VJQ0FnSUNyX2JhNTNBRRAB",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 5,
          "text": {
            "text": "Omg!!! The food here is amazing! I lovvvve Mexican food and this place hit the spot! The atmosphere was fun. The guac & chips were amazing. I only had one margarita & it was good as well! My only knock on the service was both times I came in it took a lil too long for a waitress to come over & it wasn’t even busy BUT both times the waitresses were kind & quick! I’d definitely recommend this spot! We need one in TX!",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Omg!!! The food here is amazing! I lovvvve Mexican food and this place hit the spot! The atmosphere was fun. The guac & chips were amazing. I only had one margarita & it was good as well! My only knock on the service was both times I came in it took a lil too long for a waitress to come over & it wasn’t even busy BUT both times the waitresses were kind & quick! I’d definitely recommend this spot! We need one in TX!",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "T T",
            "uri": "https://www.google.com/maps/contrib/117024988804761385443/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUwaVwOd0ML9OQ0kuihTmwnH9iAnhT6jf5sXyyPakScJL1Jn6jSFw=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-07-10T14:15:06.272168Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/photos/AdCG2DNb-aLwoW1mZ5L2UGXPiAGlOPdp9l8PtvfjuIqbKAnswmkOvzk3XhHoJoyUiUN5qR5RBhc4txXDsN18hMHxvUe9KNoMkCq4ReEyFNOD3zuKu35E-u4zWWe2J_5rt-XFFVAWnWWnHgPJJdXUIvbQhRn0p9DC79MCnFtU",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "ana quijada",
              "uri": "https://maps.google.com/maps/contrib/101002297323897277869",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocL43knGccqtXyUwagxxYcqVVV1sw63R0wxqRlIsg7AvVccOlg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/photos/AdCG2DMnO9CoahLVMK35mhS7FjKPGH_X-Lvpm4TNuyXwtkjjbjHmkWh_bhMq0XH5pAj-Y3_it6VNLdAPrjjh5PV1E0mFEascSFey1ugLXZjHSMnkRixmLth3FO09HWFs_BTOZCe41YtmSpu6vM8kR0r468RHRoiTMSXFv6Xj",
          "widthPx": 4000,
          "heightPx": 3000,
          "authorAttributions": [
            {
              "displayName": "Mitchell Everlyn",
              "uri": "https://maps.google.com/maps/contrib/114997294767088263092",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLzyO6tjFyLwQEFLjKFbnct_9H1TL_sGCVItqE5bHDm46nymA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/photos/AdCG2DPLMxFj6LyutEBxDUsdRoi18-bJIUBz1vhgGS3_HxF6ao5xWvlTa1ltYl0jAOS9hHkvJuZeWZNN2Z9HRCKKesA25OHQMc9TyLGe3JmDdfjIsJSHMRd7uu6Lvl3f3YNxzqgWlkkZc_EjqRgo3WZL10hMRZVtC9ODEked",
          "widthPx": 3600,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Sarah Stierch",
              "uri": "https://maps.google.com/maps/contrib/102295477941248367242",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVphXMPL0wlDgHECOBtACvjpIO9jtK9ANOATs4bmpZHrYHuYt-t=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/photos/AdCG2DOmuHXkisPov12E1zSfHzdWVL7tO0BEJZ3MnoidzLJbORFGcZHL0j7IrGPFBFuD98O_Su6LGijGuvslcysM3VZqUD5oKcaife9b2AjF9CGkooGcb6TnatXbMjo7IZl4zzSESXPDuab8QiRkpnN4Bu2ppcr1CryQ2sWz",
          "widthPx": 4000,
          "heightPx": 3000,
          "authorAttributions": [
            {
              "displayName": "Laura Jane",
              "uri": "https://maps.google.com/maps/contrib/115442580808574292505",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLa2y1TYvL0z0bKBnfJtgotVy_xtOVhoRtbnvrnNTV3NCAWJA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/photos/AdCG2DO-gJB3TByFuiGoOXpxaVbbeAOqUgF4gTw42D43xKiQLO9brmNWXFJWlQjeb-7KJywGYVsYUC7MrAMHn1Ozrn6O2EyKh_YZEGN4F0aodaW74Q92fyrlVOV2sMXazt8G4_egSi-i8Xal8o8eu5DaqZXzSdHL70asmy4B",
          "widthPx": 3072,
          "heightPx": 4080,
          "authorAttributions": [
            {
              "displayName": "Elijah Novoa",
              "uri": "https://maps.google.com/maps/contrib/108130799961587083557",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVJS5e5LJInR-rxnVP4m4tMQkO86fXKpL2Fp9Ayaw1WwRysPEo=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/photos/AdCG2DNg0kpZIUDiBMODdoOQ7M8l08eddGp3jbRAcL45lYJgO45KLUeW8iQV2JHZzswFOkMi4e7hoFwLOUQGDlC3YdIArlIFEji9cROEwoWw3xDpSTcWaxEG6j1Ptt52NkEZemgRGdU5ZceZosGYdkCkT84GnwZihC0jYwcv",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Sarah Stierch",
              "uri": "https://maps.google.com/maps/contrib/102295477941248367242",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVphXMPL0wlDgHECOBtACvjpIO9jtK9ANOATs4bmpZHrYHuYt-t=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/photos/AdCG2DM2eD2ZuT7Yf1BKkEJBtsX3NkhVoFINEhp3KFPDLXD4g4DGk1c2zmjkrLzwzgUKNz7R5jH8971Qxic6hUWlVvja2Loj_RFxfXHoqNwGg6iZ6PyHUZ2cD6vHov3q8XEg8Lrmu0Ji5-Fx2O5bZeaZVuc92b018TPQbKJC",
          "widthPx": 3600,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Christiane Highfill",
              "uri": "https://maps.google.com/maps/contrib/111336891865015635249",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVkL2Y25q_WX-YUSDngQ1N-bLeSeHEamVkM22TWe0By1iSIm40d=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/photos/AdCG2DMI6Vda-mMcka9XjOFnkiZTahdAS6wHvyopy04R4VXtB4rzcmUQI4vMqVgV0Hu5IdDkV0bGzOgTUoru743UqRx5PIzN0h9pfLaZAcJcDzZxze3MEOrHw2Wc0RVUynFHnPY-ZbgciEVnohQfYkYkNWCGHdpILNg-Q_Q2",
          "widthPx": 4000,
          "heightPx": 3000,
          "authorAttributions": [
            {
              "displayName": "Dee Kittykat",
              "uri": "https://maps.google.com/maps/contrib/103403214699983122573",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVPjHjMHL43BdtHK2gdLhqmEGUnA_srOdktuzpVbYz6t7a4LlWPYw=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/photos/AdCG2DMqC0niBjAFfpqio2LTuPrrbJcLTZTjRpDkzu6umks5FQMWgqmmAEgKj3RyxEc5KIXBZIF6B7Q9qBnGwj0MrMp4yGQxSJaH0e_FDTcwhSPkyoM9mJX93aiGK63o5SL3qwGCy3e_S9KddCRapyMQW8QxYB5Ry3cqdUzy",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Shi J.",
              "uri": "https://maps.google.com/maps/contrib/109191156742510319225",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLsnaXp-k6TWnCcY0db-Ij72MXwFBSV0IdTTHlN1N9DI5NNLw=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJRfplRKvHwoARS6jKeJrLLto/photos/AdCG2DO-jpm9Tnsno58y8RpqY4ecc9rf2DYpkc9qQixoLv-krVbnBpQT7K-4vielf-43E9eHf0-GWZVD4Zaq-cmnDdn1tAOc05_ZLKd1X5bJf5b0YuME76pjQRU2RPzFLzzsTRU3V5Dlr4SV8YF2Nl9xSEB69hzdRiT72vvm",
          "widthPx": 2700,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Ashok Hatwar",
              "uri": "https://maps.google.com/maps/contrib/111236990385940564322",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLf7azbPout_bUX8a48pBh9CztLQRzAO_Al8o91BmRb08-cFA=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "menuForChildren": False,
      "servesCocktails": True,
      "servesDessert": True,
      "restroom": True,
      "goodForGroups": True,
      "goodForWatchingSports": True,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "parkingOptions": {
        "paidParkingLot": True,
        "paidStreetParking": True,
        "paidGarageParking": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleRestroom": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Mexican restaurant and bar serving traditional dishes, plus beer, wine, cocktails and margaritas.",
          "languageCode": "en-US"
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJxRGIvkzGwoARrrvAkWzswnw",
            "placeId": "ChIJxRGIvkzGwoARrrvAkWzswnw",
            "displayName": {
              "text": "PricewaterhouseCoopers, LLP",
              "languageCode": "en"
            },
            "types": [
              "accounting",
              "establishment",
              "finance",
              "point_of_interest"
            ],
            "spatialRelationship": "ACROSS_THE_ROAD",
            "straightLineDistanceMeters": 59.702152,
            "travelDistanceMeters": 51.302032
          },
          {
            "name": "places/ChIJ8TvIE7HHwoAR7W9Tr2zza6Q",
            "placeId": "ChIJ8TvIE7HHwoAR7W9Tr2zza6Q",
            "displayName": {
              "text": "InterContinental Los Angeles Downtown, an IHG Hotel",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "lodging",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 105.32005,
            "travelDistanceMeters": 102.18042
          },
          {
            "name": "places/ChIJwTYORbHHwoARSygnvwueZMI",
            "placeId": "ChIJwTYORbHHwoARSygnvwueZMI",
            "displayName": {
              "text": "Chick-fil-A",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "food",
              "point_of_interest",
              "restaurant"
            ],
            "straightLineDistanceMeters": 66.23908,
            "travelDistanceMeters": 150.1515
          },
          {
            "name": "places/ChIJSZiFGLHHwoAR0Op4_Ylxh0k",
            "placeId": "ChIJSZiFGLHHwoAR0Op4_Ylxh0k",
            "displayName": {
              "text": "Target",
              "languageCode": "en"
            },
            "types": [
              "clothing_store",
              "department_store",
              "electronics_store",
              "establishment",
              "furniture_store",
              "home_goods_store",
              "point_of_interest",
              "shoe_store",
              "store"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 227.30414,
            "travelDistanceMeters": 214.30943
          },
          {
            "name": "places/ChIJK46NJrHHwoARaVJLvul0IcE",
            "placeId": "ChIJK46NJrHHwoARaVJLvul0IcE",
            "displayName": {
              "text": "FIGat7th",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest",
              "shopping_mall"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 209.46347,
            "travelDistanceMeters": 214.47699
          }
        ],
        "areas": [
          {
            "name": "places/ChIJFxgUlrPHwoARoUK2qWd6P9g",
            "placeId": "ChIJFxgUlrPHwoARoUK2qWd6P9g",
            "displayName": {
              "text": "Financial District",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "OUTSKIRTS"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo",
      "id": "ChIJj_5FxSLGwoAR8Jlbxey3fPo",
      "types": [
        "mexican_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(323) 536-2114",
      "internationalPhoneNumber": "+1 323-536-2114",
      "formattedAddress": "1335 Willow St A6, Los Angeles, CA 90013, USA",
      "addressComponents": [
        {
          "longText": "A6",
          "shortText": "A6",
          "types": [
            "subpremise"
          ],
          "languageCode": "en"
        },
        {
          "longText": "1335",
          "shortText": "1335",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "Willow Street",
          "shortText": "Willow St",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90013",
          "shortText": "90013",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "2237",
          "shortText": "2237",
          "types": [
            "postal_code_suffix"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632QQ9+QC",
        "compoundCode": "2QQ9+QC Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.0394718,
        "longitude": -118.23145960000001
      },
      "viewport": {
        "low": {
          "latitude": 34.0380379197085,
          "longitude": -118.23279448029149
        },
        "high": {
          "latitude": 34.0407358802915,
          "longitude": -118.23009651970851
        }
      },
      "rating": 4.3,
      "googleMapsUri": "https://maps.google.com/?cid=18049503634145384944",
      "websiteUri": "http://www.chuystacosdorados.com/",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 1,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 1,
              "hour": 20,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 20,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 20,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 20,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 5,
              "hour": 20,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 11,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 20,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 11:00 AM – 8:00 PM",
          "Tuesday: 11:00 AM – 8:00 PM",
          "Wednesday: 11:00 AM – 8:00 PM",
          "Thursday: 11:00 AM – 8:00 PM",
          "Friday: 11:00 AM – 8:00 PM",
          "Saturday: 11:00 AM – 8:00 PM",
          "Sunday: Closed"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e1335 Willow St A6\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90013-2237\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_INEXPENSIVE",
      "userRatingCount": 650,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Chuy's Tacos Dorados",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "reservable": False,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": False,
      "servesWine": False,
      "servesBrunch": False,
      "servesVegetarianFood": False,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 1,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 20,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 20,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 20,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 20,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 20,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 11,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 20,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 11:00 AM – 8:00 PM",
          "Tuesday: 11:00 AM – 8:00 PM",
          "Wednesday: 11:00 AM – 8:00 PM",
          "Thursday: 11:00 AM – 8:00 PM",
          "Friday: 11:00 AM – 8:00 PM",
          "Saturday: 11:00 AM – 8:00 PM",
          "Sunday: Closed"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "1335 Willow St A6, Los Angeles",
      "editorialSummary": {
        "text": "Taco spot specializing in slow-cooked beef.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/reviews/ChZDSUhNMG9nS0VJQ0FnSURUalBhTklnEAE",
          "relativePublishTimeDescription": "4 months ago",
          "rating": 5,
          "text": {
            "text": "Can’t say enough good things about Chuy’s Tacos Dorados! I had heard good things and had this mapped out for several months to try on our next trip to Los Angeles for my home in San Diego county. Happy to say these were as amazing as the hype if not better the service was excellent and they even offered water for our dogs.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Can’t say enough good things about Chuy’s Tacos Dorados! I had heard good things and had this mapped out for several months to try on our next trip to Los Angeles for my home in San Diego county. Happy to say these were as amazing as the hype if not better the service was excellent and they even offered water for our dogs.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Aaron Carpenter",
            "uri": "https://www.google.com/maps/contrib/107782070666599539002/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjV_7HKd933gMd0GOwEyl1FBQtwSGZDek9jKqrGtDwG2lEW4eMqX=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-05-23T03:36:24.792323Z"
        },
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/reviews/ChdDSUhNMG9nS0VJQ0FnSUNMeVpucWlRRRAB",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 4,
          "text": {
            "text": "I enjoyed eating here for the first time.  It has an open concept outside vibe as well as an 2nd floor patio set up.  You order at a kiosk and wait to be called.  The food is all al la Carte and I am satisfied with my order.  Parking can be a little tricky though.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "I enjoyed eating here for the first time.  It has an open concept outside vibe as well as an 2nd floor patio set up.  You order at a kiosk and wait to be called.  The food is all al la Carte and I am satisfied with my order.  Parking can be a little tricky though.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Gladys P. Bowden-Brown",
            "uri": "https://www.google.com/maps/contrib/106281450472300341943/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXshrv3573mrQoItlU0_GnDW8zHuinua0hENE6l7bGkEdordNUsmg=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-06-20T19:04:38.340292Z"
        },
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/reviews/ChdDSUhNMG9nS0VJQ0FnSUNEcWZYMDJBRRAB",
          "relativePublishTimeDescription": "6 months ago",
          "rating": 5,
          "text": {
            "text": "Don’t listen to the haters, this place is amazing. The tacos and quesadillas are very good, and the prices for the area are very low: 4-7$ for decent portions. The salsa is free. You can order from two tablets outdoors and the service is very fast",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Don’t listen to the haters, this place is amazing. The tacos and quesadillas are very good, and the prices for the area are very low: 4-7$ for decent portions. The salsa is free. You can order from two tablets outdoors and the service is very fast",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Arthur Bouffard",
            "uri": "https://www.google.com/maps/contrib/104000580830693724711/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVuDm8_iTy3AurwTwT6hEww-FnCpPBPlIjiinhdVdray9lIWp0Y4Q=s128-c0x00000000-cc-rp-mo-ba6"
          },
          "publishTime": "2024-03-30T00:10:07.769221Z"
        },
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/reviews/ChdDSUhNMG9nS0VJQ0FnSUNicU1uaW5nRRAB",
          "relativePublishTimeDescription": "2 months ago",
          "rating": 4,
          "text": {
            "text": "Cute spot for cheap eats in a generally overpriced area. Yes, the tacos are more expensive than your usual food truck, especially cause of tax and tip, as well as a mysterious service charge, however it’s still a great deal, cause these babies are STUFFED! I tried the shredded beef taco and it hit the spot. The shredded lettuce and cheese was piled high and the salsa was tastyyyy. Real old school nostalgia roadtrip mexi vibes. I haven’t had a hard shelled taco in ages, and it was fun to revisit. That being said, the lettuce and cheese are piled so high that it’s hard to eat and taste in the same bite as the beef. But a tasty unexpected stop for lunch, which I’d happily do again.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Cute spot for cheap eats in a generally overpriced area. Yes, the tacos are more expensive than your usual food truck, especially cause of tax and tip, as well as a mysterious service charge, however it’s still a great deal, cause these babies are STUFFED! I tried the shredded beef taco and it hit the spot. The shredded lettuce and cheese was piled high and the salsa was tastyyyy. Real old school nostalgia roadtrip mexi vibes. I haven’t had a hard shelled taco in ages, and it was fun to revisit. That being said, the lettuce and cheese are piled so high that it’s hard to eat and taste in the same bite as the beef. But a tasty unexpected stop for lunch, which I’d happily do again.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Ellen Máirín Johnston",
            "uri": "https://www.google.com/maps/contrib/107217509857765798874/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjW34xJjh6Tnc9xzgbK4PXyYUEwjsYhcdzieBA31_oRKu0kTJHOb=s128-c0x00000000-cc-rp-mo-ba3"
          },
          "publishTime": "2024-07-22T20:52:04.332295Z"
        },
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/reviews/ChdDSUhNMG9nS0VJQ0FnSUQ1NnJibF93RRAB",
          "relativePublishTimeDescription": "4 months ago",
          "rating": 5,
          "text": {
            "text": "I recently visited Chuy’s Tacos Dorados with my sister, and let me tell you, it’s hard to rate such a legendary taco place. The establishment may be small, but the food is absolutely amazing.\n\nWe all decided to go for the taco plate, and we were not disappointed. The tacos were hot and flavorful, and the beans were a real standout. Even though I didn’t get to try the rice myself, my boys devoured it and said it was delicious.\n\nThe sauce provided a nice kick, with the green sauce being surprisingly spicy this time around. It seems like they switched things up, but it was still fantastic.\n\nIf you find yourself in the area, do yourself a favor and stop by Chuy’s Tacos Dorados. The food is so, so, so good - you won’t regret it.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "I recently visited Chuy’s Tacos Dorados with my sister, and let me tell you, it’s hard to rate such a legendary taco place. The establishment may be small, but the food is absolutely amazing.\n\nWe all decided to go for the taco plate, and we were not disappointed. The tacos were hot and flavorful, and the beans were a real standout. Even though I didn’t get to try the rice myself, my boys devoured it and said it was delicious.\n\nThe sauce provided a nice kick, with the green sauce being surprisingly spicy this time around. It seems like they switched things up, but it was still fantastic.\n\nIf you find yourself in the area, do yourself a favor and stop by Chuy’s Tacos Dorados. The food is so, so, so good - you won’t regret it.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Justin Weathersbee (Blk182atN7)",
            "uri": "https://www.google.com/maps/contrib/114129849866770783157/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUsE6aBd4q-cF6NQY9zQtqN4s_rwh2x_7Qr4SO2QS_XdmKzGijHUA=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-06-11T14:10:15.540870Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/photos/AdCG2DPZeTzmbs5T7DJ2i_B8rbh4SDcaZvDJW-KLcytdIbY_-lWrDF_QWU0-V87zSZpJawk1x4nljTwoBwJ4orhfhvRHxOrfS1v3PxYoz2tDD9ei_Mn181WFBHaO7uIdRJJ8V2-YTmFgUi_XSdqTlfIAvK2Ei85Qc8_f2mIb",
          "widthPx": 4000,
          "heightPx": 3000,
          "authorAttributions": [
            {
              "displayName": "Eddie Velandia",
              "uri": "https://maps.google.com/maps/contrib/110249340698080213676",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUrnMEMwXFDcaA3fVTOuPVCYZPu8JpFxa9sFpOanV3y7GSb4rhA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/photos/AdCG2DPwh2LDucmV0sep_upo_VObb9g4i7AxBQSCZv_r19Mpu93isZJQQx0lyHizvvyxntMfky4fpC4Ipz0GsBhTrKbF1y_MUy-nlWZUuYGwKl2i6YrmX4xeHk1GirZqBXcTCHfBD8GrCvvrQw2Q3N_xmDa6rJ1VYAm1OVfc",
          "widthPx": 828,
          "heightPx": 466,
          "authorAttributions": [
            {
              "displayName": "Chuy's Tacos Dorados",
              "uri": "https://maps.google.com/maps/contrib/113604065000802606101",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWueu5RV86xAVnF3nykx8JLQfr576hJEi9TbhQa74RmVajIvDQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/photos/AdCG2DOCiFgW_TqWPosUndeomR-8uGEYK55CMvttasU5mNk05rA3CgR-xIiyC_1MOIobv4eXJkXQZ-Rc3GwXGc5pSJrN0_WtIZzWWKUaFg9rVtZbtfwuUEa2C6HtFwrnEoQkJ51AAz9QTmobDczapcvbASaZg32G9kId0tBT",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Aaron Carpenter",
              "uri": "https://maps.google.com/maps/contrib/107782070666599539002",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjV_7HKd933gMd0GOwEyl1FBQtwSGZDek9jKqrGtDwG2lEW4eMqX=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/photos/AdCG2DPRG2AiCZJJ0WPD2SE3jk0ADN6qn8K4WxEZejIt5J_bCbBtCIAlIpFJtw_sf0AVkeutEGGMDCz3Kt2MaufGdJROgue7YR4SDsJj9uJU7Ah-pLteaimtHsS_0teJgKhCyV57wIfF10gbJa3n3AQb51xRNjeE7uzx_HVO",
          "widthPx": 3072,
          "heightPx": 4080,
          "authorAttributions": [
            {
              "displayName": "Tonie Salogel",
              "uri": "https://maps.google.com/maps/contrib/111556801328308076388",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU1l2nOHjwRbqEx66gaRIp4UG-UPvryKYxhftWoA0Fowsj_nJk=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/photos/AdCG2DP3CUWmwYcFFkCwoKwQdfIfRTUF1lqiBXakkCp_zHlQOw-C6kn-JF9ZjtpxpMiT2TUnoEGjSLtSv5uiM9EnqGRSrTS0C0qKMn8XpWiaDEtZMTnvaw9JWINe5mypYaiXUgK3Q-jTHEs5hd5Yqo0Wu8sxToQ30AU_g1MN",
          "widthPx": 4000,
          "heightPx": 3000,
          "authorAttributions": [
            {
              "displayName": "Gladys P. Bowden-Brown",
              "uri": "https://maps.google.com/maps/contrib/106281450472300341943",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXshrv3573mrQoItlU0_GnDW8zHuinua0hENE6l7bGkEdordNUsmg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/photos/AdCG2DPcCYnZNVBS9qjpkTFc-9OCgT57AjCRLZsslnR6B2Q1KZtMYEN9CagdaD9eyxyaVrRFJ3kEcR_Lu3jLHDoW8ZTDPxbWqJbNiToXIAmqO8mdbZBqs8ZnQcvbw9QIlBl7gOXgHSCReK0QV2-O_N_Wfjw0bfjJ_fR6WnXz",
          "widthPx": 3000,
          "heightPx": 4000,
          "authorAttributions": [
            {
              "displayName": "Gladys P. Bowden-Brown",
              "uri": "https://maps.google.com/maps/contrib/106281450472300341943",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXshrv3573mrQoItlU0_GnDW8zHuinua0hENE6l7bGkEdordNUsmg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/photos/AdCG2DNBjvXAAdiklFCesx6gpD9oN-phM0kA-BnMZDojA73jm6IofQ9UvfkNaV3Cx6h6F2WDW8iBdiTrRNbsTqqg3ao9-h5xF9EA91wSGek_5cBPlJIs9SksBN966ka-6rz6UiEJ1B7l5Vyqs4kCzUwJyRJXbYyancFJ0QGd",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Justin Weathersbee (Blk182atN7)",
              "uri": "https://maps.google.com/maps/contrib/114129849866770783157",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUsE6aBd4q-cF6NQY9zQtqN4s_rwh2x_7Qr4SO2QS_XdmKzGijHUA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/photos/AdCG2DMg8eG1sBvmQ-H2ueSkkB5lzHFvm5_SWTBhNIQliG-B-Yt-JEKBgDublTK5wukqHM_Uhxte6e-P-wQ5nkPVPub-Li9IMJ2X43jNNusvntIdmLL-PJnKOMwX192If15lk_ohtF5kHNn_bXOsCXFvGmLfrYZ4c433fHiI",
          "widthPx": 3600,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Arthur Bouffard",
              "uri": "https://maps.google.com/maps/contrib/104000580830693724711",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVuDm8_iTy3AurwTwT6hEww-FnCpPBPlIjiinhdVdray9lIWp0Y4Q=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/photos/AdCG2DOhAi3QttqgtvBzzGrGsaeHxBMWTKMem7DOnlKUmBzlYmrYX6C5cQic3xNAkwKQI1RGG1_3ez_9w0T-AVcPtEnMxDxW_ap0tNHPukpcdeDw86GxjG_gYP3wgPXs5j4KI_eaDwg0dsUEz63nvj00cV-xF_q4YlDSbDcP",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Darryl Ford",
              "uri": "https://maps.google.com/maps/contrib/117806518920761852131",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjW-zGI77yjLzMW8CzJoesSW1v7q9bt71HUtm0ZMz8Wa76v-foz9Tg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJj_5FxSLGwoAR8Jlbxey3fPo/photos/AdCG2DP9rqdZsP6ySFhcRN50XDxgJqTnYc1FqQk9Q0fsmTZWCMrrG7pgAwAvIwno7NUF2704iwJiexxDLRx93nVDIBg49fGlluP37JH6h1icxWwKHvn3ZgutFAXpRiRcqRNwsLsJ90HZkWcYxozl3fEO4pJxHIfNHj1a81EG",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "kandyce segovia",
              "uri": "https://maps.google.com/maps/contrib/118391658762346188401",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjW6Oxfiol_JipILPfov0I4QRAHAVhoHR44ZmuBFX_2AMsIccTof=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "liveMusic": False,
      "menuForChildren": False,
      "servesCocktails": False,
      "servesCoffee": False,
      "goodForChildren": True,
      "goodForWatchingSports": False,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "parkingOptions": {
        "paidParkingLot": True,
        "freeStreetParking": True,
        "valetParking": False
      },
      "accessibilityOptions": {
        "wheelchairAccessibleParking": True,
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Casual spot offering classic Mexican fare, such as tacos and burritos, plus housemade salsa.",
          "languageCode": "en-US"
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJi4G5KCPGwoARZI_gTqJmHiI",
            "placeId": "ChIJi4G5KCPGwoARZI_gTqJmHiI",
            "displayName": {
              "text": "Zinc Café & Market",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "food",
              "point_of_interest",
              "restaurant"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 102.04192,
            "travelDistanceMeters": 145.4544
          },
          {
            "name": "places/ChIJD1v_6SLGwoARm83Iv5NYUeo",
            "placeId": "ChIJD1v_6SLGwoARm83Iv5NYUeo",
            "displayName": {
              "text": "6th St Bridge",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 150.67233,
            "travelDistanceMeters": 181.85599
          },
          {
            "name": "places/ChIJg7xPJCPGwoAReA9jUBE23DA",
            "placeId": "ChIJg7xPJCPGwoAReA9jUBE23DA",
            "displayName": {
              "text": "Blue Bottle Coffee",
              "languageCode": "en"
            },
            "types": [
              "cafe",
              "establishment",
              "food",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 106.69343,
            "travelDistanceMeters": 123.44603
          },
          {
            "name": "places/ChIJZdSkG3DGwoARAn-8yF-Kvvc",
            "placeId": "ChIJZdSkG3DGwoARAn-8yF-Kvvc",
            "displayName": {
              "text": "Two Bit Circus",
              "languageCode": "en"
            },
            "types": [
              "bar",
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 202.22122,
            "travelDistanceMeters": 372.12738
          },
          {
            "name": "places/ChIJLWWpYRjGwoARYfyFCGVqIFo",
            "placeId": "ChIJLWWpYRjGwoARYfyFCGVqIFo",
            "displayName": {
              "text": "6th Street Viaduct",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 318.8141,
            "travelDistanceMeters": 657.33954
          }
        ],
        "areas": [
          {
            "name": "places/ChIJP4e1VDrGwoAR4IoQrY1TbdQ",
            "placeId": "ChIJP4e1VDrGwoAR4IoQrY1TbdQ",
            "displayName": {
              "text": "Arts District",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "OUTSKIRTS"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJww7eN7PHwoARplLD_aQspDc",
      "id": "ChIJww7eN7PHwoARplLD_aQspDc",
      "types": [
        "mexican_restaurant",
        "bar",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 258-2280",
      "internationalPhoneNumber": "+1 213-258-2280",
      "formattedAddress": "401 S Grand Ave, Los Angeles, CA 90071, USA",
      "addressComponents": [
        {
          "longText": "401",
          "shortText": "401",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "South Grand Avenue",
          "shortText": "S Grand Ave",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90071",
          "shortText": "90071",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85633P2W+HM",
        "compoundCode": "3P2W+HM Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.051481599999995,
        "longitude": -118.25329810000001
      },
      "viewport": {
        "low": {
          "latitude": 34.049999769708492,
          "longitude": -118.25448708029151
        },
        "high": {
          "latitude": 34.052697730291491,
          "longitude": -118.25178911970852
        }
      },
      "rating": 4.2,
      "googleMapsUri": "https://maps.google.com/?cid=4009378655410279078",
      "websiteUri": "http://www.pezcantina.com/",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 1,
              "hour": 11,
              "minute": 30
            },
            "close": {
              "day": 1,
              "hour": 14,
              "minute": 30
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 11,
              "minute": 30
            },
            "close": {
              "day": 2,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 11,
              "minute": 30
            },
            "close": {
              "day": 3,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 11,
              "minute": 30
            },
            "close": {
              "day": 4,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 11,
              "minute": 30
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 16,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 11:30 AM – 2:30 PM",
          "Tuesday: 11:30 AM – 9:00 PM",
          "Wednesday: 11:30 AM – 9:00 PM",
          "Thursday: 11:30 AM – 9:00 PM",
          "Friday: 11:30 AM – 10:00 PM",
          "Saturday: 4:00 – 10:00 PM",
          "Sunday: Closed"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e401 S Grand Ave\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90071\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_MODERATE",
      "userRatingCount": 1053,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Pez Cantina",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "curbsidePickup": True,
      "reservable": True,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": True,
      "servesWine": True,
      "servesBrunch": True,
      "servesVegetarianFood": True,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 1,
              "hour": 11,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 14,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 11,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 11,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 11,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 11,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 16,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 11:30 AM – 2:30 PM",
          "Tuesday: 11:30 AM – 9:00 PM",
          "Wednesday: 11:30 AM – 9:00 PM",
          "Thursday: 11:30 AM – 9:00 PM",
          "Friday: 11:30 AM – 10:00 PM",
          "Saturday: 4:00 – 10:00 PM",
          "Sunday: Closed"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "401 S Grand Ave, Los Angeles",
      "editorialSummary": {
        "text": "Beach-inspired decor & a coastal-theme Mexican menu keep this sleek eatery relaxed and light.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/reviews/ChZDSUhNMG9nS0VJQ0FnSUNKbjZxRUVREAE",
          "relativePublishTimeDescription": "a year ago",
          "rating": 4,
          "text": {
            "text": "This place has very delicious food and drinks. I like how much flavor everything has. The drinks are very upscale. The only complaint is some of the items are a bit small in portion for the price point. The staff is very friendly, I recently had an incident where I got a chip in my eye (yes a chip) and someone from the kitchen staff came to help me and checked in on me. I was very grateful for his assistance. So far everything I have tried has been on point, shall return.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "This place has very delicious food and drinks. I like how much flavor everything has. The drinks are very upscale. The only complaint is some of the items are a bit small in portion for the price point. The staff is very friendly, I recently had an incident where I got a chip in my eye (yes a chip) and someone from the kitchen staff came to help me and checked in on me. I was very grateful for his assistance. So far everything I have tried has been on point, shall return.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Evelyn Diaz Reyes",
            "uri": "https://www.google.com/maps/contrib/112111951724709483619/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWIQVFO5AZiiTgaY61ozsd_2uTuGBnZS1l6qBGnQedCzNQfyW6P4g=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2023-07-07T21:48:26.511217Z"
        },
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/reviews/ChdDSUhNMG9nS0VJQ0FnSURONS1fWGl3RRAB",
          "relativePublishTimeDescription": "8 months ago",
          "rating": 5,
          "text": {
            "text": "Arturo is simply the best! Came for a quick power lunch with my coworkers. He smoothly brought in guac and chips and placed our drink order. Food was delicious and served with a smile. We will return soon!",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Arturo is simply the best! Came for a quick power lunch with my coworkers. He smoothly brought in guac and chips and placed our drink order. Food was delicious and served with a smile. We will return soon!",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Rita32117",
            "uri": "https://www.google.com/maps/contrib/115621849046109034165/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWNU52G8k6C4uhr57Zm-Kh914Z9Rw5t7vHHJUmgaukmXMFKm4ib=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-01-26T21:55:19.043778Z"
        },
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/reviews/ChdDSUhNMG9nS0VJQ0FnSUNWbkphTndBRRAB",
          "relativePublishTimeDescription": "10 months ago",
          "rating": 4,
          "text": {
            "text": "went for a company party. food was great, beautiful atmosphere but a bit cold. they only\nhad 8 heat lamps to serve a party of close to 80, but we also chose to have the party in cold December lol\n\nfood was delicious in my opinion and the the view was just beautiful being downtown.\n\ni feel like the waiters could have been a bit more on top of who chose what meal and they didn’t seem willing to serve extra guacamole 🥑 without asking for an extra charge.\n\nwith the understanding they were catering to a large party, i feel they did fairly well.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "went for a company party. food was great, beautiful atmosphere but a bit cold. they only\nhad 8 heat lamps to serve a party of close to 80, but we also chose to have the party in cold December lol\n\nfood was delicious in my opinion and the the view was just beautiful being downtown.\n\ni feel like the waiters could have been a bit more on top of who chose what meal and they didn’t seem willing to serve extra guacamole 🥑 without asking for an extra charge.\n\nwith the understanding they were catering to a large party, i feel they did fairly well.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Felicia",
            "uri": "https://www.google.com/maps/contrib/116950996564015826357/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocJlgi7_CO1dgjdVd1hmnsAOreMFvRY93DtTrWsoEiRPK28h6T98=s128-c0x00000000-cc-rp-mo-ba3"
          },
          "publishTime": "2023-12-06T02:03:11.291913Z"
        },
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/reviews/ChdDSUhNMG9nS0VJQ0FnSURqLTlmdTl3RRAB",
          "relativePublishTimeDescription": "5 months ago",
          "rating": 4,
          "text": {
            "text": "Staff is so nice and professional. I had a big party and they accommodated us perfectly. Food seems a little bit pricey for the taste, but overall the drinks and ambience make up for it.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Staff is so nice and professional. I had a big party and they accommodated us perfectly. Food seems a little bit pricey for the taste, but overall the drinks and ambience make up for it.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Mo s",
            "uri": "https://www.google.com/maps/contrib/103003776629942587873/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUZ6NJ8r5DWFOAg6_ppzD1RL1vSbvcJT-0FkyezZoC0q4VVxVtuQg=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-05-08T03:59:33.776596Z"
        },
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/reviews/ChdDSUhNMG9nS0VJQ0FnSUR6MEtucnZ3RRAB",
          "relativePublishTimeDescription": "4 months ago",
          "rating": 3,
          "text": {
            "text": "The food was okay. Lacked flavor and the wow factor. To my surprise parking was easy customer service was poured.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "The food was okay. Lacked flavor and the wow factor. To my surprise parking was easy customer service was poured.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Renee Matthews (LA Real Estate Agent)",
            "uri": "https://www.google.com/maps/contrib/113393072483520763317/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUJ850MkA_zyx9yUmAY6Z0luv5VWkoFAGkQdlOeeKWt4XEhUsci=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-06-06T23:04:46.696461Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/photos/AdCG2DPcLJtYvfWvvUfQzVNy5zPRSy2jzkuLQyTPZ-85OdHLZCOdZ3Tja3cHBinf_BWMkplhy0bbvczaG5ATMqaIO_ZIeHMfEJrWlv5KxneMQ4e9Q8KOJxhliM2nCv3xIqYKQvXbB-inYTJHnY-vtg0TC4qawwh9bheu_UtO",
          "widthPx": 4800,
          "heightPx": 3200,
          "authorAttributions": [
            {
              "displayName": "Pez Cantina",
              "uri": "https://maps.google.com/maps/contrib/111290987861067303911",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWapZBktI9sp3YRzuWGOIdxQvBaNR2Ntb_p9Ce2EtJfMITzYcNG=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/photos/AdCG2DPMtPzYx9JkwcoTBHYcvyj7govGW2saNNabmjft_ciP-qid3QOex8CrRhjWW3w6jVuTx4z1HxiHZ7TJx3aMp97UXuUcchjRQQ-9RV9H3l9z_tsTpFnRTb2RbHUOPUBVbvlOntLDRkEpmcJGz7xxiuycfg3mBdwchZ7h",
          "widthPx": 4000,
          "heightPx": 2672,
          "authorAttributions": [
            {
              "displayName": "Pez Cantina",
              "uri": "https://maps.google.com/maps/contrib/111290987861067303911",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWapZBktI9sp3YRzuWGOIdxQvBaNR2Ntb_p9Ce2EtJfMITzYcNG=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/photos/AdCG2DNW1ne0t_17mwrcDAHeF6VNphkHehtv6jAibe-T4WO-fhYJ1O750a9iW25Owi3zY00UPFpoJrylDdf3Z7jcSUZjGyffSprSozcRxy4BMawyoOVXGghUclr9vpVre20K3cvHa0p0mQaR8pSr6FJwRFVsrPhtXp8sL_r0",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Aldo Velasco",
              "uri": "https://maps.google.com/maps/contrib/106146848998542025584",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWrK9G_1S8oWjOvniNUnnQQF48CDNHcMDDWNl2gNTe-l30pCpQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/photos/AdCG2DMPlceRhHftuf5wFHLL3ZGgmK7re8mdkthkmI8OGrIevWGpmnqsa_tDcp_bwIwSu7HMT3C_wFw839XHRiboXUKoLci_agCM6PM8Aj6EL-rzK_iJmAgQmN8U9wM6SK6O1ETwh2rCA151UdXQenzy7Dic2z6eKosI1MZH",
          "widthPx": 3024,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Sev",
              "uri": "https://maps.google.com/maps/contrib/116356368744954732758",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUYUlmNKr_hbfZ380Ok0cHLZZLhtRo3ueSutBwPvm0L3pe5ybK1EQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/photos/AdCG2DPSrct4gVkjf6Br-JzZPccfHwFlULE5iXhUftF4A5Ca25pE-TntU9UzGy6EcfdwneFkUi58609HRriVjitd3LJH12fDyU2HQFpU2foJsD4fVlRqn7uY1yNTASC9lg90elsJp-NaZ8eWZUbUVM3WVvvB_Y7Rd9sPbT3X",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Zac (Wenzi)",
              "uri": "https://maps.google.com/maps/contrib/106157137788764263786",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVVIY8uKYDjf3f-YHt4bljnYvOe0Jr_zL6-d7xP2JUyP9waAV-N=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/photos/AdCG2DMrbBYa5NO_l00JkJl2GazuXjgJp6099ndFRyy8z58Kl6htNZ7ZMoz8OkSxUFUtElHEaq91tq4fGeNLb3WwL8Sx7v0kwSTHo4T2VX4Wiij2Jv5gjuOXry580dNWjIVIgMIwEdJxzuGQJeA3D4yj9jrolgfAIRvCM7x2",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "hajrush vlashi",
              "uri": "https://maps.google.com/maps/contrib/109393002039643991932",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXDBQdA30k4p6Gyr-aIu0xjJnLp_ipGvz7DSRBtl_9xQKWVhVg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/photos/AdCG2DOr9i1abw-30f0e1iGQHsXlgfqewQnxVrQ_qLegy56orGvuOB4QYXhPlxFAFYNhCs-uQ6VTHNc0Efk_SglwwA2uXMu-qv53G14ysDaL8Tm-9qoVXTVFZHS9OIJaW5UmUemn8yFiEvjecMY2ZuD9wwrv5GXvLhkNnF6q",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Connie Sparks",
              "uri": "https://maps.google.com/maps/contrib/114643794289635984122",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUrtKJuVC7_X1saHHz5hgM_CoT3tAT3qcZ5PpxItqDH1vGQIPM0=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/photos/AdCG2DOxiOGy0HxGZUde8WNjUN-B5kKiQkEOzh6WQtxigYZgL2hhMgn1jDWmufsjkzjSiRRRlrHjBupkvFMCDja8jSeibfDCzt51agkKQO7yE4h2ksv9F-elm4RL-bCkE-8rsASGgtwdB2_zSGQAW_tOdb7AVlhMz5VWxopX",
          "widthPx": 3072,
          "heightPx": 4080,
          "authorAttributions": [
            {
              "displayName": "Matthew Gruen",
              "uri": "https://maps.google.com/maps/contrib/116843115735333438200",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLJbgdEX2j8SZ7Q-Dy_82eTFAlRr4AoLiig5mY-c6wlUM9r5w=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/photos/AdCG2DMX-XNR65FHZz3-MdjH5UqVmWxaudWF8X6Kcbo4bSCj4cnsGJn4V6F9jVRy2Hab1Pxdc-UGOm0HAK98fZ7dG1ME0pfptMJgsSJKuMxVujiLoDVCclPEkZBLkyfjC701X9K5f7I6nYU7QynAX8ZLToaXk9MSmKrRx9AU",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "steezy",
              "uri": "https://maps.google.com/maps/contrib/108157750738336848443",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjX1046PlqKAOF_jJbMebEw7Vm4gM6mxmDX6jHCUoGMPPsqk6g1bvg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/photos/AdCG2DO1xqPrhtwQJLQmPVO7aXQeprz7KYTK4MjDTLqk_9L8qfRaYuTgJcTJoNGFaeaLZyQ9Mc_ky5wScItq064a50Lbh6Z-O5OKg9gH1aoU-0asEJjm_SnS5KWznIrghn4vH-G7GB6wTEO8mlgaPnTiAnrET6ZfcD8djVZr",
          "widthPx": 329,
          "heightPx": 280,
          "authorAttributions": [
            {
              "displayName": "Maureen Harris",
              "uri": "https://maps.google.com/maps/contrib/108343027394066802030",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocL4MKIHZokrK2AQc8xyqH4yjaJX_hLZ8T7eQyvgWFOIAXdPHg=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "liveMusic": True,
      "menuForChildren": True,
      "servesCocktails": True,
      "servesDessert": True,
      "servesCoffee": True,
      "goodForChildren": True,
      "allowsDogs": False,
      "restroom": True,
      "goodForGroups": True,
      "goodForWatchingSports": True,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleParking": True,
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleRestroom": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Coastal Mexican-style restaurant and bar serving sea-to-land fare, plus live music and a patio.",
          "languageCode": "en-US"
        },
        "description": {
          "text": "Trending Mexican restaurant in Downtown Los Angeles' Bunker Hill neighborhood serving coastal-style fare and margaritas for lunch, brunch, dinner, and late-night bites.\nThe menu focuses on dishes from various regions of Mexico, including vegetarian and healthy options. People like the ceviche and the molcajete. There are also happy hour specials.\nFeaturing a rooftop patio, the oasis-like venue has a cozy atmosphere and live music. It's good for watching sports, and popular for solo diners. Some people praise the attentive staff.\nCustomers typically spend $20–30.",
          "languageCode": "en-US"
        },
        "references": {
          "reviews": [
            {
              "name": "places/ChIJww7eN7PHwoARplLD_aQspDc/reviews/ChdDSUhNMG9nS0VJQ0FnSURKNXYydzdRRRAB",
              "relativePublishTimeDescription": "a year ago",
              "rating": 5,
              "text": {
                "text": "Good food. A twist to Mex food. Very attentive.",
                "languageCode": "en"
              },
              "originalText": {
                "text": "Good food. A twist to Mex food. Very attentive.",
                "languageCode": "en"
              },
              "authorAttribution": {
                "displayName": "Maria Corona",
                "uri": "https://www.google.com/maps/contrib/101758344958950936483/reviews",
                "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocJajTCqC1uqHASxK3YC4nMMEJD3RAXQE3FXzOXG_-HT-5pAeQ=s128-c0x00000000-cc-rp-mo-ba4"
              },
              "publishTime": "2023-07-16T08:39:49.513532Z"
            }
          ]
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJaT3J2LPHwoAR58Oo8wHj-o0",
            "placeId": "ChIJaT3J2LPHwoAR58Oo8wHj-o0",
            "displayName": {
              "text": "Chase Bank",
              "languageCode": "en"
            },
            "types": [
              "atm",
              "bank",
              "establishment",
              "finance",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 26.403612,
            "travelDistanceMeters": 24.278227
          },
          {
            "name": "places/ChIJDfep7bTHwoARampuf-EsLyc",
            "placeId": "ChIJDfep7bTHwoARampuf-EsLyc",
            "displayName": {
              "text": "American Business Bank",
              "languageCode": "en"
            },
            "types": [
              "bank",
              "establishment",
              "finance",
              "point_of_interest"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 56.65203,
            "travelDistanceMeters": 185.47871
          },
          {
            "name": "places/ChIJodbVu0zGwoARekw_P-O7D00",
            "placeId": "ChIJodbVu0zGwoARekw_P-O7D00",
            "displayName": {
              "text": "Deloitte",
              "languageCode": "en"
            },
            "types": [
              "accounting",
              "establishment",
              "finance",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 133.06262,
            "travelDistanceMeters": 85.66224
          },
          {
            "name": "places/ChIJpUaBoLTHwoARc-FN_jhLIB8",
            "placeId": "ChIJpUaBoLTHwoARc-FN_jhLIB8",
            "displayName": {
              "text": "Millennium Biltmore Hotel Los Angeles",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "lodging",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 198.76498,
            "travelDistanceMeters": 201.7417
          },
          {
            "name": "places/ChIJhctCXrPHwoAReR4UBjSN9Kk",
            "placeId": "ChIJhctCXrPHwoAReR4UBjSN9Kk",
            "displayName": {
              "text": "Torrey Pines Bank",
              "languageCode": "en"
            },
            "types": [
              "bank",
              "establishment",
              "finance",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 95.437294,
            "travelDistanceMeters": 116.10482
          }
        ],
        "areas": [
          {
            "name": "places/ChIJwYelS03GwoARE7_M6i6siCc",
            "placeId": "ChIJwYelS03GwoARE7_M6i6siCc",
            "displayName": {
              "text": "Bunker Hill",
              "languageCode": "en"
            },
            "containment": "OUTSKIRTS"
          },
          {
            "name": "places/ChIJFxgUlrPHwoARoUK2qWd6P9g",
            "placeId": "ChIJFxgUlrPHwoARoUK2qWd6P9g",
            "displayName": {
              "text": "Financial District",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0",
      "id": "ChIJFTDY1tDHwoAR1Cnjipl0kf0",
      "types": [
        "mexican_restaurant",
        "fast_food_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 335-5025",
      "internationalPhoneNumber": "+1 213-335-5025",
      "formattedAddress": "255 S Grand Ave, Los Angeles, CA 90012, USA",
      "addressComponents": [
        {
          "longText": "255",
          "shortText": "255",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "South Grand Avenue",
          "shortText": "S Grand Ave",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90012",
          "shortText": "90012",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85633P3X+9C",
        "compoundCode": "3P3X+9C Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.053450399999996,
        "longitude": -118.2513923
      },
      "viewport": {
        "low": {
          "latitude": 34.051985869708496,
          "longitude": -118.25251618029147
        },
        "high": {
          "latitude": 34.054683830291495,
          "longitude": -118.24981821970849
        }
      },
      "rating": 3.2,
      "googleMapsUri": "https://maps.google.com/?cid=18271513366027774420",
      "websiteUri": "https://locations.chipotle.com/ca/los-angeles/255-s-grand-ave?utm_source=google&utm_medium=yext&utm_campaign=yext_listings",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 10,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 10,
              "minute": 0
            },
            "close": {
              "day": 1,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 10,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 10,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 10,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 10,
              "minute": 0
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 10,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 10:00 AM – 10:00 PM",
          "Tuesday: 10:00 AM – 10:00 PM",
          "Wednesday: 10:00 AM – 10:00 PM",
          "Thursday: 10:00 AM – 10:00 PM",
          "Friday: 10:00 AM – 10:00 PM",
          "Saturday: 10:00 AM – 10:00 PM",
          "Sunday: 10:00 AM – 10:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e255 S Grand Ave\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90012\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_INEXPENSIVE",
      "userRatingCount": 57,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Chipotle Mexican Grill",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "reservable": False,
      "servesBreakfast": False,
      "servesLunch": True,
      "servesDinner": True,
      "servesBrunch": False,
      "servesVegetarianFood": True,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 10,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 10,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 10,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 10,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 10,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 10,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 10,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 10:00 AM – 10:00 PM",
          "Tuesday: 10:00 AM – 10:00 PM",
          "Wednesday: 10:00 AM – 10:00 PM",
          "Thursday: 10:00 AM – 10:00 PM",
          "Friday: 10:00 AM – 10:00 PM",
          "Saturday: 10:00 AM – 10:00 PM",
          "Sunday: 10:00 AM – 10:00 PM"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "255 S Grand Ave, Los Angeles",
      "editorialSummary": {
        "text": "Fast-food chain offering Mexican fare, including design-your-own burritos, tacos & bowls.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/reviews/ChZDSUhNMG9nS0VJQ0FnSUNIM2Q2cEhnEAE",
          "relativePublishTimeDescription": "a month ago",
          "rating": 3,
          "text": {
            "text": "Mexican food lovers can never say \"No\" to Chipotle! Chipotle food always tastes good and yummy.\n\nThe staff needs to clean dirty tables, though.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Mexican food lovers can never say \"No\" to Chipotle! Chipotle food always tastes good and yummy.\n\nThe staff needs to clean dirty tables, though.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Anudnya Kulkarni",
            "uri": "https://www.google.com/maps/contrib/111038865293771413392/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUOpOnuTkRpf7pnCJCFcF42VHDy3MTN8tzncuXa_B3CPOCnbDi8uw=s128-c0x00000000-cc-rp-mo-ba7"
          },
          "publishTime": "2024-09-07T22:35:45.553883Z"
        },
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/reviews/ChdDSUhNMG9nS0VJQ0FnSURyb0tYemtnRRAB",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 1,
          "text": {
            "text": "What a joke! I ordered CHICKEN with BLACK BEANS bowl and got vegetarian bowl full of RED BEANS with 3-4 pieces of chicken! What kind of blind people work there?!?! Disappointed!!! Never ever will order from this particular location!!",
            "languageCode": "en"
          },
          "originalText": {
            "text": "What a joke! I ordered CHICKEN with BLACK BEANS bowl and got vegetarian bowl full of RED BEANS with 3-4 pieces of chicken! What kind of blind people work there?!?! Disappointed!!! Never ever will order from this particular location!!",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Aizhan Muxayeva",
            "uri": "https://www.google.com/maps/contrib/105712285728044291745/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXLXuim7EpnUg5-2HxK6lk4ScGVSno-Ls9fBGk7HY7YoCHTTIM2=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-07-12T23:30:56.359601Z"
        },
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/reviews/ChZDSUhNMG9nS0VJQ0FnSUQ3b05peWFnEAE",
          "relativePublishTimeDescription": "a month ago",
          "rating": 4,
          "text": {
            "text": "First time to this location, only reason not a 5 star is parking. But otherwise same food you expect at chipotle, lots of seating available. Friendly staff and clean tables.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "First time to this location, only reason not a 5 star is parking. But otherwise same food you expect at chipotle, lots of seating available. Friendly staff and clean tables.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Kimberly H",
            "uri": "https://www.google.com/maps/contrib/105715819016193416754/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWlGjfZgXPRS1ac0cIfCCqdC0-q2XH-9l6gIm7X9uh07Zx-AzuCMw=s128-c0x00000000-cc-rp-mo-ba6"
          },
          "publishTime": "2024-08-20T02:29:58.045416Z"
        },
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/reviews/ChZDSUhNMG9nS0VJQ0FnSURCN0xIMFhnEAE",
          "relativePublishTimeDescription": "a year ago",
          "rating": 1,
          "text": {
            "text": "I admit that this is a prime location for Chipotle, but unfortunately this location specifically is terrible.\n\nService workers didn’t seem to care much about the customers. Without even having closed yet (atleast an hour away from closing), most ingredients were already put away. I came inside to pick up a mobile order when the place was virtually empty, and they still insisted I walk outside to the pickup window, instead of merely handing my meal to me inside (which was just a few steps away). Almost too funny to be True!\n\nThe best part: my chicken bowl had no chicken. Maybe 1-2 little nibbles worth. What a joke!\n\nLove Chipotle. Hate this location. Save your money and go elsewhere, especially with Chipotle prices racked up lately.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "I admit that this is a prime location for Chipotle, but unfortunately this location specifically is terrible.\n\nService workers didn’t seem to care much about the customers. Without even having closed yet (atleast an hour away from closing), most ingredients were already put away. I came inside to pick up a mobile order when the place was virtually empty, and they still insisted I walk outside to the pickup window, instead of merely handing my meal to me inside (which was just a few steps away). Almost too funny to be True!\n\nThe best part: my chicken bowl had no chicken. Maybe 1-2 little nibbles worth. What a joke!\n\nLove Chipotle. Hate this location. Save your money and go elsewhere, especially with Chipotle prices racked up lately.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Arin Sarkissian",
            "uri": "https://www.google.com/maps/contrib/112808743622361118105/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUwSgOHACueM9TXGB4nEv4Lzml4dNuiGWfot_oUW_rbkobd6JDk=s128-c0x00000000-cc-rp-mo-ba6"
          },
          "publishTime": "2023-01-13T18:29:34.175144Z"
        },
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/reviews/ChZDSUhNMG9nS0VJQ0FnSURueGZqbGJnEAE",
          "relativePublishTimeDescription": "a week ago",
          "rating": 1,
          "text": {
            "text": "This location is always out of veggies and for some reason they refuse to make more and then tell you the only other vegetarian option is some tofu stuff I don’t actually like and costs more. Here’s a pro tip: make more veggies if people always order veggies. It’s not rocket science.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "This location is always out of veggies and for some reason they refuse to make more and then tell you the only other vegetarian option is some tofu stuff I don’t actually like and costs more. Here’s a pro tip: make more veggies if people always order veggies. It’s not rocket science.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Lari Stang",
            "uri": "https://www.google.com/maps/contrib/109792019111168492002/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocIiYHR4NlAhbcusKswxgQtVluWk580pdhbTYp7rHTjjiWOyJA=s128-c0x00000000-cc-rp-mo-ba2"
          },
          "publishTime": "2024-10-07T21:53:09.934489Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/photos/AdCG2DOYzQ6ndoXch1Pzmi1L3zzd8oWTBoEkLE9fuUFKsK1o9S-jXvAq7pm1VbgheT5e3H_3Hz7xlRTNt5kc7nn9eZGCi47Ii6Q_t2m0nbt_edDX2sSTvdE-tOm58M2Rxy4GtPgt7WAyd5VgXJZSjkI_XloxtcYy8GPoMZ3i",
          "widthPx": 4160,
          "heightPx": 3120,
          "authorAttributions": [
            {
              "displayName": "Adam M",
              "uri": "https://maps.google.com/maps/contrib/101829170422726427745",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUVTJ1OdTVa2cNTlL5-2PbrGDd9Amh7gM3OXJ8wTRhwdS_a0wzoJA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/photos/AdCG2DMDHsv1wbqsa_55LYX0DNmhvPGOB8QM5GrWj0Jrnn1aS4ZcpjevOgWpaMHkSeka38Z16eOtxsCLeqHtn5bQzPuF09PeshGTKG9UqIIVNgxcQzPlHu8WmzEqA_za24KquE-Sij14qF9EKtUCPPwOMRRP27R4U_qGu6Xv",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Aizhan Muxayeva",
              "uri": "https://maps.google.com/maps/contrib/105712285728044291745",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXLXuim7EpnUg5-2HxK6lk4ScGVSno-Ls9fBGk7HY7YoCHTTIM2=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/photos/AdCG2DMvyza0LofvOeLQI8UDMGrn-fRcGoL1Z_EU-FvCV9tCdDkVvEJ0isxh1joVf3vmWg1pBud80vqSxFeGgL32wiVsYEIYWb2vH4VJwYbRd2bpAYZdYKgdc0zKgwTj5N45tnC7DOtKvoXV9WCV1IKMkIh9CN9s08c-bSWN",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Edward Orde",
              "uri": "https://maps.google.com/maps/contrib/103328358122391010909",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUqXyzBiijdR9v7AVdUw5KdjKIKvTi3pdOlwsw-3IyqVE1REnT96w=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/photos/AdCG2DNhjlMfE1R-P_vmovidsbXnF-Sd03S69JfBxgPRyLDEj3DxHmhHJEQB9z9oywEFqswvRX0TmBKpCU_YJNZtJzqBY6r4g0twMcKJPQ_30PP4fXvssarr5KiJUI4GplarL5SI-5okmZsZxUtvwn8I9COne7PMju8tcu-F",
          "widthPx": 2992,
          "heightPx": 2992,
          "authorAttributions": [
            {
              "displayName": "Oscar Chavez",
              "uri": "https://maps.google.com/maps/contrib/101302254850431607921",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXLZ2FnDvqGKVdcES_JoRTBXtCwPiWejrQAEwIP1_aaSqkHFF31=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/photos/AdCG2DPtXtO3XVEgPf7xJ-odw1HYrtP6Wzahfu4jN6CHsHFY_lQSF-WExjYR_kxFaAHpOixQajqhC0lhvQN8tRiTu7g34W3DSZdbP4ybOeOmsPFwwtRhtgwlemXxGszn6hGg-szLeL-kpgdxmVVJuMf5KktAUB_uV76DFfZ5",
          "widthPx": 2268,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "EDIE LINE",
              "uri": "https://maps.google.com/maps/contrib/103763289323297612902",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVcx2KLQTRj3g-9qzCZ614u4LByGXQxGZ7XhbFcBHxZi-a77SsK=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/photos/AdCG2DN4ic1Li0M9i3J-WxyqatSmlaiE9xECee9-O_4Na91ehIrl1Yc93oyVtmpv4FtVXgZqWDCPJuLPp1XZI3iuroKkHslbAqbb9_j_wD2z4NsAkFHkum6e7GltPM48Tn_e4Y7ZinRC4PyqyIC5GVbwn6QVljqSgG-KMhhO",
          "widthPx": 2992,
          "heightPx": 2992,
          "authorAttributions": [
            {
              "displayName": "Oscar Chavez",
              "uri": "https://maps.google.com/maps/contrib/101302254850431607921",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXLZ2FnDvqGKVdcES_JoRTBXtCwPiWejrQAEwIP1_aaSqkHFF31=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/photos/AdCG2DOiBku0FY1lbkSf0aef1-TniWZ0ukMBXYeQO9YeDc_0N4AuzgOH5-Tl0fuASaE2NomJlNVJXhlHgBLFfwwt0mXCsZ8YrDRtoThXrCkNvvPGNxEJRTKLxfCFWfH-LrL8OWZQxY-_NiSAGvNedRlYlP0_MSOP2LYK1gLb",
          "widthPx": 4032,
          "heightPx": 2268,
          "authorAttributions": [
            {
              "displayName": "EDIE LINE",
              "uri": "https://maps.google.com/maps/contrib/103763289323297612902",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVcx2KLQTRj3g-9qzCZ614u4LByGXQxGZ7XhbFcBHxZi-a77SsK=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/photos/AdCG2DNHMEjv5dudjiwU99zkXiMh3T1v1kqFC6WaDdqm6GlRmwoQDQBEKck7zseFDh0578J_Jhpe1FhLIgm7k9BW1RBnV0_6AJjJMecqI0-Zv8xqGInr0UivdWmE_980TaqsakHcg0dVOJOwH4_H_rIerLXbdBheD6FkAJba",
          "widthPx": 3600,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Kimberly H",
              "uri": "https://maps.google.com/maps/contrib/105715819016193416754",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWlGjfZgXPRS1ac0cIfCCqdC0-q2XH-9l6gIm7X9uh07Zx-AzuCMw=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/photos/AdCG2DPr7ODr6SfMnR7NuoJu-apcilBG7qHhjQIl3tRomo8PrZ2AKMk9o7Y3qNN-xIaf9rBwCzOfdgfFC630GpVy2bbD7LdHRhnq2UTYpGvpT_D74l51DaSwQFdEr-lAFTnAFBXkccWA_GPzs_DV2tsYaI-wBqGpEDY6HMyr",
          "widthPx": 3600,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Kimberly H",
              "uri": "https://maps.google.com/maps/contrib/105715819016193416754",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWlGjfZgXPRS1ac0cIfCCqdC0-q2XH-9l6gIm7X9uh07Zx-AzuCMw=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJFTDY1tDHwoAR1Cnjipl0kf0/photos/AdCG2DMhRDONeyC6kPhOk9EOpm9EBCXTkZkwjDIwx-BcvvzXeist0ohPFxncy9-T1vjs1LOWhxmivNguIXQa0zVmCwUMUJlW_hYsVv32piE_c0BdwhFQ_uHUW0PxJ_TfM_evKeZMJyHK_SgRylmOhncjBFLbqNB0xV84H2jw",
          "widthPx": 3600,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Kimberly H",
              "uri": "https://maps.google.com/maps/contrib/105715819016193416754",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWlGjfZgXPRS1ac0cIfCCqdC0-q2XH-9l6gIm7X9uh07Zx-AzuCMw=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "liveMusic": False,
      "menuForChildren": True,
      "servesDessert": False,
      "servesCoffee": False,
      "goodForChildren": True,
      "restroom": True,
      "goodForGroups": True,
      "goodForWatchingSports": False,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleParking": True,
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleRestroom": True,
        "wheelchairAccessibleSeating": True
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJXaYsEk3GwoARvx7RKBUE8Zg",
            "placeId": "ChIJXaYsEk3GwoARvx7RKBUE8Zg",
            "displayName": {
              "text": "The Broad",
              "languageCode": "en"
            },
            "types": [
              "art_gallery",
              "establishment",
              "museum",
              "point_of_interest",
              "tourist_attraction"
            ],
            "straightLineDistanceMeters": 161.69487
          },
          {
            "name": "places/ChIJNyYB20zGwoARilchsDXicdE",
            "placeId": "ChIJNyYB20zGwoARilchsDXicdE",
            "displayName": {
              "text": "Wells Fargo Bank",
              "languageCode": "en"
            },
            "types": [
              "atm",
              "bank",
              "establishment",
              "finance",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 114.26124
          },
          {
            "name": "places/ChIJc9UqAiXHwoARRktIsv23_aI",
            "placeId": "ChIJc9UqAiXHwoARRktIsv23_aI",
            "displayName": {
              "text": "The Museum of Contemporary Art, Los Angeles",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "museum",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 80.63975
          },
          {
            "name": "places/ChIJcVHLhVLGwoARfy5ZhYboW_Y",
            "placeId": "ChIJcVHLhVLGwoARfy5ZhYboW_Y",
            "displayName": {
              "text": "Subway",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "food",
              "meal_takeaway",
              "point_of_interest",
              "restaurant"
            ],
            "straightLineDistanceMeters": 29.636824
          },
          {
            "name": "places/ChIJvTeDLU3GwoAR5JZYnapXBg8",
            "placeId": "ChIJvTeDLU3GwoAR5JZYnapXBg8",
            "displayName": {
              "text": "Bank of America Financial Center",
              "languageCode": "en"
            },
            "types": [
              "bank",
              "establishment",
              "finance",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 160.1099
          }
        ],
        "areas": [
          {
            "name": "places/ChIJwYelS03GwoARE7_M6i6siCc",
            "placeId": "ChIJwYelS03GwoARE7_M6i6siCc",
            "displayName": {
              "text": "Bunker Hill",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw",
      "id": "ChIJa0ByTsrHwoARNAjZlAdlHTw",
      "types": [
        "mexican_restaurant",
        "fast_food_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "formattedAddress": "913 S Broadway, Los Angeles, CA 90015, USA",
      "addressComponents": [
        {
          "longText": "913",
          "shortText": "913",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "South Broadway",
          "shortText": "S Broadway",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90015",
          "shortText": "90015",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "1609",
          "shortText": "1609",
          "types": [
            "postal_code_suffix"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632PRV+V9",
        "compoundCode": "2PRV+V9 Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.0421282,
        "longitude": -118.2565099
      },
      "viewport": {
        "low": {
          "latitude": 34.040750769708495,
          "longitude": -118.25784588029148
        },
        "high": {
          "latitude": 34.043448730291495,
          "longitude": -118.25514791970849
        }
      },
      "rating": 4.2,
      "googleMapsUri": "https://maps.google.com/?cid=4331729499836713012",
      "websiteUri": "http://www.tacosmexico.com/",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 0,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: Open 24 hours",
          "Tuesday: Open 24 hours",
          "Wednesday: Open 24 hours",
          "Thursday: Open 24 hours",
          "Friday: Open 24 hours",
          "Saturday: Open 24 hours",
          "Sunday: Open 24 hours"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e913 S Broadway\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90015-1609\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_INEXPENSIVE",
      "userRatingCount": 758,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Tacos Mexico",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "reservable": False,
      "servesBreakfast": True,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": False,
      "servesWine": False,
      "servesBrunch": False,
      "servesVegetarianFood": False,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 4,
              "hour": 0,
              "minute": 0,
              "truncated": True,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 3,
              "hour": 23,
              "minute": 59,
              "truncated": True,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: Open 24 hours",
          "Tuesday: Open 24 hours",
          "Wednesday: Open 24 hours",
          "Thursday: Open 24 hours",
          "Friday: Open 24 hours",
          "Saturday: Open 24 hours",
          "Sunday: Open 24 hours"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "913 S Broadway, Los Angeles",
      "editorialSummary": {
        "text": "Casual regional chain serving Mexican fast fare, including desserts, beverages & breakfast.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/reviews/ChZDSUhNMG9nS0VJQ0FnSUM3ak5DMUNnEAE",
          "relativePublishTimeDescription": "2 months ago",
          "rating": 5,
          "text": {
            "text": "I’ve been here a few times throughout the years and it has not disappointed. The locale is pretty small, there are a few tables and chairs and a small little area with countertop where you can stand and eat. The food is good and the staff are attentive and friendly.\n\nThe only downside (which has nothing to do with the business itself) is that it’s located in the heart of downtown and there will be transients/druggies nearby which can make it uncomfortable to eat there. It’s definitely more of a grab and go than sit and eat type of place.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "I’ve been here a few times throughout the years and it has not disappointed. The locale is pretty small, there are a few tables and chairs and a small little area with countertop where you can stand and eat. The food is good and the staff are attentive and friendly.\n\nThe only downside (which has nothing to do with the business itself) is that it’s located in the heart of downtown and there will be transients/druggies nearby which can make it uncomfortable to eat there. It’s definitely more of a grab and go than sit and eat type of place.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "K S",
            "uri": "https://www.google.com/maps/contrib/106621886107039748396/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVnlbXiDTAT8iSeVNdWTwVS8fHZnKOmsLGcTWSJSHuaOIzzOP2I=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-08-13T05:31:07.012890Z"
        },
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/reviews/ChZDSUhNMG9nS0VJQ0FnSURUMzlfWEFREAE",
          "relativePublishTimeDescription": "4 months ago",
          "rating": 4,
          "text": {
            "text": "Great option for late night tacos. Amazing flavor at a decent price. The asasa was good but the carnitas was really good! And the hot salsa is actually hot!",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Great option for late night tacos. Amazing flavor at a decent price. The asasa was good but the carnitas was really good! And the hot salsa is actually hot!",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Trey P",
            "uri": "https://www.google.com/maps/contrib/111068625762020408673/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLYVqOsxdN--WsKQYSmGXZBfCL6bpE4Vd78QQ9YxHbaHXCNzA=s128-c0x00000000-cc-rp-mo-ba3"
          },
          "publishTime": "2024-05-29T13:27:11.738604Z"
        },
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/reviews/ChdDSUhNMG9nS0VJQ0FnSUNucE5UQ3BnRRAB",
          "relativePublishTimeDescription": "3 weeks ago",
          "rating": 5,
          "text": {
            "text": "About 6 years ago we seen a show at the ace.. we love Mexican food and tacos especially... we were so shocked to find this treasure right next door on our way in and out.. I stood and ate close to 10 tacos each serving and was ready to eat more if my belly would.have had room.. this is a close tie for #1 with my favorite taco shop anywhere iv traveled .. tire shop taqeria is the only.other place that's ever been THIS good",
            "languageCode": "en"
          },
          "originalText": {
            "text": "About 6 years ago we seen a show at the ace.. we love Mexican food and tacos especially... we were so shocked to find this treasure right next door on our way in and out.. I stood and ate close to 10 tacos each serving and was ready to eat more if my belly would.have had room.. this is a close tie for #1 with my favorite taco shop anywhere iv traveled .. tire shop taqeria is the only.other place that's ever been THIS good",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Johnathan Schmidt",
            "uri": "https://www.google.com/maps/contrib/104895227573489986468/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocI5PYfVNttxHtN2ki5PD7X3mXiS-ZuRPqf370oVYSKQVrciSg=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-09-22T23:37:34.944644Z"
        },
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/reviews/ChdDSUhNMG9nS0VJQ0FnSUM5bE5XajB3RRAB",
          "relativePublishTimeDescription": "7 months ago",
          "rating": 5,
          "text": {
            "text": "Asada tacos on point 👌🏽. Service was super quick and friendly. Open 24 hours. Parking lot right next to the stand.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Asada tacos on point 👌🏽. Service was super quick and friendly. Open 24 hours. Parking lot right next to the stand.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Jeff",
            "uri": "https://www.google.com/maps/contrib/108122599560019381118/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjW3gsxqlMyoXjvIyIAH-nAH4LFmmqA0b_KyeQZKz1-LzjH9_3ufpQ=s128-c0x00000000-cc-rp-mo-ba6"
          },
          "publishTime": "2024-03-02T18:04:58.180897Z"
        },
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/reviews/ChZDSUhNMG9nS0VJQ0FnSUNOelotM01REAE",
          "relativePublishTimeDescription": "9 months ago",
          "rating": 4,
          "text": {
            "text": "Came through for some late night tacos after a laker game.\n\nTJ style tacos, ~$2.50/taco. I got Cabeza, al pastor, and carne asada. Al pastor didn’t feel like it was cut from a trumpo but still was good. Carne cut into small sized pieces for the taco and had some caramelized edges. Cabeza was soft and cooked down well. That was my favorite of the group.\n\nAll tacos are TJ style so they tiny, 2-3 bites max per taco. So order a bunch if you’re hungry",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Came through for some late night tacos after a laker game.\n\nTJ style tacos, ~$2.50/taco. I got Cabeza, al pastor, and carne asada. Al pastor didn’t feel like it was cut from a trumpo but still was good. Carne cut into small sized pieces for the taco and had some caramelized edges. Cabeza was soft and cooked down well. That was my favorite of the group.\n\nAll tacos are TJ style so they tiny, 2-3 bites max per taco. So order a bunch if you’re hungry",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Ivan kirk Acayan",
            "uri": "https://www.google.com/maps/contrib/104784890471572271430/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLdEyTf_tKN-QpZabMhbEB67hgqJ-8EN8ZZTpk4h9dHDJz_Vw=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-01-16T19:44:43.215502Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/photos/AdCG2DNsB3ZEGrG9iyIrSs9mIWyaiqjT05TvKjMm2R7ssM9SqCDYO_MfhwUC4O1z4wcPYpJnLtH6tpaApsYsPaOB_CcsoiXjkEC7a6kM5zERWMA3SHTwdC9c0gjHKXU_Vw2V44uj_fuH7pdklcAm_mpUzcySEVtQYkfYKiLF",
          "widthPx": 3024,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Tõnu Ojala",
              "uri": "https://maps.google.com/maps/contrib/109213613128821008129",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWrxlbt3wlqb8RXXP_IiHbeRZuphchMMTDXH7a514QNDs8zdzluGg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/photos/AdCG2DPKba5Iu4y7Ljbgrd8XdPuIp8UHyBo_6LaTTE_-RI-VxgHvaN0AJuJbe8GTWPxupqgFMctuA88bK6veWvu3Tlly994djhdVfXq2DL5Oqvfkq4WhG6MvlELJINbO4ma2mdp-WK4rkF9GJgemHR6UNiV-YqxiEw8Xqa9P",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Jeff",
              "uri": "https://maps.google.com/maps/contrib/108122599560019381118",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjW3gsxqlMyoXjvIyIAH-nAH4LFmmqA0b_KyeQZKz1-LzjH9_3ufpQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/photos/AdCG2DNlbmrQVVCWflEt6InkRPqCwEhU67raH0X2WE0EMDv45EgHRvQ4hW0NXqRxKQeVfDw370q-2Ilydr7nH319zFwONgHEg-8s0d_ueEw-lSw0UAXC4nZzY2e1RlHtX9IWQhy--voTpyZPKUomIBDKVBp5eWENV9uMIePx",
          "widthPx": 3600,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Jason",
              "uri": "https://maps.google.com/maps/contrib/105372047508374638133",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUWdWnELivlDfHf9K9MuAMWkgM2W5wMLl455NE0j_HVDng7jHYo=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/photos/AdCG2DMUgBtLR6ip_5owm77zB_LNYlw5w6EHJwt-rGC1RFlkLIcrnwNt1qIYioLPmtlWcKYw0I2tyEnr583Cf7CyTVgBcLu3d1kKjwmsDvH59R5wkSwEeC8RlIQt5bInq9Zgb5sGLrlk_vzx8lJbT1juTq3J7wsy-tSNX2td",
          "widthPx": 4000,
          "heightPx": 3000,
          "authorAttributions": [
            {
              "displayName": "Trey P",
              "uri": "https://maps.google.com/maps/contrib/111068625762020408673",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLYVqOsxdN--WsKQYSmGXZBfCL6bpE4Vd78QQ9YxHbaHXCNzA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/photos/AdCG2DOj09qeZtalL8mz9_hJjqs9HkxH9UgKqB8Tr_R4M9LwjFBeHtlxLCwgV5tUR-vTV8x4QsrJTxe8A7TXat88u8NyFkUXbZ6B0ZCdtpVdpe-CTUp5b79dTnvTtJk-_cbV1mmPAWMC8RrDg7rr3aPohwP6I22dq80en7l2",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Jeff",
              "uri": "https://maps.google.com/maps/contrib/108122599560019381118",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjW3gsxqlMyoXjvIyIAH-nAH4LFmmqA0b_KyeQZKz1-LzjH9_3ufpQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/photos/AdCG2DPpyTnYrtz9B0DWUQRQwIqABOxP_c1Z0QYLdrRvfhMU1vqLR24DWraf9R1biod4Ve8F7dKvDf3MW_d2iUeNrckk0up0PcXiJSk8meGxYgL9qdjeHKneSUeNLpAgQ1DWgczZ--6Td1yUpPnfR5tJdIJNq14ItyIQjcNx",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Ivan kirk Acayan",
              "uri": "https://maps.google.com/maps/contrib/104784890471572271430",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLdEyTf_tKN-QpZabMhbEB67hgqJ-8EN8ZZTpk4h9dHDJz_Vw=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/photos/AdCG2DO9Oflr9k49k7_49lRZJbbjb3dfcWOfEsVZ9NJp0uTPQvHBsyne71t6_bzZxX53urd_LUx62FfCs65P9mhKa9Xj1TAE-wsc3xvY-20_zSuMFQHEJZR7LGRc28G8HXGi0lbVhHUNWpc7y05zoS-z1G8bgnqU-R5z3zzd",
          "widthPx": 4080,
          "heightPx": 3072,
          "authorAttributions": [
            {
              "displayName": "Francisco Hernandez",
              "uri": "https://maps.google.com/maps/contrib/117778775634997243286",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU0jwAQDNi8Lvc0E4jUFnl6YKURc2rai4npvo7OZ0BRpmbBSNUu=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/photos/AdCG2DMevOyGx8BdpYsTG7pZXEPoMyStL0YblCeKI4FdIZ844T_yhXeJfSx66zXq-RoxFlSWFL1fxIvnYw4kcEWu62QUR81kMvU05Eqd1vlEpmYIsfz3jGLucwVB7Q3CCV4EE1OsYwGDqROISvyTPdTHZh1p3PRJHuKMluFi",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Erik Delgado",
              "uri": "https://maps.google.com/maps/contrib/111186369034847860913",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXioiYss9g2UsI2-BkL58LrxC08xSXJFBj0fJdJSHGc0-ADPcsl=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/photos/AdCG2DNe_EbIPokwJ3DqYG0ydSxj-6__IqIIoohMKCTz-wn4UvoPMpXiteK7T_xZRMvieypzai_7eVAeQZ0-19ExPsGqBl2G3q21t4zy_BDzzB26H7IOq7V68GJgbo5B5BW6ZTGKVt4a_9HgOSWZP5iuzs6wmdgYCWdamd0",
          "widthPx": 2252,
          "heightPx": 4000,
          "authorAttributions": [
            {
              "displayName": "Aya Dijkwel",
              "uri": "https://maps.google.com/maps/contrib/101722842380832765431",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXWQmhoPAqchz8WzZG1oUbTPF3Zt9UBSRBcfHDNHS2ZpPJVjVs=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJa0ByTsrHwoARNAjZlAdlHTw/photos/AdCG2DOq6uKGRJo6ToYapgXdNEec4GfnZR1_q0ecIPCKFSwYb9M-Ffr735gDqE5KHZFKLwiAWoReyZTSUFCWXb34blgnWmY_txiDJa-lzb7PS6JYj5ANCGQR-Mc4vIJSpLKJWB2jei39HBz5RIHGqk8nLHaIMgwRlNFzvO3D",
          "widthPx": 2408,
          "heightPx": 1992,
          "authorAttributions": [
            {
              "displayName": "25 Ventnor Villas",
              "uri": "https://maps.google.com/maps/contrib/111772064481566811379",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWkSSOckZrk2xTAU29qYw6QGNK8fDkhe39lCi4jRr1mVE6YSkbO=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "liveMusic": False,
      "menuForChildren": False,
      "servesCocktails": False,
      "servesDessert": False,
      "servesCoffee": False,
      "restroom": False,
      "goodForWatchingSports": False,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "parkingOptions": {
        "paidParkingLot": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Tacos and other Mexican standards served in a casual space with late-night hours.",
          "languageCode": "en-US"
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJWQrC-crHwoARJvmB0kX7tbI",
            "placeId": "ChIJWQrC-crHwoARJvmB0kX7tbI",
            "displayName": {
              "text": "The Orpheum Theatre",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 119.33631,
            "travelDistanceMeters": 108.98238
          },
          {
            "name": "places/ChIJF7vjdMvHwoARoik8RlCo1Yg",
            "placeId": "ChIJF7vjdMvHwoARoik8RlCo1Yg",
            "displayName": {
              "text": "California Market Center",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 211.90137,
            "travelDistanceMeters": 233.6608
          },
          {
            "name": "places/ChIJL_hWS8rHwoARzpgvUnSUds0",
            "placeId": "ChIJL_hWS8rHwoARzpgvUnSUds0",
            "displayName": {
              "text": "STILE Downtown Los Angeles by Kasa",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "lodging",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 58.360943,
            "travelDistanceMeters": 73.480125
          },
          {
            "name": "places/ChIJNz-s1F_HwoARhUTJevovio0",
            "placeId": "ChIJNz-s1F_HwoARhUTJevovio0",
            "displayName": {
              "text": "west elm",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "furniture_store",
              "home_goods_store",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 53.214832,
            "travelDistanceMeters": 50.06826
          },
          {
            "name": "places/ChIJL_hWS8rHwoAR8tjTKEGvNyU",
            "placeId": "ChIJL_hWS8rHwoAR8tjTKEGvNyU",
            "displayName": {
              "text": "The United Theater on Broadway",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "movie_theater",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 68.443596,
            "travelDistanceMeters": 77.31214
          }
        ],
        "areas": [
          {
            "name": "places/ChIJw2qwSkrGwoARg4ZFCHwosJg",
            "placeId": "ChIJw2qwSkrGwoARg4ZFCHwosJg",
            "displayName": {
              "text": "Historic Core",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJN28nbMjHwoAR0mBlu0518tE",
            "placeId": "ChIJN28nbMjHwoAR0mBlu0518tE",
            "displayName": {
              "text": "South Park",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJi-nd5XXHwoARCEs032aQKkw",
      "id": "ChIJi-nd5XXHwoARCEs032aQKkw",
      "types": [
        "mexican_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "formattedAddress": "1280-1200 E Olympic Blvd, Los Angeles, CA 90021, USA",
      "addressComponents": [
        {
          "longText": "1280-1200",
          "shortText": "1280-1200",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "East Olympic Boulevard",
          "shortText": "E Olympic Blvd",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90021",
          "shortText": "90021",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632QJ4+Q6",
        "compoundCode": "2QJ4+Q6 Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.031982299999996,
        "longitude": -118.2444528
      },
      "viewport": {
        "low": {
          "latitude": 34.0308115197085,
          "longitude": -118.2458606302915
        },
        "high": {
          "latitude": 34.0335094802915,
          "longitude": -118.24316266970851
        }
      },
      "rating": 4.7,
      "googleMapsUri": "https://maps.google.com/?cid=5488357867410180872",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 18,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 1,
              "hour": 18,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 18,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 18,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 18,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 5,
              "hour": 18,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 18,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 9:00 AM – 6:00 PM",
          "Tuesday: 9:00 AM – 6:00 PM",
          "Wednesday: 9:00 AM – 6:00 PM",
          "Thursday: 9:00 AM – 6:00 PM",
          "Friday: 9:00 AM – 6:00 PM",
          "Saturday: 9:00 AM – 6:00 PM",
          "Sunday: 9:00 AM – 6:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e1280-1200 E Olympic Blvd\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90021\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "userRatingCount": 27,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Piñata District",
        "languageCode": "it"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "dineIn": True,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 18,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 18,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 18,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 18,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 18,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 18,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 18,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 9:00 AM – 6:00 PM",
          "Tuesday: 9:00 AM – 6:00 PM",
          "Wednesday: 9:00 AM – 6:00 PM",
          "Thursday: 9:00 AM – 6:00 PM",
          "Friday: 9:00 AM – 6:00 PM",
          "Saturday: 9:00 AM – 6:00 PM",
          "Sunday: 9:00 AM – 6:00 PM"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "1280-1200 E Olympic Blvd, Los Angeles",
      "reviews": [
        {
          "name": "places/ChIJi-nd5XXHwoARCEs032aQKkw/reviews/ChdDSUhNMG9nS0VJQ0FnSURuOW9LVm5nRRAB",
          "relativePublishTimeDescription": "a week ago",
          "rating": 5,
          "text": {
            "text": "Awesome helpful staff and an incredible selection of candy!",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Awesome helpful staff and an incredible selection of candy!",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Friendly_Ursa",
            "uri": "https://www.google.com/maps/contrib/108685544491097633556/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjV-j-bMm_MHC1_2zrj7dUSUbv0YnI8xdRVOiKx_cPEb0K1ShJei=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-10-05T18:32:35.351525Z"
        },
        {
          "name": "places/ChIJi-nd5XXHwoARCEs032aQKkw/reviews/ChZDSUhNMG9nS0VJQ0FnSURqbTliMVhnEAE",
          "relativePublishTimeDescription": "5 months ago",
          "rating": 5,
          "text": {
            "text": "No parking great prices",
            "languageCode": "en"
          },
          "originalText": {
            "text": "No parking great prices",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "xiomara Santin",
            "uri": "https://www.google.com/maps/contrib/117571376357406394516/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjX-U-8DjoTy0WNto9EK-F0qhHtHuUjinRrMAD70syPvzEZg9uRRvA=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-05-07T19:34:30.866077Z"
        },
        {
          "name": "places/ChIJi-nd5XXHwoARCEs032aQKkw/reviews/ChdDSUhNMG9nS0VJQ0FnSUNabnF5YTd3RRAB",
          "relativePublishTimeDescription": "a year ago",
          "rating": 5,
          "text": {
            "text": "Fun place to visit on Sundays",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Fun place to visit on Sundays",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Sal Campos",
            "uri": "https://www.google.com/maps/contrib/106313491968774693882/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocL5SOgfGg-H65ItQqbyucVhbvrwamx9qo6zS0b_RpdtpUrZunPZ=s128-c0x00000000-cc-rp-mo-ba6"
          },
          "publishTime": "2023-09-11T03:31:50.189928Z"
        },
        {
          "name": "places/ChIJi-nd5XXHwoARCEs032aQKkw/reviews/ChZDSUhNMG9nS0VJQ0FnSUNYcnZMa1RBEAE",
          "relativePublishTimeDescription": "in the last week",
          "rating": 5,
          "text": {
            "text": "Good quality piñatas",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Good quality piñatas",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Detsiriet Adame",
            "uri": "https://www.google.com/maps/contrib/108700897209530116156/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocICGMX2UIHfkLn57Zb5UsM7l5gYouTm8vUO-xQlCoAge0w4Dw=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-10-16T18:34:58.514006Z"
        },
        {
          "name": "places/ChIJi-nd5XXHwoARCEs032aQKkw/reviews/ChZDSUhNMG9nS0VJQ0FnSUQxdk1TNFRBEAE",
          "relativePublishTimeDescription": "4 months ago",
          "rating": 5,
          "text": {
            "text": "Good place to find all party themes and find delicious food 😋",
            "languageCode": "en-US"
          },
          "originalText": {
            "text": "Buen lugar para encontrar toda temática sobre fiestas y encuentras rica comida  😋",
            "languageCode": "es"
          },
          "authorAttribution": {
            "displayName": "Miguel Jahen",
            "uri": "https://www.google.com/maps/contrib/115691972615778448993/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVhmVCAt9cn3SG0djRnxhFOHVjbaIclXLW6zcCWGBR2H06CVCRuEg=s128-c0x00000000-cc-rp-mo-ba3"
          },
          "publishTime": "2024-05-24T19:00:51.590936Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJi-nd5XXHwoARCEs032aQKkw/photos/AdCG2DMu0Pexnm6-38vUOpYLZyq9awyMZVo7Qvlj2E1-eEESKZABRfvlkAlxCQc3DPfY-iwJuhfUrJ-NqBV2KN6YrbN1HlhrpunoVW--s68ZZOnvnareJe4AEoq1ihh6GPcmfeXYHJrav7Ym9AODW6mgp--cXoIyDhUQFWXo",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Wilber Mira",
              "uri": "https://maps.google.com/maps/contrib/111600845294933124279",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUoeOkpe7sXAA2cR9bN3QD0fNPobQZAZO-CVHLlvcCl8WUd7kha=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJi-nd5XXHwoARCEs032aQKkw/photos/AdCG2DM_o5f_sf7OSsK81Z_demrQekUl8OsWIGDRZQdjTQk1NZfbj_5940qE5rrNRm0hpyabnbeoIaiXRGWDcDGSOY8JE0d-0ZMYwkSj0iulQzbQIaM_HxmjhWoWMrFSjZUD4h0gslZTBWhblX1zNOyW14FyxmKa2Xbr7YdN",
          "widthPx": 3060,
          "heightPx": 4080,
          "authorAttributions": [
            {
              "displayName": "Mariana Reyes",
              "uri": "https://maps.google.com/maps/contrib/118068312410190091898",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocKHe38g8hzSBCCuZ6U6pe91mQLAksfABNiktrBK6nT9f0eLOA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJi-nd5XXHwoARCEs032aQKkw/photos/AdCG2DPY7gPCiZfrS_8VqxjVgQ3qSC6tOoBqQmc9-1Sc_uhcBal3YhVN6EnHQHaQxjilyUgFy1CQzek6uzdQREs8emN6Tg7VwgOLLjGEIBAuiQ0Zio1AkPbFWJdydLOMiICNE1nsU_vlUDZ_Z_PUMRVW8mhvgEN63WwphTBY",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Wilber Mira",
              "uri": "https://maps.google.com/maps/contrib/111600845294933124279",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUoeOkpe7sXAA2cR9bN3QD0fNPobQZAZO-CVHLlvcCl8WUd7kha=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJi-nd5XXHwoARCEs032aQKkw/photos/AdCG2DN4rWUMvtruTRSr_HluJJo07AQu1cZsQALFohPRcT9eCTpkSnkTW8T8s-SAMJIRRhH9sw3OAWz2oRcUaFY6LZE7e4GLXhSXrAFMVTlON3Z_gXz1JnHG4qQchgN29ey20ynUALj59v69Kj9MHPq7nwqzdaenRCm79--U",
          "widthPx": 3060,
          "heightPx": 4080,
          "authorAttributions": [
            {
              "displayName": "Mariana Reyes",
              "uri": "https://maps.google.com/maps/contrib/118068312410190091898",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocKHe38g8hzSBCCuZ6U6pe91mQLAksfABNiktrBK6nT9f0eLOA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJi-nd5XXHwoARCEs032aQKkw/photos/AdCG2DPtX1uzFa2oooWpztXcC5QYLpB_2ogYmjmKD3gcBGxfuUflXrQLa_X8cozslUuak8S3fqIvem8oPdL8nJoF2KZaPn0vgdthx0DQ-AG3ra4rjlSXkEHCYzh1y-gxEGdo6UOXXi6AhVHohNPq54EiVWhr4TpHNbVy428f",
          "widthPx": 2252,
          "heightPx": 4000,
          "authorAttributions": [
            {
              "displayName": "Sal Campos",
              "uri": "https://maps.google.com/maps/contrib/106313491968774693882",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocL5SOgfGg-H65ItQqbyucVhbvrwamx9qo6zS0b_RpdtpUrZunPZ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJi-nd5XXHwoARCEs032aQKkw/photos/AdCG2DNRsBa6E6IjMZ-JJMNQcd1RP5WKFM9MUYRci25N1T_F9IuVY6zSkrctffHMcLROv1zNWF4cqFSdEESAiJ1XciPWhjWcalaROD8HrQG7bT_yspfbut0cdbO47vMyIQCoAmvx24VoGYrtdx_GEITGCJrpH8-QfsGzfiz1",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Wilber Mira",
              "uri": "https://maps.google.com/maps/contrib/111600845294933124279",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUoeOkpe7sXAA2cR9bN3QD0fNPobQZAZO-CVHLlvcCl8WUd7kha=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJi-nd5XXHwoARCEs032aQKkw/photos/AdCG2DPXHN10r9TeE-JDWt_EgGfSEqZQKt3q6Vty92d0eppaMjwjPLyQoQ129mKy2nCVx8bsAyRKbbJauj8vCiZ2GMvscK2OVHosuB6G9usMggS3ewn3hc-Uos3YUyi2A4JG0yWM2XFgI9Qb1eGh6wZi9hiChZAevBBd-qhx",
          "widthPx": 2252,
          "heightPx": 4000,
          "authorAttributions": [
            {
              "displayName": "Sal Campos",
              "uri": "https://maps.google.com/maps/contrib/106313491968774693882",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocL5SOgfGg-H65ItQqbyucVhbvrwamx9qo6zS0b_RpdtpUrZunPZ=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "goodForChildren": True,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False
      },
      "accessibilityOptions": {
        "wheelchairAccessibleParking": True,
        "wheelchairAccessibleEntrance": True
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJU5WJ0i7GwoARfaYkbEM-ER0",
            "placeId": "ChIJU5WJ0i7GwoARfaYkbEM-ER0",
            "displayName": {
              "text": "Navarro’s Party Supply",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "home_goods_store",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "BESIDE",
            "straightLineDistanceMeters": 29.549355,
            "travelDistanceMeters": 15.247097
          },
          {
            "name": "places/ChIJ-x7tKCnGwoARw13GyEu1JJE",
            "placeId": "ChIJ-x7tKCnGwoARw13GyEu1JJE",
            "displayName": {
              "text": "McDonald's",
              "languageCode": "en"
            },
            "types": [
              "cafe",
              "establishment",
              "food",
              "point_of_interest",
              "restaurant",
              "store"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 110.25814,
            "travelDistanceMeters": 120.49525
          },
          {
            "name": "places/ChIJMePKfyXGwoAR7SsBsuWsli4",
            "placeId": "ChIJMePKfyXGwoAR7SsBsuWsli4",
            "displayName": {
              "text": "ROW DTLA",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "finance",
              "food",
              "point_of_interest",
              "restaurant",
              "shopping_mall"
            ],
            "straightLineDistanceMeters": 405.93478,
            "travelDistanceMeters": 301.15247
          },
          {
            "name": "places/ChIJ8V9kHi_GwoARwkpMD4D0uIE",
            "placeId": "ChIJ8V9kHi_GwoARwkpMD4D0uIE",
            "displayName": {
              "text": "Wells Fargo Bank",
              "languageCode": "en"
            },
            "types": [
              "atm",
              "bank",
              "establishment",
              "finance",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 161.5848,
            "travelDistanceMeters": 241.57329
          },
          {
            "name": "places/ChIJPS9KzS7GwoARAR5J7gxcRCQ",
            "placeId": "ChIJPS9KzS7GwoARAR5J7gxcRCQ",
            "displayName": {
              "text": "Dream Market",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "liquor_store",
              "point_of_interest",
              "store"
            ],
            "straightLineDistanceMeters": 52.414284,
            "travelDistanceMeters": 114.63747
          }
        ],
        "areas": [
          {
            "name": "places/ChIJf_9O_SzGwoARtrkWOBLCwII",
            "placeId": "ChIJf_9O_SzGwoARtrkWOBLCwII",
            "displayName": {
              "text": "Fashion District",
              "languageCode": "en"
            },
            "containment": "OUTSKIRTS"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "OUTSKIRTS"
          }
        ]
      }
    },
    {
      "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU",
      "id": "ChIJd0TBKcrHwoARbdU8Wx2vFuU",
      "types": [
        "mexican_restaurant",
        "fast_food_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 623-3306",
      "internationalPhoneNumber": "+1 213-623-3306",
      "formattedAddress": "301 W Olympic Blvd, Los Angeles, CA 90015, USA",
      "addressComponents": [
        {
          "longText": "301",
          "shortText": "301",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "West Olympic Boulevard",
          "shortText": "W Olympic Blvd",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90015",
          "shortText": "90015",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632PRR+RJ",
        "compoundCode": "2PRR+RJ Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.042015,
        "longitude": -118.25841
      },
      "viewport": {
        "low": {
          "latitude": 34.0405909697085,
          "longitude": -118.25966543029149
        },
        "high": {
          "latitude": 34.043288930291496,
          "longitude": -118.2569674697085
        }
      },
      "rating": 4.3,
      "googleMapsUri": "https://maps.google.com/?cid=16507574024792757613",
      "websiteUri": "https://locations.chipotle.com/ca/los-angeles/301-w-olympic-blvd?utm_source=google&utm_medium=yext&utm_campaign=yext_listings",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 10,
              "minute": 30
            },
            "close": {
              "day": 0,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 10,
              "minute": 30
            },
            "close": {
              "day": 1,
              "hour": 23,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 10,
              "minute": 30
            },
            "close": {
              "day": 2,
              "hour": 23,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 10,
              "minute": 30
            },
            "close": {
              "day": 3,
              "hour": 23,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 10,
              "minute": 30
            },
            "close": {
              "day": 4,
              "hour": 23,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 10,
              "minute": 30
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 10,
              "minute": 30
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 10:30 AM – 11:00 PM",
          "Tuesday: 10:30 AM – 11:00 PM",
          "Wednesday: 10:30 AM – 11:00 PM",
          "Thursday: 10:30 AM – 11:00 PM",
          "Friday: 10:30 AM – 10:00 PM",
          "Saturday: 10:30 AM – 10:00 PM",
          "Sunday: 10:30 AM – 10:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e301 W Olympic Blvd\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90015\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_INEXPENSIVE",
      "userRatingCount": 343,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Chipotle Mexican Grill",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "reservable": False,
      "servesBreakfast": False,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": True,
      "servesWine": False,
      "servesBrunch": False,
      "servesVegetarianFood": True,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 10,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 10,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 23,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 10,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 23,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 10,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 23,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 10,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 23,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 10,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 10,
              "minute": 30,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 22,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 10:30 AM – 11:00 PM",
          "Tuesday: 10:30 AM – 11:00 PM",
          "Wednesday: 10:30 AM – 11:00 PM",
          "Thursday: 10:30 AM – 11:00 PM",
          "Friday: 10:30 AM – 10:00 PM",
          "Saturday: 10:30 AM – 10:00 PM",
          "Sunday: 10:30 AM – 10:00 PM"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "301 W Olympic Blvd, Los Angeles",
      "editorialSummary": {
        "text": "Fast-food chain offering Mexican fare, including design-your-own burritos, tacos & bowls.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/reviews/ChdDSUhNMG9nS0VJQ0FnSUNuNG9HM3FRRRAB",
          "relativePublishTimeDescription": "3 weeks ago",
          "rating": 5,
          "text": {
            "text": "Had a great time coming to this location many times as it’s a staple of the downtown Los Angeles community. As I have had a couple business meetings here as I don’t really like to eat fast food. I feel this food is more fresh and the customer services are real solid at what they do. I look for passion and great service when I am eating out. I love to get the bowls whenever I am here over the burrito with chicken bowl, fajitas, lettuce, and even spinach as well. This place is always filled with a lot of clients. I would choose this everyday if I could.\n\nlocations.chipotle.com\n\nMonday - Thursday\n10:30 AM - 11:00 PM\nFriday - Sunday\n10:30 AM - 10:00 PM\n\nCHIPOTLE MEXICAN GRILL\n301 W Olympic Blvd\nLos Angeles, CA 90015\nNear Hill St & Olympic Blvd\n\nPICKUP OPTIONS\nopen content icon\nIn-Store Pickup, Delivery\nNEARBY STORES\nChipotle Mexican GrillLink Opens in New Tab\n601 W 7th St\nOpens at\n10:30 AM\n, Closes at\n11:00 PM\nChipotle Mexican GrillLink Opens in New Tab\n255 S Grand Ave\nOpens at\n10:00 AM\n, Closes at\n10:00 PM\nChipotle Mexican GrillLink Opens in New Tab\n1122 W 6th St\nOpens at\n10:00 AM\n, Closes at\n10:00 PM\nChipotle Mexican GrillLink Opens in New Tab\n2595 S Hoover St\nOpens at\n10:30 AM\n, Closes at\n11:00 PM\n\nTop sellers:\n\nBurrito\nYour choice of freshly grilled meat or sofritas wrapped in a warm flour tortilla with rice, beans, or fajita veggies, and topped with guac, salsa, queso blanco, sour cream or cheese.\nChicken, White Rice, Black Beans, Fresh Tomato Salsa, and Queso Blanco\n\nBurrito Bowl\nYour choice of freshly grilled meat or sofritas served in a delicious bowl with rice, beans, or fajita veggies, and topped with guac, salsa, queso blanco, sour cream or cheese.\nSteak, Supergreen Lettuce Blend, Fajita Veggies, Cheese, Guacamole, and Tomatillo Red-Chili Salsa\n\nLifestyle Bowl\nNo matter where you’re going, Lifestyle Bowls can help you get there–Keto, Whole30®, Vegan, Vegetarian, Paleo, High Protein, Gluten Free, Grain Free, you’re free to be you with our reimagined Lifestyle Bowls.\nWhite Rice, Pinto Beans, Cheese, Romaine Lettuce, Roasted Chili-Corn Salsa, Fresh Tomato Salsa, Sour Cream, and Guacamole\n\nTakeout\nDelivery\nGood for kids\nOutdoor dining\nOutdoor parking\nStreet parking\nParking lot\nContactless payments\n\nBurrito\nBowl\nTacos\nSalad\n\nOptions to choose from on the side:\n\nChicken $6.70\nCarnitas $7.20\nSteak $7.20\n\n2,000 calories daily chat\n\nGenuine Queso\nOn your burrito: $1.30\nOn the side: $2.30\nChips & Queso : $3.55\nLarge chips & Large Queso : $5.35",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Had a great time coming to this location many times as it’s a staple of the downtown Los Angeles community. As I have had a couple business meetings here as I don’t really like to eat fast food. I feel this food is more fresh and the customer services are real solid at what they do. I look for passion and great service when I am eating out. I love to get the bowls whenever I am here over the burrito with chicken bowl, fajitas, lettuce, and even spinach as well. This place is always filled with a lot of clients. I would choose this everyday if I could.\n\nlocations.chipotle.com\n\nMonday - Thursday\n10:30 AM - 11:00 PM\nFriday - Sunday\n10:30 AM - 10:00 PM\n\nCHIPOTLE MEXICAN GRILL\n301 W Olympic Blvd\nLos Angeles, CA 90015\nNear Hill St & Olympic Blvd\n\nPICKUP OPTIONS\nopen content icon\nIn-Store Pickup, Delivery\nNEARBY STORES\nChipotle Mexican GrillLink Opens in New Tab\n601 W 7th St\nOpens at\n10:30 AM\n, Closes at\n11:00 PM\nChipotle Mexican GrillLink Opens in New Tab\n255 S Grand Ave\nOpens at\n10:00 AM\n, Closes at\n10:00 PM\nChipotle Mexican GrillLink Opens in New Tab\n1122 W 6th St\nOpens at\n10:00 AM\n, Closes at\n10:00 PM\nChipotle Mexican GrillLink Opens in New Tab\n2595 S Hoover St\nOpens at\n10:30 AM\n, Closes at\n11:00 PM\n\nTop sellers:\n\nBurrito\nYour choice of freshly grilled meat or sofritas wrapped in a warm flour tortilla with rice, beans, or fajita veggies, and topped with guac, salsa, queso blanco, sour cream or cheese.\nChicken, White Rice, Black Beans, Fresh Tomato Salsa, and Queso Blanco\n\nBurrito Bowl\nYour choice of freshly grilled meat or sofritas served in a delicious bowl with rice, beans, or fajita veggies, and topped with guac, salsa, queso blanco, sour cream or cheese.\nSteak, Supergreen Lettuce Blend, Fajita Veggies, Cheese, Guacamole, and Tomatillo Red-Chili Salsa\n\nLifestyle Bowl\nNo matter where you’re going, Lifestyle Bowls can help you get there–Keto, Whole30®, Vegan, Vegetarian, Paleo, High Protein, Gluten Free, Grain Free, you’re free to be you with our reimagined Lifestyle Bowls.\nWhite Rice, Pinto Beans, Cheese, Romaine Lettuce, Roasted Chili-Corn Salsa, Fresh Tomato Salsa, Sour Cream, and Guacamole\n\nTakeout\nDelivery\nGood for kids\nOutdoor dining\nOutdoor parking\nStreet parking\nParking lot\nContactless payments\n\nBurrito\nBowl\nTacos\nSalad\n\nOptions to choose from on the side:\n\nChicken $6.70\nCarnitas $7.20\nSteak $7.20\n\n2,000 calories daily chat\n\nGenuine Queso\nOn your burrito: $1.30\nOn the side: $2.30\nChips & Queso : $3.55\nLarge chips & Large Queso : $5.35",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Ladi Saka",
            "uri": "https://www.google.com/maps/contrib/101604654856214513669/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVo9pQnfmnTh-yTrgOk_0LfagRCLvOCOnNNrl1Cm4F9ZNaz82F5=s128-c0x00000000-cc-rp-mo-ba6"
          },
          "publishTime": "2024-09-24T10:08:29.921674Z"
        },
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/reviews/ChdDSUhNMG9nS0VJQ0FnSUN0ekoyRGlBRRAB",
          "relativePublishTimeDescription": "8 months ago",
          "rating": 4,
          "text": {
            "text": "Chipotle has always been my favorite quick meal after a workout spot and this spot didn’t disappoint.\n\nGot myself a salad bowl with roasted vegetables, chicken, machaca beef, little bit of corn, little bit of cheese, little bit of sour cream and guacamole for a filling & satisfying lunch.\n\nI’d definitely come back here again and try their other menu items.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Chipotle has always been my favorite quick meal after a workout spot and this spot didn’t disappoint.\n\nGot myself a salad bowl with roasted vegetables, chicken, machaca beef, little bit of corn, little bit of cheese, little bit of sour cream and guacamole for a filling & satisfying lunch.\n\nI’d definitely come back here again and try their other menu items.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Rodrigo “funning”",
            "uri": "https://www.google.com/maps/contrib/117621384126831676862/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU66q7s69xnIgG16vNq6uvDZaMF9tEXwzGs7WPIbqyH1YCNbsEXUA=s128-c0x00000000-cc-rp-mo-ba7"
          },
          "publishTime": "2024-01-29T14:41:38.979186Z"
        },
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/reviews/ChZDSUhNMG9nS0VJQ0FnSURUbWVLNlJBEAE",
          "relativePublishTimeDescription": "4 months ago",
          "rating": 1,
          "text": {
            "text": "I ordered online and was only give TWO PIECES OF BEEF in my online order. I will never order online and if they do this in person I would have refused the food. So disrespectful! TWO PIECES OF BEEF! Are you kidding me!",
            "languageCode": "en"
          },
          "originalText": {
            "text": "I ordered online and was only give TWO PIECES OF BEEF in my online order. I will never order online and if they do this in person I would have refused the food. So disrespectful! TWO PIECES OF BEEF! Are you kidding me!",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "cameron james",
            "uri": "https://www.google.com/maps/contrib/110669481992860528719/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWKH27q_9wQ7iwg9gCVD2KMkBRpTWHGlXUdlXyoiOnopzK4HwdR=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-05-25T21:59:47.171091Z"
        },
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/reviews/ChdDSUhNMG9nS0VJQ0FnSURyck1PUDF3RRAB",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 5,
          "text": {
            "text": "I often came here on my lunch break and always felt safe despite the iffy neighborhood. The corner is improving, with a new high rise being built by the Mayan club. The food never disappoints, and the staff are very friendly. Best of all, they handle long lines efficiently without lagging.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "I often came here on my lunch break and always felt safe despite the iffy neighborhood. The corner is improving, with a new high rise being built by the Mayan club. The food never disappoints, and the staff are very friendly. Best of all, they handle long lines efficiently without lagging.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Brett P",
            "uri": "https://www.google.com/maps/contrib/102388709992721278434/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocJDjQMKl6BHCRbJICQ1BCo5NyAm9V8HY1OfQkRM0F8NhVu-0A=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-07-15T18:09:43.520386Z"
        },
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/reviews/ChZDSUhNMG9nS0VJQ0FnSUMwcVpIdUtBEAE",
          "relativePublishTimeDescription": "5 months ago",
          "rating": 5,
          "text": {
            "text": "I would come here on my lunch break. Although the neighborhood could be a little bit iffy I always felt safe going to this establishment and even eating there. I would say this corner is pretty up and coming as there is a new high rise being built by the Mayan club. But back to the food itself it never disappoints. Staff there are very friendly. And best of all I never felt like they lag when the line gets long.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "I would come here on my lunch break. Although the neighborhood could be a little bit iffy I always felt safe going to this establishment and even eating there. I would say this corner is pretty up and coming as there is a new high rise being built by the Mayan club. But back to the food itself it never disappoints. Staff there are very friendly. And best of all I never felt like they lag when the line gets long.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Alen Beygelman",
            "uri": "https://www.google.com/maps/contrib/107652157466511028053/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjUj6JD42DXHo-acIyvG4IXHP8a3XJNIH0m8RC_8X_lFmusNiHp0ww=s128-c0x00000000-cc-rp-mo-ba6"
          },
          "publishTime": "2024-05-14T05:37:40.449614Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/photos/AdCG2DPmj_K1jzW3bNpJm2EgwWG-pefe2Opj0op9EWguSrr6TRV4UZ1QM980GBEjBtjrL6H4QN32GB620JloctIcaxrJG2od2wqhgpR5cW-1GNvn5nonifnca5BH5Y5fA-q08HtTsLVRorippde3GqtMMFSZUwKVAp1Wdw10",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Ladi Saka",
              "uri": "https://maps.google.com/maps/contrib/101604654856214513669",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVo9pQnfmnTh-yTrgOk_0LfagRCLvOCOnNNrl1Cm4F9ZNaz82F5=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/photos/AdCG2DOE6Xdr9wfIj9rnsXmo-N48APN3V8EEu5LNZ90ZcgSkzBFC9Nt3O-YKJp-O0kIZ08ArEaeqgU4pf6ucqVp5YfaK8dLr7K2vqWQf0CO0gDZ2IrQwrFJjAhDzcV-9NJqVq4TZuWyvFRyy_t7JoMpua094lP927kvC9lc6",
          "widthPx": 3600,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Rodrigo “funning”",
              "uri": "https://maps.google.com/maps/contrib/117621384126831676862",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU66q7s69xnIgG16vNq6uvDZaMF9tEXwzGs7WPIbqyH1YCNbsEXUA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/photos/AdCG2DNzB2S2SkgektPFZoPB-i-NUhavHYhY8bOZMZB9XGqNwqAw0Xr5YR-6Ichoj4wem_FEc1Ctpq3kAjaPO4ptWQy-vR02AVAyuHuPFrFxPaHCryXjjLNhEU4csWUf7cQtsCox2olZeAFIrfp-RRBgMZndwGu1ypwww3AP",
          "widthPx": 1290,
          "heightPx": 968,
          "authorAttributions": [
            {
              "displayName": "Ladi Saka",
              "uri": "https://maps.google.com/maps/contrib/101604654856214513669",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVo9pQnfmnTh-yTrgOk_0LfagRCLvOCOnNNrl1Cm4F9ZNaz82F5=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/photos/AdCG2DO-yZ9YlzDhoBiT3hG5b7FyD_gEgOVfGOyj0jCUPKhImn-teJPePqqPW2VhOwoGxSI960XCVnujN-dzcX2TqXoRZlpbvwGnG4K7ikvJ7zFDllEmoOLHmcxQcfdxSTt5OKxIgnvGV97hQ6ysvHjK_CEKOZJX0EXlE-_e",
          "widthPx": 1290,
          "heightPx": 934,
          "authorAttributions": [
            {
              "displayName": "Ladi Saka",
              "uri": "https://maps.google.com/maps/contrib/101604654856214513669",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVo9pQnfmnTh-yTrgOk_0LfagRCLvOCOnNNrl1Cm4F9ZNaz82F5=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/photos/AdCG2DOk4EcAtnar1_p1vZ8WZ1Gzrmc7gF6u7O98jfC-Hiqd-FXuRWVQYFRFkcj5mreqFU9KVf4-i15dV57pAuKWykg7f56tD2x4yHqMPARozBfdXCb9ZvQ_5p8wn_Dt-qI8qMP2WHyZAu8yag8xHkz1DArYmvWxi2AKQVEA",
          "widthPx": 1290,
          "heightPx": 739,
          "authorAttributions": [
            {
              "displayName": "Ladi Saka",
              "uri": "https://maps.google.com/maps/contrib/101604654856214513669",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVo9pQnfmnTh-yTrgOk_0LfagRCLvOCOnNNrl1Cm4F9ZNaz82F5=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/photos/AdCG2DMn6-8sGI6u9p1bu59ApJl0BZRDKZFE8rCosUNKR56bgsWs0-mrLTdYcrOz_YwgBPiK_iEkdB81C7o3c0hCSXzSYExq0L-QEX4fsJijd6Zfi9nGn246HoyO1XWNjKT9eKFRMavt5LQPNjSRHLV0UdPHeLUGjOQKQOsN",
          "widthPx": 3456,
          "heightPx": 4608,
          "authorAttributions": [
            {
              "displayName": "Mom RIP Sister R I P (Nikki Mom)",
              "uri": "https://maps.google.com/maps/contrib/117425408460128459259",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU1qRahq3c8QT-9ZVVu6STV1VnoEPgUY8m2Bv5NUOd68M3BFo5Y=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/photos/AdCG2DPh3415we0e9JILTy-PatpTIyF32OUJ56IgXkShzlOxzjjcL0CZGXoT2Pk-_v1P_-pmGVvca4i-Nz5GvtkDP7m9DNMK1K21UW5vBmk5ge56-Zc4tODPc91NDf4QrjaVkriPcQOXpTmZLnyG9s91R9C7rQGRudInsIB7",
          "widthPx": 1290,
          "heightPx": 1680,
          "authorAttributions": [
            {
              "displayName": "Ladi Saka",
              "uri": "https://maps.google.com/maps/contrib/101604654856214513669",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVo9pQnfmnTh-yTrgOk_0LfagRCLvOCOnNNrl1Cm4F9ZNaz82F5=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/photos/AdCG2DN6XNMuvVHhgDw2Ns5k-2froRwe45Ht1tuvcjbQNfdvACK2teYSceL_K3C3uOSuPqsdTGqVLylqDFj0KUYyN5nKrFGYhQC95YqPM6e0YRwrE8chr9JDBsBOk_KRdlo6dZqMxkER46r8IWDV7YKS_TdYHI0i4Wr1xUlD",
          "widthPx": 4608,
          "heightPx": 3456,
          "authorAttributions": [
            {
              "displayName": "Mom RIP Sister R I P (Nikki Mom)",
              "uri": "https://maps.google.com/maps/contrib/117425408460128459259",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU1qRahq3c8QT-9ZVVu6STV1VnoEPgUY8m2Bv5NUOd68M3BFo5Y=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/photos/AdCG2DM89a2JuI1DYyp5yh6nyTZub9Q22F5t_xn9_S6KR3GuwAoTqioa7BJEYtbnJlGcBWfv5dRJiCJSnUt1kt6Lsod7gARQcMXBq66zXrD4dpIPRGezPvy1ouG2bz9GP9h1S7M7XByDwEmntTFuZoBv-WgG3OnUZ_wEBDT9",
          "widthPx": 3264,
          "heightPx": 2448,
          "authorAttributions": [
            {
              "displayName": "Patchy Pa Patches",
              "uri": "https://maps.google.com/maps/contrib/100491170924252316722",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWldoZBkp80Ov-eGA3hYJhoyWU5BFDPKnWrsNzs8DvdEhpRkVSd=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJd0TBKcrHwoARbdU8Wx2vFuU/photos/AdCG2DPzH3-Q58Eg8wf_aj8ScYHIQfrX4hAbwcGV7C08NIrWRzihzubpK3O_hKhdZkba-sx4HjtzVfPMjB4ae_CXBtHDMOgww4eDVtsxcxf5QDK1xMEg1cNFg5MWHcymCUZGI-kRJuV5qhTVzuxcLWXAwia2g6Aik_k_LZqQ",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Edgar Rivas",
              "uri": "https://maps.google.com/maps/contrib/107277035995535461296",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVG1VgLGHg4WK0Q2_awySItQ77khVUhqIQNbWQXgfikrTLyko4B7Q=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "liveMusic": False,
      "menuForChildren": True,
      "servesCocktails": False,
      "servesDessert": False,
      "servesCoffee": False,
      "goodForChildren": True,
      "restroom": True,
      "goodForGroups": True,
      "goodForWatchingSports": False,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "parkingOptions": {
        "paidStreetParking": True,
        "paidGarageParking": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleParking": True,
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleRestroom": True,
        "wheelchairAccessibleSeating": True
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJL_hWS8rHwoARzpgvUnSUds0",
            "placeId": "ChIJL_hWS8rHwoARzpgvUnSUds0",
            "displayName": {
              "text": "STILE Downtown Los Angeles by Kasa",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "lodging",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 111.92285,
            "travelDistanceMeters": 248.46024
          },
          {
            "name": "places/ChIJA76xJcrHwoART08Chu8l36c",
            "placeId": "ChIJA76xJcrHwoART08Chu8l36c",
            "displayName": {
              "text": "South Park by Windsor Apartments",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest",
              "real_estate_agency"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 48.9797,
            "travelDistanceMeters": 70.23478
          },
          {
            "name": "places/ChIJT359ZcnHwoARlzqycZrBhdc",
            "placeId": "ChIJT359ZcnHwoARlzqycZrBhdc",
            "displayName": {
              "text": "The Belasco",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "night_club",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 201.59605,
            "travelDistanceMeters": 199.01022
          },
          {
            "name": "places/ChIJL_hWS8rHwoAR8tjTKEGvNyU",
            "placeId": "ChIJL_hWS8rHwoAR8tjTKEGvNyU",
            "displayName": {
              "text": "The United Theater on Broadway",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "movie_theater",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 122.888115,
            "travelDistanceMeters": 244.62822
          },
          {
            "name": "places/ChIJWQrC-crHwoARJvmB0kX7tbI",
            "placeId": "ChIJWQrC-crHwoARJvmB0kX7tbI",
            "displayName": {
              "text": "The Orpheum Theatre",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 276.8551,
            "travelDistanceMeters": 329.34842
          }
        ],
        "areas": [
          {
            "name": "places/ChIJN28nbMjHwoAR0mBlu0518tE",
            "placeId": "ChIJN28nbMjHwoAR0mBlu0518tE",
            "displayName": {
              "text": "South Park",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          }
        ]
      }
    },
    {
      "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E",
      "id": "ChIJ97N_50TGwoARAMKHgO5qa6E",
      "types": [
        "mexican_restaurant",
        "fast_food_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(213) 687-4391",
      "internationalPhoneNumber": "+1 213-687-4391",
      "formattedAddress": "E 23 Olvera St, Los Angeles, CA 90012, USA",
      "addressComponents": [
        {
          "longText": "E 23",
          "shortText": "E 23",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "Olvera Street",
          "shortText": "Olvera St",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Downtown Los Angeles",
          "shortText": "Downtown Los Angeles",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90012",
          "shortText": "90012",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85633Q57+52",
        "compoundCode": "3Q57+52 Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.0579886,
        "longitude": -118.2374002
      },
      "viewport": {
        "low": {
          "latitude": 34.0567516197085,
          "longitude": -118.23874533029149
        },
        "high": {
          "latitude": 34.0594495802915,
          "longitude": -118.2360473697085
        }
      },
      "rating": 4.4,
      "googleMapsUri": "https://maps.google.com/?cid=11631508035205579264",
      "websiteUri": "http://www.cielitolindo.org/",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 20,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 1,
              "hour": 20,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 20,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 20,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 20,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 5,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 21,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 9:00 AM – 8:00 PM",
          "Tuesday: 9:00 AM – 8:00 PM",
          "Wednesday: 9:00 AM – 8:00 PM",
          "Thursday: 9:00 AM – 8:00 PM",
          "Friday: 9:00 AM – 9:00 PM",
          "Saturday: 9:00 AM – 9:00 PM",
          "Sunday: 9:00 AM – 8:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003eE 23 Olvera St\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90012\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_INEXPENSIVE",
      "userRatingCount": 2325,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Cielito Lindo",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": False,
      "dineIn": True,
      "curbsidePickup": False,
      "reservable": False,
      "servesBreakfast": False,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": False,
      "servesWine": False,
      "servesBrunch": False,
      "servesVegetarianFood": False,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 20,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 20,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 20,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 20,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 20,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 5,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 6,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 9:00 AM – 8:00 PM",
          "Tuesday: 9:00 AM – 8:00 PM",
          "Wednesday: 9:00 AM – 8:00 PM",
          "Thursday: 9:00 AM – 8:00 PM",
          "Friday: 9:00 AM – 9:00 PM",
          "Saturday: 9:00 AM – 9:00 PM",
          "Sunday: 9:00 AM – 8:00 PM"
        ]
      },
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "E 23 Olvera St, Los Angeles",
      "editorialSummary": {
        "text": "Since 1934 this humble stand's been serving taquitos, tamales & burritos on historic Olvera Street.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/reviews/ChZDSUhNMG9nS0VJQ0FnSURyMVpMZUF3EAE",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 5,
          "text": {
            "text": "OG spot with simple, fresh, delicious food. I had the #1 Combo, 3 Beef Taquitos which were great. There are a couple of spots to sit or take your food down the walkway to sit outside and enjoy the ambiance.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "OG spot with simple, fresh, delicious food. I had the #1 Combo, 3 Beef Taquitos which were great. There are a couple of spots to sit or take your food down the walkway to sit outside and enjoy the ambiance.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Matt Leonard",
            "uri": "https://www.google.com/maps/contrib/108791823693982137331/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU7UAGq8gnfvEXSY2ZAUsR8OP_CzIPY8vUd_6y3gF6y8MI-TIo0=s128-c0x00000000-cc-rp-mo-ba4"
          },
          "publishTime": "2024-07-18T23:12:35.202737Z"
        },
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/reviews/ChZDSUhNMG9nS0VJQ0FnSURMcXB5TkRREAE",
          "relativePublishTimeDescription": "3 months ago",
          "rating": 1,
          "text": {
            "text": "The workers very friendly but the tacos were very bland and the salsa was extremely watered down. We got the 2 taquitos with a chile relleno and an horchata, even the horchata had a funky taste 😣",
            "languageCode": "en"
          },
          "originalText": {
            "text": "The workers very friendly but the tacos were very bland and the salsa was extremely watered down. We got the 2 taquitos with a chile relleno and an horchata, even the horchata had a funky taste 😣",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Tania Campos",
            "uri": "https://www.google.com/maps/contrib/107257092265032109680/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjX91m8iaN6Kp8n94Qjt1an66_fnB2HBHrz9p1Cn8TAIZPzxBap_=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-06-26T21:14:22.184618Z"
        },
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/reviews/ChdDSUhNMG9nS0VJQ0FnSURIZ01pcjVBRRAB",
          "relativePublishTimeDescription": "a month ago",
          "rating": 4,
          "text": {
            "text": "Alvera Street! Best place to have some authentic Mexican food while you're in Los Angeles!! Been a long time since I was here! Missed it So Much!",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Alvera Street! Best place to have some authentic Mexican food while you're in Los Angeles!! Been a long time since I was here! Missed it So Much!",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Arthur Padilla",
            "uri": "https://www.google.com/maps/contrib/112215391309458702488/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXMEly87N5fk_uFo7WhCV7VHpbjh9R2HRuy_uE-5BlZyEdIM2fr=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-09-11T00:00:57.524150Z"
        },
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/reviews/ChdDSUhNMG9nS0VJQ0FnSURIMnFmTS1BRRAB",
          "relativePublishTimeDescription": "a month ago",
          "rating": 4,
          "text": {
            "text": "Food is decent , taquitos are decent. I got the chile verde burrito, it mostly had beans and cheese and very little pork.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Food is decent , taquitos are decent. I got the chile verde burrito, it mostly had beans and cheese and very little pork.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Dominick Bucio",
            "uri": "https://www.google.com/maps/contrib/100133122176434577941/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocL9VIO32aakmjWH40Gm35r1CymFcLHs7dsyNTTRFeSt2QngHA=s128-c0x00000000-cc-rp-mo-ba3"
          },
          "publishTime": "2024-09-15T00:58:32.783240Z"
        },
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/reviews/ChZDSUhNMG9nS0VJQ0FnSURIenRLWld3EAE",
          "relativePublishTimeDescription": "a month ago",
          "rating": 5,
          "text": {
            "text": "Stood in line for more than 45mins. Definitely worth it! I got 2, number ones (three taquitos with beans 🫘 and cheese 🧀) a bean and cheese burrito 🌯, 1 Pepsi and 1 agua de Jamaica. $43.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Stood in line for more than 45mins. Definitely worth it! I got 2, number ones (three taquitos with beans 🫘 and cheese 🧀) a bean and cheese burrito 🌯, 1 Pepsi and 1 agua de Jamaica. $43.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Veronica Hernandez",
            "uri": "https://www.google.com/maps/contrib/106290082241002287221/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjW9ryyg4DKE78HZ04xLG-QoBWKQTSy1B5sAdrvMSQ7td160aG2fiA=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-09-16T01:45:16.053408Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/photos/AdCG2DOqMZRecAGb6hdpWdC9o3pyZd3h9BuGoWHYCJwHvj3TOybd6sxrfICj1ez6sB5CYcXmoCoMGMXaBGBuMKusySETGnVMlYpAaJei4EajaubNRdtyZ9pufMZ4j2h-A_cN0vN5yS94JhpplOwJwSjEveFg4ap2WxUc9Bwm",
          "widthPx": 4000,
          "heightPx": 3000,
          "authorAttributions": [
            {
              "displayName": "Tokio",
              "uri": "https://maps.google.com/maps/contrib/101955601074550869053",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjV16b92gZfpd9bcANQsR52skzAisrTKN0vLWxzcHJFfmRP8AYQWJQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/photos/AdCG2DP73DxdGEB-U6swIFwsarHXMb_Ja-xsgvJp8-5lvo7bD8myr4NGnJkQ0kWC3bbOzBBbUQ3bgB5sWgckI87IYmt0epXFLo0ikeQFBn19jNPVmC7HghSuidL9szXwzHSQf3ALuaXSh6QZAkY_NIV-Anrai9uB4Yp_xeB6",
          "widthPx": 1318,
          "heightPx": 854,
          "authorAttributions": [
            {
              "displayName": "Cielito Lindo",
              "uri": "https://maps.google.com/maps/contrib/105842275112843604951",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocJK0WL_mgdx6oKTCAGhprR6vFDXlZ29Q7Ra5eQGHdLHaVBM4Q=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/photos/AdCG2DOiqfl6fBA37gQ4vJxDzxqhW4OWvLfKbbdtVhuDpledCzCaI8-6OIWJNTBY1fUCx3DavFThcp67LHPwzZd0aW_CAT28UawCrsCgzBJ-b-HLLZWeT_N1L64DHBJmps_y9cvZTHeuMjAy-_qVKV7Hx0ah4h38o7LCjlrf",
          "widthPx": 3840,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "Matt Leonard",
              "uri": "https://maps.google.com/maps/contrib/108791823693982137331",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU7UAGq8gnfvEXSY2ZAUsR8OP_CzIPY8vUd_6y3gF6y8MI-TIo0=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/photos/AdCG2DNr8yP3Fv3x2cZRoZ99P2iXPGr3y1fLWTMLb9oqAYr95ErLj0MXBSORxunfNR7CK52knf6ADWJXsZHWFvaryS90A9RtPdCGWLmYHvpYj0vvxkvgtOg6HqSeg6hrNJ6itSZ6z0s4KTUsHxwhF-kkJScD-N5vN-GXKsUL",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Mike Arredondo",
              "uri": "https://maps.google.com/maps/contrib/101728370482632205500",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocIzN3xPqK2ASLf-qqhhwRmwxOAYDpL5IbzRbNvydxvzWe9X7w=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/photos/AdCG2DNWINABNOB1vyd-HjnktdA35HwHkUjuBsNaPmhvImaF8jcM9ptBJ2TjF7HaA1EyN9ZRDTH41ypiODt4EgXOR2aOPFvFSDjTfVXCG--W3n8iPIWb3UAFN3ZNMihWnsocpjw9y63PB6-eFRqdgXWJljFX2ITWo3VF4zJP",
          "widthPx": 4800,
          "heightPx": 3600,
          "authorAttributions": [
            {
              "displayName": "Chief Victor",
              "uri": "https://maps.google.com/maps/contrib/115873747796932406567",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjURoAmlAwd2AJjByqkvPxMXczCicKgAmKQnxR_HHqF0ZdCUFzENKg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/photos/AdCG2DPeh-5agvXvGYruCG_WZCzT3m8DNVHkECNzuRiCq2Jstn53X1eKPgyh7vFZ4PtUlxD1aQx6wfyHDMuVgSuHgB8QiNIgKjMhDH6vmb3qyK-IIC5zY5PDjjN0s8mq812y42n-5HT12yjqps9CcuyE584n5aiCLNwJKCP4",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Dominick Bucio",
              "uri": "https://maps.google.com/maps/contrib/100133122176434577941",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocL9VIO32aakmjWH40Gm35r1CymFcLHs7dsyNTTRFeSt2QngHA=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/photos/AdCG2DMl0nrKfOpMofNc7XlCowVKcDEYnaIOxucsDDIg-v1BhvIhJfoK7NrEnpsB1l-3Sr8Mw5kxEARq0n3V5qI8Li1KNapTue7__oFsmVAzVBNc_YYy3ktqS-Dg_lcuUuwtWMWh7e1gGP2BHsHjG-MHCvcC1NoSxZWG-H40",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Arthur Padilla",
              "uri": "https://maps.google.com/maps/contrib/112215391309458702488",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXMEly87N5fk_uFo7WhCV7VHpbjh9R2HRuy_uE-5BlZyEdIM2fr=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/photos/AdCG2DMJJad_c2vssd8fdyoB5Lc7G8GtUNjEUnAMxvf5itnP91OCxW9EcktAErtpNH6CKLBHt9Gc11UnHFo51xDlKzOOLM-Omh_M0fz_hAkHARdt1un8hwNH7GqAHFyr1xYHQPD9QsDicnYb5cSZ2i7d27Y8g0tXAguRnMvK",
          "widthPx": 3024,
          "heightPx": 4032,
          "authorAttributions": [
            {
              "displayName": "Joe Masucci",
              "uri": "https://maps.google.com/maps/contrib/116710775623489310833",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXIjgfWDVojPSrQtl62DcRn1fqPr6t7RUqBhOrN28WLYogZRfqn=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/photos/AdCG2DPrfDgbp8egdcH5jYMYTd8UdRletDjOtzgge9eRJJmB7H38_0CsYnAInQGhzVTkFDxLZdwyH28rKsdzN4rNNdAcwPGe7BznCxun7WW5k1_ch18HbhaMhJZSkOWJTE1fogK10udC1GxuNye2TV827Fo3XaGnDf1TY_hq",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "sofia zarzuela",
              "uri": "https://maps.google.com/maps/contrib/105768999961052146959",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXNPGn8-JS4XfxFsy989xpyvbfwOffvWkalvo6yGnm-5Wynhtiy5w=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJ97N_50TGwoARAMKHgO5qa6E/photos/AdCG2DPjSEqu6KmsRA_amqoubEgAsVEggzizcibkABfoSgKALuvlyYgsvrlRWQPz4J2UZg86Fdzhs8I2X6xhzAHWEcRbbL8ZX2DKNHW5HMWzrM40jftUFrqM0gaoxY4rNDG6JHLzXkyw5v5UeXsEAmKN6L0GfirfRkPtUpsl",
          "widthPx": 3600,
          "heightPx": 4800,
          "authorAttributions": [
            {
              "displayName": "J H",
              "uri": "https://maps.google.com/maps/contrib/113791338986589199966",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXwcYYz4Ec77BYKcYgqvCRqfyJBGjIpmzKDrebh488FZ1W7Kb6PtA=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "liveMusic": False,
      "menuForChildren": False,
      "servesCocktails": False,
      "servesDessert": False,
      "servesCoffee": True,
      "goodForChildren": True,
      "restroom": False,
      "goodForGroups": True,
      "goodForWatchingSports": False,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False,
        "acceptsNfc": True
      },
      "parkingOptions": {
        "paidParkingLot": True,
        "paidStreetParking": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleParking": True,
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Busy, old-school eatery known for its beef taquitos and green avocado sauce.",
          "languageCode": "en-US"
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJJzekAUXGwoARhCSQfa2BSLY",
            "placeId": "ChIJJzekAUXGwoARhCSQfa2BSLY",
            "displayName": {
              "text": "Italian American Museum of Los Angeles IAMLA",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "museum",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 46.410027,
            "travelDistanceMeters": 78.1112
          },
          {
            "name": "places/ChIJ2YN22kTGwoARshYCMmIIuQM",
            "placeId": "ChIJ2YN22kTGwoARshYCMmIIuQM",
            "displayName": {
              "text": "Metro Plaza Hotel",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "lodging",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 96.05404,
            "travelDistanceMeters": 116.88078
          },
          {
            "name": "places/ChIJC228bEXGwoARO6m8cJcKpDI",
            "placeId": "ChIJC228bEXGwoARO6m8cJcKpDI",
            "displayName": {
              "text": "Our Lady Queen of Angels Catholic Church",
              "languageCode": "en"
            },
            "types": [
              "church",
              "establishment",
              "place_of_worship",
              "point_of_interest",
              "tourist_attraction"
            ],
            "straightLineDistanceMeters": 220.21461,
            "travelDistanceMeters": 238.44086
          },
          {
            "name": "places/ChIJz7SQuzfHwoAREE6nSE8ZMmo",
            "placeId": "ChIJz7SQuzfHwoAREE6nSE8ZMmo",
            "displayName": {
              "text": "Los Angeles Union Station",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 213.39563,
            "travelDistanceMeters": 274.54752
          },
          {
            "name": "places/ChIJp8Kl0onHwoAR7Y4PrIpIEUY",
            "placeId": "ChIJp8Kl0onHwoAR7Y4PrIpIEUY",
            "displayName": {
              "text": "Placita Olvera",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "food",
              "point_of_interest",
              "restaurant",
              "store"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 64.10213,
            "travelDistanceMeters": 62.81008
          }
        ],
        "areas": [
          {
            "name": "places/ChIJAf09JTTGwoARIKmlGd9S_iY",
            "placeId": "ChIJAf09JTTGwoARIKmlGd9S_iY",
            "displayName": {
              "text": "Downtown Los Angeles",
              "languageCode": "en"
            },
            "containment": "OUTSKIRTS"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJd1jR50TGwoARmTj1J6pIKR8",
            "placeId": "ChIJd1jR50TGwoARmTj1J6pIKR8",
            "displayName": {
              "text": "Parking lot",
              "languageCode": "en"
            },
            "containment": "OUTSKIRTS"
          }
        ]
      }
    },
    {
      "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320",
      "id": "ChIJVQBvxRHGwoAR3hWZdRv0320",
      "types": [
        "mexican_restaurant",
        "restaurant",
        "food",
        "point_of_interest",
        "establishment"
      ],
      "nationalPhoneNumber": "(323) 604-9592",
      "internationalPhoneNumber": "+1 323-604-9592",
      "formattedAddress": "1842 1st St, Los Angeles, CA 90033, USA",
      "addressComponents": [
        {
          "longText": "1842",
          "shortText": "1842",
          "types": [
            "street_number"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "1st Street",
          "shortText": "1st St",
          "types": [
            "route"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Central LA",
          "shortText": "Central LA",
          "types": [
            "neighborhood",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles",
          "shortText": "Los Angeles",
          "types": [
            "locality",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "Los Angeles County",
          "shortText": "Los Angeles County",
          "types": [
            "administrative_area_level_2",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "California",
          "shortText": "CA",
          "types": [
            "administrative_area_level_1",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "United States",
          "shortText": "US",
          "types": [
            "country",
            "political"
          ],
          "languageCode": "en"
        },
        {
          "longText": "90033",
          "shortText": "90033",
          "types": [
            "postal_code"
          ],
          "languageCode": "en-US"
        },
        {
          "longText": "3411",
          "shortText": "3411",
          "types": [
            "postal_code_suffix"
          ],
          "languageCode": "en-US"
        }
      ],
      "plusCode": {
        "globalCode": "85632QWJ+MJ",
        "compoundCode": "2QWJ+MJ Los Angeles, CA, USA"
      },
      "location": {
        "latitude": 34.046748799999996,
        "longitude": -118.21843039999999
      },
      "viewport": {
        "low": {
          "latitude": 34.0455127197085,
          "longitude": -118.21977698029148
        },
        "high": {
          "latitude": 34.0482106802915,
          "longitude": -118.21707901970851
        }
      },
      "rating": 4.4,
      "googleMapsUri": "https://maps.google.com/?cid=7917315068714882526",
      "websiteUri": "http://casafinarestaurant.com/",
      "regularOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 1,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 2,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 3,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 4,
              "hour": 21,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 6,
              "hour": 1,
              "minute": 0
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 9,
              "minute": 0
            },
            "close": {
              "day": 0,
              "hour": 1,
              "minute": 0
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 9:00 AM – 9:00 PM",
          "Tuesday: 9:00 AM – 9:00 PM",
          "Wednesday: 9:00 AM – 9:00 PM",
          "Thursday: 9:00 AM – 9:00 PM",
          "Friday: 9:00 AM – 1:00 AM",
          "Saturday: 9:00 AM – 1:00 AM",
          "Sunday: 9:00 AM – 9:00 PM"
        ]
      },
      "utcOffsetMinutes": -420,
      "adrFormatAddress": "\u003cspan class=\"street-address\"\u003e1842 1st St\u003c/span\u003e, \u003cspan class=\"locality\"\u003eLos Angeles\u003c/span\u003e, \u003cspan class=\"region\"\u003eCA\u003c/span\u003e \u003cspan class=\"postal-code\"\u003e90033-3411\u003c/span\u003e, \u003cspan class=\"country-name\"\u003eUSA\u003c/span\u003e",
      "businessStatus": "OPERATIONAL",
      "priceLevel": "PRICE_LEVEL_MODERATE",
      "userRatingCount": 1012,
      "iconMaskBaseUri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet",
      "iconBackgroundColor": "#FF9E67",
      "displayName": {
        "text": "Casa Fina Mexican Restaurant & Cantina",
        "languageCode": "en"
      },
      "primaryTypeDisplayName": {
        "text": "Mexican Restaurant",
        "languageCode": "en-US"
      },
      "takeout": True,
      "delivery": True,
      "dineIn": True,
      "reservable": True,
      "servesBreakfast": True,
      "servesLunch": True,
      "servesDinner": True,
      "servesBeer": True,
      "servesWine": True,
      "servesBrunch": True,
      "servesVegetarianFood": True,
      "currentOpeningHours": {
        "openNow": True,
        "periods": [
          {
            "open": {
              "day": 0,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            },
            "close": {
              "day": 0,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          },
          {
            "open": {
              "day": 1,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            },
            "close": {
              "day": 1,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 21
              }
            }
          },
          {
            "open": {
              "day": 2,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            },
            "close": {
              "day": 2,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 22
              }
            }
          },
          {
            "open": {
              "day": 3,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            },
            "close": {
              "day": 3,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 23
              }
            }
          },
          {
            "open": {
              "day": 4,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            },
            "close": {
              "day": 4,
              "hour": 21,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 17
              }
            }
          },
          {
            "open": {
              "day": 5,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 18
              }
            },
            "close": {
              "day": 6,
              "hour": 1,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            }
          },
          {
            "open": {
              "day": 6,
              "hour": 9,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 19
              }
            },
            "close": {
              "day": 0,
              "hour": 1,
              "minute": 0,
              "date": {
                "year": 2024,
                "month": 10,
                "day": 20
              }
            }
          }
        ],
        "weekdayDescriptions": [
          "Monday: 9:00 AM – 9:00 PM",
          "Tuesday: 9:00 AM – 9:00 PM",
          "Wednesday: 9:00 AM – 9:00 PM",
          "Thursday: 9:00 AM – 9:00 PM",
          "Friday: 9:00 AM – 1:00 AM",
          "Saturday: 9:00 AM – 1:00 AM",
          "Sunday: 9:00 AM – 9:00 PM"
        ]
      },
      "currentSecondaryOpeningHours": [
        {
          "openNow": True,
          "periods": [
            {
              "open": {
                "day": 1,
                "hour": 15,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 21
                }
              },
              "close": {
                "day": 1,
                "hour": 18,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 21
                }
              }
            },
            {
              "open": {
                "day": 2,
                "hour": 15,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 22
                }
              },
              "close": {
                "day": 2,
                "hour": 18,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 22
                }
              }
            },
            {
              "open": {
                "day": 3,
                "hour": 15,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 23
                }
              },
              "close": {
                "day": 3,
                "hour": 18,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 23
                }
              }
            },
            {
              "open": {
                "day": 4,
                "hour": 15,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 17
                }
              },
              "close": {
                "day": 4,
                "hour": 18,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 17
                }
              }
            },
            {
              "open": {
                "day": 5,
                "hour": 15,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 18
                }
              },
              "close": {
                "day": 5,
                "hour": 18,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 18
                }
              }
            }
          ],
          "weekdayDescriptions": [
            "Monday: 3:00 – 6:00 PM",
            "Tuesday: 3:00 – 6:00 PM",
            "Wednesday: 3:00 – 6:00 PM",
            "Thursday: 3:00 – 6:00 PM",
            "Friday: 3:00 – 6:00 PM",
            "Saturday: Closed",
            "Sunday: Closed"
          ],
          "secondaryHoursType": "HAPPY_HOUR"
        },
        {
          "openNow": True,
          "periods": [
            {
              "open": {
                "day": 0,
                "hour": 9,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 20
                }
              },
              "close": {
                "day": 0,
                "hour": 20,
                "minute": 30,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 20
                }
              }
            },
            {
              "open": {
                "day": 1,
                "hour": 9,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 21
                }
              },
              "close": {
                "day": 1,
                "hour": 20,
                "minute": 30,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 21
                }
              }
            },
            {
              "open": {
                "day": 2,
                "hour": 9,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 22
                }
              },
              "close": {
                "day": 2,
                "hour": 20,
                "minute": 30,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 22
                }
              }
            },
            {
              "open": {
                "day": 3,
                "hour": 9,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 23
                }
              },
              "close": {
                "day": 3,
                "hour": 20,
                "minute": 30,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 23
                }
              }
            },
            {
              "open": {
                "day": 4,
                "hour": 9,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 17
                }
              },
              "close": {
                "day": 4,
                "hour": 20,
                "minute": 30,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 17
                }
              }
            },
            {
              "open": {
                "day": 5,
                "hour": 8,
                "minute": 30,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 18
                }
              },
              "close": {
                "day": 5,
                "hour": 22,
                "minute": 30,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 18
                }
              }
            },
            {
              "open": {
                "day": 6,
                "hour": 8,
                "minute": 30,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 19
                }
              },
              "close": {
                "day": 6,
                "hour": 22,
                "minute": 30,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 19
                }
              }
            }
          ],
          "weekdayDescriptions": [
            "Monday: 9:00 AM – 8:30 PM",
            "Tuesday: 9:00 AM – 8:30 PM",
            "Wednesday: 9:00 AM – 8:30 PM",
            "Thursday: 9:00 AM – 8:30 PM",
            "Friday: 8:30 AM – 10:30 PM",
            "Saturday: 8:30 AM – 10:30 PM",
            "Sunday: 9:00 AM – 8:30 PM"
          ],
          "secondaryHoursType": "DELIVERY"
        },
        {
          "openNow": True,
          "periods": [
            {
              "open": {
                "day": 0,
                "hour": 9,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 20
                }
              },
              "close": {
                "day": 0,
                "hour": 21,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 20
                }
              }
            },
            {
              "open": {
                "day": 1,
                "hour": 9,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 21
                }
              },
              "close": {
                "day": 1,
                "hour": 21,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 21
                }
              }
            },
            {
              "open": {
                "day": 2,
                "hour": 9,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 22
                }
              },
              "close": {
                "day": 2,
                "hour": 21,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 22
                }
              }
            },
            {
              "open": {
                "day": 3,
                "hour": 9,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 23
                }
              },
              "close": {
                "day": 3,
                "hour": 21,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 23
                }
              }
            },
            {
              "open": {
                "day": 4,
                "hour": 9,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 17
                }
              },
              "close": {
                "day": 4,
                "hour": 21,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 17
                }
              }
            },
            {
              "open": {
                "day": 5,
                "hour": 9,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 18
                }
              },
              "close": {
                "day": 5,
                "hour": 23,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 18
                }
              }
            },
            {
              "open": {
                "day": 6,
                "hour": 9,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 19
                }
              },
              "close": {
                "day": 6,
                "hour": 23,
                "minute": 0,
                "date": {
                  "year": 2024,
                  "month": 10,
                  "day": 19
                }
              }
            }
          ],
          "weekdayDescriptions": [
            "Monday: 9:00 AM – 9:00 PM",
            "Tuesday: 9:00 AM – 9:00 PM",
            "Wednesday: 9:00 AM – 9:00 PM",
            "Thursday: 9:00 AM – 9:00 PM",
            "Friday: 9:00 AM – 11:00 PM",
            "Saturday: 9:00 AM – 11:00 PM",
            "Sunday: 9:00 AM – 9:00 PM"
          ],
          "secondaryHoursType": "ONLINE_SERVICE_HOURS"
        }
      ],
      "regularSecondaryOpeningHours": [
        {
          "openNow": True,
          "periods": [
            {
              "open": {
                "day": 1,
                "hour": 15,
                "minute": 0
              },
              "close": {
                "day": 1,
                "hour": 18,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 2,
                "hour": 15,
                "minute": 0
              },
              "close": {
                "day": 2,
                "hour": 18,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 3,
                "hour": 15,
                "minute": 0
              },
              "close": {
                "day": 3,
                "hour": 18,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 4,
                "hour": 15,
                "minute": 0
              },
              "close": {
                "day": 4,
                "hour": 18,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 5,
                "hour": 15,
                "minute": 0
              },
              "close": {
                "day": 5,
                "hour": 18,
                "minute": 0
              }
            }
          ],
          "weekdayDescriptions": [
            "Monday: 3:00 – 6:00 PM",
            "Tuesday: 3:00 – 6:00 PM",
            "Wednesday: 3:00 – 6:00 PM",
            "Thursday: 3:00 – 6:00 PM",
            "Friday: 3:00 – 6:00 PM",
            "Saturday: Closed",
            "Sunday: Closed"
          ],
          "secondaryHoursType": "HAPPY_HOUR"
        },
        {
          "openNow": True,
          "periods": [
            {
              "open": {
                "day": 0,
                "hour": 9,
                "minute": 0
              },
              "close": {
                "day": 0,
                "hour": 20,
                "minute": 30
              }
            },
            {
              "open": {
                "day": 1,
                "hour": 9,
                "minute": 0
              },
              "close": {
                "day": 1,
                "hour": 20,
                "minute": 30
              }
            },
            {
              "open": {
                "day": 2,
                "hour": 9,
                "minute": 0
              },
              "close": {
                "day": 2,
                "hour": 20,
                "minute": 30
              }
            },
            {
              "open": {
                "day": 3,
                "hour": 9,
                "minute": 0
              },
              "close": {
                "day": 3,
                "hour": 20,
                "minute": 30
              }
            },
            {
              "open": {
                "day": 4,
                "hour": 9,
                "minute": 0
              },
              "close": {
                "day": 4,
                "hour": 20,
                "minute": 30
              }
            },
            {
              "open": {
                "day": 5,
                "hour": 8,
                "minute": 30
              },
              "close": {
                "day": 5,
                "hour": 22,
                "minute": 30
              }
            },
            {
              "open": {
                "day": 6,
                "hour": 8,
                "minute": 30
              },
              "close": {
                "day": 6,
                "hour": 22,
                "minute": 30
              }
            }
          ],
          "weekdayDescriptions": [
            "Monday: 9:00 AM – 8:30 PM",
            "Tuesday: 9:00 AM – 8:30 PM",
            "Wednesday: 9:00 AM – 8:30 PM",
            "Thursday: 9:00 AM – 8:30 PM",
            "Friday: 8:30 AM – 10:30 PM",
            "Saturday: 8:30 AM – 10:30 PM",
            "Sunday: 9:00 AM – 8:30 PM"
          ],
          "secondaryHoursType": "DELIVERY"
        },
        {
          "openNow": True,
          "periods": [
            {
              "open": {
                "day": 0,
                "hour": 9,
                "minute": 0
              },
              "close": {
                "day": 0,
                "hour": 21,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 1,
                "hour": 9,
                "minute": 0
              },
              "close": {
                "day": 1,
                "hour": 21,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 2,
                "hour": 9,
                "minute": 0
              },
              "close": {
                "day": 2,
                "hour": 21,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 3,
                "hour": 9,
                "minute": 0
              },
              "close": {
                "day": 3,
                "hour": 21,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 4,
                "hour": 9,
                "minute": 0
              },
              "close": {
                "day": 4,
                "hour": 21,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 5,
                "hour": 9,
                "minute": 0
              },
              "close": {
                "day": 5,
                "hour": 23,
                "minute": 0
              }
            },
            {
              "open": {
                "day": 6,
                "hour": 9,
                "minute": 0
              },
              "close": {
                "day": 6,
                "hour": 23,
                "minute": 0
              }
            }
          ],
          "weekdayDescriptions": [
            "Monday: 9:00 AM – 9:00 PM",
            "Tuesday: 9:00 AM – 9:00 PM",
            "Wednesday: 9:00 AM – 9:00 PM",
            "Thursday: 9:00 AM – 9:00 PM",
            "Friday: 9:00 AM – 11:00 PM",
            "Saturday: 9:00 AM – 11:00 PM",
            "Sunday: 9:00 AM – 9:00 PM"
          ],
          "secondaryHoursType": "ONLINE_SERVICE_HOURS"
        }
      ],
      "primaryType": "mexican_restaurant",
      "shortFormattedAddress": "1842 1st St, Los Angeles",
      "editorialSummary": {
        "text": "Warm, bright eatery for classic Mexican cuisine such as homestyle fajitas, tacos & tequila drinks.",
        "languageCode": "en"
      },
      "reviews": [
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/reviews/ChdDSUhNMG9nS0VJQ0FnSUNkLUxEWGd3RRAB",
          "relativePublishTimeDescription": "8 months ago",
          "rating": 5,
          "text": {
            "text": "Wow it was delicious. But two things I don't like was that a person goes around asking if you want your picture taken for a small few. (Come on everyone has a cell phone I'll take my own pictures) The 2nd thing was parking.$5 Buck if you want to park your car in the back (very small) parking lot that's in the same building.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Wow it was delicious. But two things I don't like was that a person goes around asking if you want your picture taken for a small few. (Come on everyone has a cell phone I'll take my own pictures) The 2nd thing was parking.$5 Buck if you want to park your car in the back (very small) parking lot that's in the same building.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Darlene “Dee” Villareal",
            "uri": "https://www.google.com/maps/contrib/104855706036075806103/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXPu0TcOAZOsvD-JPsVXXM6U0MBBohT85zEoB27zPm4wduUd4A53Q=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-02-11T15:05:36.758853Z"
        },
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/reviews/ChZDSUhNMG9nS0VJQ0FnSUNYblAtYU1REAE",
          "relativePublishTimeDescription": "in the last week",
          "rating": 5,
          "text": {
            "text": "The food is delicious, and the portions are more than expected. The service is good but lacks on busy days. Good drinks, they pour cocktails as if Stevie Wonder was the bartender.  Tvs to watch but only in bar area.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "The food is delicious, and the portions are more than expected. The service is good but lacks on busy days. Good drinks, they pour cocktails as if Stevie Wonder was the bartender.  Tvs to watch but only in bar area.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Jonathan Rivers",
            "uri": "https://www.google.com/maps/contrib/106094991316336423286/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWpMsoGVEndSZxZIIKCLvYPGiJuQCpv93N13PYeFimlzJsY_Q=s128-c0x00000000-cc-rp-mo-ba2"
          },
          "publishTime": "2024-10-14T05:45:06.012983Z"
        },
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/reviews/ChZDSUhNMG9nS0VJQ0FnSUNqajdiV0RREAE",
          "relativePublishTimeDescription": "5 months ago",
          "rating": 5,
          "text": {
            "text": "I can't believe i didn't know this place before. Everything is excelent, food was really good, but the mango margarita casa fina was the best of all.",
            "languageCode": "en"
          },
          "originalText": {
            "text": "I can't believe i didn't know this place before. Everything is excelent, food was really good, but the mango margarita casa fina was the best of all.",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Julio A",
            "uri": "https://www.google.com/maps/contrib/112911792723175581703/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLTXvVhtljaUG1tLLrwjVmx2HK2-gmf7VZm9vDkSGt5v_IccA=s128-c0x00000000-cc-rp-mo"
          },
          "publishTime": "2024-04-27T04:54:45.377252Z"
        },
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/reviews/ChZDSUhNMG9nS0VJQ0FnSURkeVpQblpnEAE",
          "relativePublishTimeDescription": "7 months ago",
          "rating": 5,
          "text": {
            "text": "Hidden Gem in Boyle Heights. Restaurant has beautiful decor and the Food is very delicious. The waiters provide excellent service. Definitely will return again!\nD-LO recommended 😃👍",
            "languageCode": "en"
          },
          "originalText": {
            "text": "Hidden Gem in Boyle Heights. Restaurant has beautiful decor and the Food is very delicious. The waiters provide excellent service. Definitely will return again!\nD-LO recommended 😃👍",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "D-LO",
            "uri": "https://www.google.com/maps/contrib/107052720896896669379/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVsice1tvnmKvfUNkyQW90ezhJiqpBZ2_bLPcXXZug6SeYFi-WN=s128-c0x00000000-cc-rp-mo-ba5"
          },
          "publishTime": "2024-02-24T20:45:33.196650Z"
        },
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/reviews/ChdDSUhNMG9nS0VJQ0FnSURBanFqTjV3RRAB",
          "relativePublishTimeDescription": "a week ago",
          "rating": 5,
          "text": {
            "text": "The Chili Verde pork omelet is delicious. I totally recommend this place. Always good Vibes here.\nUpdate 10/04/24- the chili Verde chilaquiles are delicious!!",
            "languageCode": "en"
          },
          "originalText": {
            "text": "The Chili Verde pork omelet is delicious. I totally recommend this place. Always good Vibes here.\nUpdate 10/04/24- the chili Verde chilaquiles are delicious!!",
            "languageCode": "en"
          },
          "authorAttribution": {
            "displayName": "Frank MacGyver",
            "uri": "https://www.google.com/maps/contrib/111296200905363285420/reviews",
            "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWs1nQXb8SqB-55zzOFj-2btDftAXwQtItOJgUPcjLcWOe8dA3v=s128-c0x00000000-cc-rp-mo-ba6"
          },
          "publishTime": "2024-10-04T21:51:52.984547Z"
        }
      ],
      "photos": [
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/photos/AdCG2DPp-h8mFi2tfswJ4rBEKHRDeEJ1j3sUyX33PLh6DN5Dob_usuMzmskUfIdfeb83j1XlTzkAitfaUOGGxb2zbYH-dkIiMQB0sUXPWDWYJEVSBEFo4ryl8pMIloJ65Zc1nblgS1nnxK8k6tlHeoE9D8oUoG0mDkk3owx1",
          "widthPx": 3000,
          "heightPx": 3822,
          "authorAttributions": [
            {
              "displayName": "Elizabeth Stenbakken",
              "uri": "https://maps.google.com/maps/contrib/102308371098652370882",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXeOF2OHp4tYmkyMIPfBWRrKyCTkBeLdGxdw4zyX5tpqRZ0dpQH=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/photos/AdCG2DPuHuJZepuBMfX3IbfTtUm26leoCxCcLH___LwoS5ZxkayznuRF0g3wP8GMbsuLFBX2p50Dx_TFBWvkFBcDpsEorNdhVHjqDRyccv6EUC68NpzcJl1JcBqbwv3JAKlaAmKlXpuOo729B_5ZvKXlWxcQLfqhtV1z_89u",
          "widthPx": 4032,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "Casa Fina Mexican Restaurant & Cantina",
              "uri": "https://maps.google.com/maps/contrib/105740623021665700325",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocJ4d90lXDslqcLUO1gy9_WChzrSIgFZT8V561xL3WJcsTwYiw=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/photos/AdCG2DOEuM1gg7ihKxv5WhLLticpwonsMChhmhTLnZ_rXyw8dtVJHDYOG0GzA9K04lT-mI-jyJoJRoUXS_8lsy8tq09dALPnLoskjMhlMnFafxBzBLoizXaBLjwOLt0wfoAOWGFw_Q5Ie0ziWLsABp77gtuN6aqExdrTTQBQ",
          "widthPx": 3456,
          "heightPx": 4608,
          "authorAttributions": [
            {
              "displayName": "Dan Paez",
              "uri": "https://maps.google.com/maps/contrib/107105285674431761429",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocLZkpRNiKqJXQbx2mdR-jkuy1P2U9Ixo8h9mbeXrAo_y6ASGQ=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/photos/AdCG2DOYLFzP5lFGlwlMvn7OTDHOKYYr4k13iSp60f2v9dHz3cBgW7_i11V5muVe1d2V7OESBEDXDGdmYqTKPT0tPDYppsvaablFmihpCxh0pCMxde0dkLVyKr-iio25Bp-9Y7MD24ZFYm5RotlkU76azPLwAwEk7nOQLZRS",
          "widthPx": 3872,
          "heightPx": 2581,
          "authorAttributions": [
            {
              "displayName": "Angel Hernandez (Angel)",
              "uri": "https://maps.google.com/maps/contrib/105918150856460494106",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXQ35lCJIMMK18njJnve0YnroV9wz4-JticGHNU_xQ5gg8Jt8Bieg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/photos/AdCG2DMbekpMOdBRXTeGIRu6MbPKoHHpNHD0fj45cUivnWz_hr2KeumP7TkT9z2ywNcBjGTA_YQ3wZNNS3JhlY88J_iPlHlFnONW-egr3fFefUKiT5N0gDL-zGkvmN-NvXZeHjkapwxedHseKC7s1GnOV2sd2EOLNNRPlsnB",
          "widthPx": 4032,
          "heightPx": 2268,
          "authorAttributions": [
            {
              "displayName": "Larry Jack",
              "uri": "https://maps.google.com/maps/contrib/109356542433508082406",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjVFxcWcUkaYQBpwRZQFBeDmL4MFHLvW27eO2fKYoljoZCkoD08CZg=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/photos/AdCG2DNV3-e5s2Ef3HLmtPLbTlpNXBeiiydwwvoXGCoCcHhjvrazpr9Kystjl7946Ld5WOqscLSNGspGZkKIbgEjNsg54S-SeFNTo1hZRCeq7LY_eQHvDM5dOOBjfXGm0V-tNVzJLbdMD0hPgWKUX3ztPLl5D0ecmIC9cRDd",
          "widthPx": 4000,
          "heightPx": 3000,
          "authorAttributions": [
            {
              "displayName": "Elizabeth Stenbakken",
              "uri": "https://maps.google.com/maps/contrib/102308371098652370882",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXeOF2OHp4tYmkyMIPfBWRrKyCTkBeLdGxdw4zyX5tpqRZ0dpQH=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/photos/AdCG2DODNo0nhCY-Q3LT1VNYCKSe2WeUXLiW22Xw9co_SWKOPPRm4bsA9qjTn4e-F4KUQAsvOa0CyBp2H4SQae3ZnTLDsN8uMb3SeY5SvBoepYWSWSIGHJcQdxgDJyDyWcHFJWlvN9_VKEYnZlac-MXapSyTta_wASjwE93j",
          "widthPx": 4000,
          "heightPx": 2252,
          "authorAttributions": [
            {
              "displayName": "Jimmy Gloria",
              "uri": "https://maps.google.com/maps/contrib/105063233059863154036",
              "photoUri": "https://lh3.googleusercontent.com/a/ACg8ocI3emTLfWVlZOT9o2-jwKPwbwchRSp3CYPESHc1xICnKsTI5a8=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/photos/AdCG2DM2aGu07zwaXZOXbWOJUS3zs8r1TgqDXAxSwEftevBuByu2uCRk2JgYnzy8v-RfBpMx-ZlA6-Nd5gZf88jFJ-P0WjufwZuVDJ-ms2X6nbuDqVKXyVVuCfkQ307aEpPsI9GdlcD6wNTmsACFf5CJ1Q2BpPsNCkIK0Ilw",
          "widthPx": 4032,
          "heightPx": 2268,
          "authorAttributions": [
            {
              "displayName": "Darlene “Dee” Villareal",
              "uri": "https://maps.google.com/maps/contrib/104855706036075806103",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjXPu0TcOAZOsvD-JPsVXXM6U0MBBohT85zEoB27zPm4wduUd4A53Q=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/photos/AdCG2DPZdyM9CYByMKg5574xgG1OsVazCRqG3Cv_1LilG_2pxc2_6cDqZCsc0hrK9hMC6Ib8bOEp04hHKX1zie3lrjStoDH7ewHzGQaULCA59sTWGgB8mZkpkJJQcYOl8SaQW_1BdqDope4rZd8jpy1T_38fyW0-mRugc91p",
          "widthPx": 3024,
          "heightPx": 3024,
          "authorAttributions": [
            {
              "displayName": "LGaby Burgos",
              "uri": "https://maps.google.com/maps/contrib/108589321220174546949",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjWdcPMYwew01o0tOyC7bx8kDc0SXgsFh_7WlwB83_ICUfTEb4hB=s100-p-k-no-mo"
            }
          ]
        },
        {
          "name": "places/ChIJVQBvxRHGwoAR3hWZdRv0320/photos/AdCG2DOOCGo7iE55sDXUohNb6UHS7f1UlV4qzEuPhvNJg5-LISLvzQ64ZBi7jEMThBdf7T_7NOSnpAR3WUyNkPH47-Gg_4UjHI35-1-iSU4NRASPaUh8Ls3Hrp8JNRksgID1XukynWmGRRFS4dUgbi3_5XDpDYUstASeE5Ug",
          "widthPx": 3120,
          "heightPx": 4160,
          "authorAttributions": [
            {
              "displayName": "Cynthia Rocha",
              "uri": "https://maps.google.com/maps/contrib/103685707927599315839",
              "photoUri": "https://lh3.googleusercontent.com/a-/ALV-UjU0EVwVThUc4mJoFmC5-Mf4sVgUabG2sHxRob02wdnu_i_FgFv6xg=s100-p-k-no-mo"
            }
          ]
        }
      ],
      "outdoorSeating": True,
      "liveMusic": False,
      "menuForChildren": True,
      "servesCocktails": True,
      "servesDessert": True,
      "servesCoffee": True,
      "goodForChildren": True,
      "allowsDogs": False,
      "restroom": True,
      "goodForGroups": True,
      "paymentOptions": {
        "acceptsCreditCards": True,
        "acceptsDebitCards": True,
        "acceptsCashOnly": False
      },
      "parkingOptions": {
        "freeParkingLot": True,
        "freeStreetParking": True,
        "valetParking": True
      },
      "accessibilityOptions": {
        "wheelchairAccessibleParking": True,
        "wheelchairAccessibleEntrance": True,
        "wheelchairAccessibleRestroom": True,
        "wheelchairAccessibleSeating": True
      },
      "generativeSummary": {
        "overview": {
          "text": "Tacos, burritos and other Mexican staples are served in a festive setting with full bar and Wi-Fi.",
          "languageCode": "en-US"
        }
      },
      "addressDescriptor": {
        "landmarks": [
          {
            "name": "places/ChIJx8N_lBHGwoARUakiXk3MBQY",
            "placeId": "ChIJx8N_lBHGwoARUakiXk3MBQY",
            "displayName": {
              "text": "Mariachi Plaza",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 117.427124,
            "travelDistanceMeters": 114.25477
          },
          {
            "name": "places/ChIJw9Gw2xHGwoARbgYiW7WTk1E",
            "placeId": "ChIJw9Gw2xHGwoARbgYiW7WTk1E",
            "displayName": {
              "text": "Birrieria Don Boni",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "food",
              "point_of_interest",
              "restaurant"
            ],
            "spatialRelationship": "ACROSS_THE_ROAD",
            "straightLineDistanceMeters": 38.371506,
            "travelDistanceMeters": 24.214104
          },
          {
            "name": "places/ChIJoVj5-w3GwoAR9FVNMYFu9AE",
            "placeId": "ChIJoVj5-w3GwoAR9FVNMYFu9AE",
            "displayName": {
              "text": "Adventist Health White Memorial",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "health",
              "hospital",
              "point_of_interest"
            ],
            "straightLineDistanceMeters": 272.94437,
            "travelDistanceMeters": 502.20157
          },
          {
            "name": "places/ChIJ35mNvxHGwoARIy0EKlP1RDU",
            "placeId": "ChIJ35mNvxHGwoARIy0EKlP1RDU",
            "displayName": {
              "text": "House of Trophies and Awards, Inc.",
              "languageCode": "en"
            },
            "types": [
              "establishment",
              "point_of_interest",
              "store"
            ],
            "spatialRelationship": "DOWN_THE_ROAD",
            "straightLineDistanceMeters": 54.91346,
            "travelDistanceMeters": 66.024536
          },
          {
            "name": "places/ChIJXTHLwhHGwoARUzxqOi6DM_E",
            "placeId": "ChIJXTHLwhHGwoARUzxqOi6DM_E",
            "displayName": {
              "text": "Eastside Luv Wine Bar",
              "languageCode": "en"
            },
            "types": [
              "bar",
              "establishment",
              "point_of_interest"
            ],
            "spatialRelationship": "AROUND_THE_CORNER",
            "straightLineDistanceMeters": 30.190071,
            "travelDistanceMeters": 41.96482
          }
        ],
        "areas": [
          {
            "name": "places/ChIJ6VmanALGwoARlDo5dgynnuw",
            "placeId": "ChIJ6VmanALGwoARlDo5dgynnuw",
            "displayName": {
              "text": "Boyle Heights",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJz-A_k1nHwoARloiyHDKVAm8",
            "placeId": "ChIJz-A_k1nHwoARloiyHDKVAm8",
            "displayName": {
              "text": "Central LA",
              "languageCode": "en"
            },
            "containment": "WITHIN"
          },
          {
            "name": "places/ChIJve4ykRHGwoARAWFHw0I3oqM",
            "placeId": "ChIJve4ykRHGwoARAWFHw0I3oqM",
            "displayName": {
              "text": "Mariachi Plaza",
              "languageCode": "en"
            },
            "containment": "NEAR"
          }
        ]
      }
    }
  ]
}

