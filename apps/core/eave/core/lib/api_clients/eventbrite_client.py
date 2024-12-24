from eave.core.config import CORE_API_APP_CONFIG
from eave.stdlib.eventbrite.client import EventbriteClient

EVENTBRITE_API_CLIENT = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)
