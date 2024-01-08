from random import randint
from flask import Flask, request
from aiohttp import ClientSession
import logging

from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.trace import get_tracer_provider, set_tracer_provider

def eave_instrument(app):
    set_tracer_provider(TracerProvider())
    get_tracer_provider().add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )
    FlaskInstrumentor.instrument_app(app)
    AioHttpClientInstrumentor().instrument()

app = Flask(__name__)
eave_instrument(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/rolldice")
async def roll_dice():
    player = request.args.get('player', default = None, type = str)
    result = str(roll())
    garbo = "unset"
    async with ClientSession() as session:
        async with session.get("https://www.google.com") as resp:
            garbo = (await resp.text())[:10]
    logger.info(f"garbo is: {garbo}")
    
    if player:
        logger.warning("%s is rolling the dice: %s", player, result)
    else:
        logger.warning("Anonymous player is rolling the dice: %s", result)
    return result

def roll():
    return randint(1, 6)


# if __name__ == "__main__":
#     app.run(port=8080)