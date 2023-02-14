import asyncio

import eave.app
import eave.slack_app

asyncio.run(eave.slack_app.start_socket_mode())
