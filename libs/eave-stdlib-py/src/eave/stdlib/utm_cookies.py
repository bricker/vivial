import re
import uuid
from dataclasses import dataclass
from enum import StrEnum

from eave.stdlib.cookies import EAVE_COOKIE_PREFIX_UTM, EAVE_VISITOR_ID_COOKIE_NAME, set_http_cookie

from .typing import (
    HTTPFrameworkRequest,
    HTTPFrameworkResponse,
    JsonObject,
)


class TrackingParam(StrEnum):
    gclid = "gclid"
    msclkid = "msclkid"
    fbclid = "fbclid"
    twclid = "twclid"
    li_fat_id = "li_fat_id"
    rdt_cid = "rdt_cid"
    ttclid = "ttclid"
    keyword = "keyword"
    matchtype = "matchtype"
    campaign = "campaign"
    campaign_id = "campaign_id"
    pid = "pid"
    cid = "cid"


@dataclass
class TrackingCookies:
    utm_params: JsonObject
    visitor_id: str | None


def set_tracking_cookies(
    request: HTTPFrameworkRequest,
    response: HTTPFrameworkResponse,
) -> None:
    """
    GTM gtag.js needs to be able to read these cookies in the browser,
    so we must set httponly to False when setting analytics cookies.
    """
    query_params = request.query_params
    request_cookies = request.cookies

    if (cookie_value := request_cookies.get(EAVE_VISITOR_ID_COOKIE_NAME)) is None or len(cookie_value) == 0:
        set_http_cookie(response=response, key=EAVE_VISITOR_ID_COOKIE_NAME, value=str(uuid.uuid4()), httponly=False)

    for key, value in query_params.items():
        lkey = key.lower()
        if lkey in TrackingParam or re.match("^utm_", lkey):
            set_http_cookie(response=response, key=f"{EAVE_COOKIE_PREFIX_UTM}{lkey}", value=value, httponly=False)


def get_tracking_cookies(request: HTTPFrameworkRequest) -> TrackingCookies:
    request_cookies = request.cookies
    visitor_id = request_cookies.get(EAVE_VISITOR_ID_COOKIE_NAME)
    utm_params: JsonObject = {}

    for key, value in request_cookies.items():
        if re.match(f"^{EAVE_COOKIE_PREFIX_UTM}", key):
            utm_param_name = re.sub(f"^{EAVE_COOKIE_PREFIX_UTM}", "", key)
            utm_params[utm_param_name] = value

    return TrackingCookies(
        utm_params=utm_params,
        visitor_id=visitor_id,
    )
