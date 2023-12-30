# TODO: python aiohttp, or gunicorn trace agent or something. monkey patch some code in there

# TODO: how to determine which framework etc to wrap? just try/catch until it works?
from .util import wrap
from eave.stdlib.nettracing.framework_aiohttp import instrument_aiohttp_client

def trace_network() -> None:
    """public entrypoint"""
    _replace_import("aiohttp.client", instrument_aiohttp_client) # "eave.stdlib.nettracing.framework_aiohttp", "instrument_aiohttp_client")


def _replace_import(module_name, wrapper_factory):
    try:
        # Import the module dynamically
        imported_module = __import__(module_name, fromlist=[''])

        # Wrap the imported module in the provided wrapper function
        wrapper_factory(imported_module)

    except ImportError as e:
        print(f"Error importing module '{module_name}': {e}")
    