from .util import wrap
from .async_wrapper import async_wrapper

def _aiohttp_request_wrapper_factory(wrapped, **kwargs):
    # TODO: actualy make this track the newtork requests and responses (or maybe this can only do one of those???)
    async def _coroutine(*args, **kwargs):
        sess, method, url = args[0], args[1], args[2] # TODO: dont want to rely on positional args
        # print(args)
        # print(kwargs)
        req_data = kwargs.get("data", None)
        # print(sess.headers)

        # TODO: replace w/ real dataclass to send to db
        trace = dict(
            module="aiohttp", 
            url=str(url),
            http_method=method
        )
        print(f"intercpeted req {trace}:\nheaders: {sess.headers}\ndata: {req_data}\n")

        try:
            response = await wrapped(*args, **kwargs)

            try:
                # trace.process_response_headers(response.headers.items())
                b = await response.text()
                print(f"intercepted resp {trace}:\nbody: {b[:50]}")
            except:
                pass

            return response
        except Exception as e:
            try:
                print(f"intercepted {trace}:\nerr: {e}")
                # trace.process_response_headers(e.headers.items())  # pylint: disable=E1101
            except:
                pass

            raise

    return async_wrapper(wrapped)(_coroutine)

# not sure if this needs the flexibility of passed module name
def aiohttp_client_wrapper(module):
    wrap(module, "ClientSession._request", _aiohttp_request_wrapper_factory)