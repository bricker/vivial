import googlemaps

from eave.core.config import CORE_API_APP_CONFIG

GOOGLE_MAPS_API_CLIENT = googlemaps.Client(key=CORE_API_APP_CONFIG.google_maps_api_key)
