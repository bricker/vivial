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
    result = str(randint(1, 6))
    
    garbo = "unset"
    async with ClientSession() as session:
        async with session.get("https://www.google.com") as resp:
            garbo = (await resp.text())[:10]
    logger.info(f"garbo is: {garbo}")

    async with ClientSession() as session:
        async with session.post("http://localhost:8080/makedice", data={"player": player}) as resp:
            garbo = await resp.text()
    
    if player:
        logger.warning("%s is rolling the dice: %s", player, result)
    else:
        logger.warning("Anonymous player is rolling the dice: %s", result)
    return result

@app.post("/makedice")
async def make_dice():
    return "you made dice, good job"

# if __name__ == "__main__":
#     app.run(port=8080)