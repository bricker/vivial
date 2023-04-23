from .. import eave_origins
_ORIGIN: eave_origins.EaveOrigin

def set_origin(origin: eave_origins.EaveOrigin) -> None:
    global _ORIGIN
    _ORIGIN = origin
