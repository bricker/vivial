from google.maps.places import PlacesAsyncClient
from google.maps.routing import RoutesAsyncClient
import googlemaps

from eave.core.config import CORE_API_APP_CONFIG
from eave.stdlib.analytics import AnalyticsTracker
from eave.stdlib.eventbrite.client import EventbriteClient

"""
We initialize these once and share them
because initialization of the clients can be slow.
In particular, the Google API clients take around 0.3 seconds to initialize.
"""

GOOGLE_MAPS_PLACES_API_CLIENT = PlacesAsyncClient()
"""
Google Places API Client.
"""

GOOGLE_MAPS_ROUTING_API_CLIENT = RoutesAsyncClient()

GOOGLE_MAPS_API_CLIENT = googlemaps.Client(key=CORE_API_APP_CONFIG.google_maps_api_key)

EVENTBRITE_API_CLIENT = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)

ANALYTICS = AnalyticsTracker(write_key=CORE_API_APP_CONFIG.segment_write_key)
