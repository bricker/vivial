class AddCookiesMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            async def wrapped_send(message):
                if message['type'] == 'http.response.start':
                    # Add cookies to the response
                    headers = [
                        (b"Set-Cookie", b"cookie_name=cookie_value; SameSite=None; Secure"),
                    ]
                    message['headers'] += headers
                await send(message)

            await self.app(scope, receive, wrapped_send)
        else:
            await self.app(scope, receive, send)

# Your Starlette app
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware

async def homepage(request):
    return PlainTextResponse("Hello, world!")

async def event(request):
    print("goet an event")
    return PlainTextResponse("event receivetd")

# Create your Starlette app
app = Starlette(routes=[
    Route("/", homepage, methods=["GET", "POST"]),
    Route("/event", event, methods=["GET", "POST"]),
])

# Wrap your app with the custom middleware
app.add_middleware(AddCookiesMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_methods=["*"],  # Allow any HTTP methods
    allow_headers=["*"],  # Allow any headers
)
