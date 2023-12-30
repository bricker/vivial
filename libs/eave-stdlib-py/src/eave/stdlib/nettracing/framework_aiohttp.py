from .util import wrap
from .async_wrapper import async_wrapper

def _aiohttp_request_wrapper_(wrapped, *args, **kwargs):
    # transaction = current_transaction()


    method, url = args[0], args[1] # need this to be so shitty?
    # TODO: replace w/ real dataclass
    trace = dict(
        module="aiohttp", 
        url=str(url),
        http_method=method
    )

    # TODO: actualy make this track the newtork requests and responses (or maybe this can only do one of those???)
    async def _coroutine():
        try:
            response = await wrapped(*args, **kwargs)

            try:
                trace.process_response_headers(response.headers.items())
            except:
                pass

            return response
        except Exception as e:
            try:
                trace.process_response_headers(e.headers.items())  # pylint: disable=E1101
            except:
                pass

            raise

    return async_wrapper(wrapped)(_coroutine, trace)() # TODO: figure out why we are passing trace. necessary?

# not sure if this needs the flexibility of passed module name
def instrument_aiohttp_client(module):
    wrap(module, "ClientSession._request", _aiohttp_request_wrapper_)