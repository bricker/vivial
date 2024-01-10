# a dummy app for testing network tracing with

from random import randint
from flask import Flask, request
from aiohttp import ClientSession
import logging

from eave.stdlib.nettracing.telem.instrumentors import eave_instrument

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