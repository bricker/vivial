# TODO: python aiohttp, or gunicorn trace agent or something. monkey patch some code in there

from eave.stdlib.nettracing.framework_aiohttp import aiohttp_client_wrapper

# TODO: how to determine which framework etc to wrap? just try/catch until it works?
def trace_network() -> None:
    """public entrypoint"""
    _replace_import("aiohttp.client", aiohttp_client_wrapper) # "eave.stdlib.nettracing.framework_aiohttp", "instrument_aiohttp_client")


def _replace_import(module_name, wrapper_factory):
    try:
        # Import the module dynamically
        imported_module = __import__(module_name, fromlist=[''])

        # Wrap the imported module in the provided wrapper function
        wrapper_factory(imported_module)

    except ImportError as e:
        print(f"Error importing module '{module_name}': {e}")
    