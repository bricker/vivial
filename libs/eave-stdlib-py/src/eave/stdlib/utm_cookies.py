from dataclasses import dataclass
import re
from typing import Mapping, Optional
import uuid


from eave.stdlib.cookies import set_http_cookie
from .typing import HTTPFrameworkResponse, JsonObject

_KNOWN_TRACKING_PARAMS = set(
    [
        "gclid",
        "msclkid",
        "fbclid",
        "twclid",
        "li_fat_id",
        "rdt_cid",
        "ttclid",
        "keyword",
        "matchtype",
        "campaign",
        "campaign_id",
        "pid",
        "cid",
    ]
)

# DON'T RENAME THESE, they are referenced in GTM by name. Changing them will break tracking.
EAVE_COOKIE_PREFIX_UTM = "ev_utm_"
EAVE_VISITOR_ID_COOKIE = "ev_visitor_id"


@dataclass
class TrackingCookies:
    utm_params: JsonObject
    visitor_id: Optional[str]


def set_tracking_cookies(
    request_cookies: Mapping[str, str], query_params: Mapping[str, str], response: HTTPFrameworkResponse
) -> None:
    """
    GTM gtag.js needs to be able to read these cookies in the browser,
    so we must set httponly to False when setting analytics cookies.
    """
    if (cookie_value := request_cookies.get(EAVE_VISITOR_ID_COOKIE)) is None or len(cookie_value) == 0:
        set_http_cookie(response=response, key=EAVE_VISITOR_ID_COOKIE, value=str(uuid.uuid4()), httponly=False)

    for key, value in query_params.items():
        lkey = key.lower()
        if lkey in _KNOWN_TRACKING_PARAMS or re.match("^utm_", lkey):
            set_http_cookie(response=response, key=f"{EAVE_COOKIE_PREFIX_UTM}{lkey}", value=value, httponly=False)


def get_tracking_cookies(request_cookies: Mapping[str, str]) -> TrackingCookies:
    visitor_id = request_cookies.get(EAVE_VISITOR_ID_COOKIE)
    utm_params: JsonObject = {}

    for key, value in request_cookies.items():
        if re.match(f"^{EAVE_COOKIE_PREFIX_UTM}", key):
            utm_param_name = re.sub(f"^{EAVE_COOKIE_PREFIX_UTM}", "", key)
            utm_params[utm_param_name] = value

    return TrackingCookies(
        utm_params=utm_params,
        visitor_id=visitor_id,
    )
