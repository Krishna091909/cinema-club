# This file is a part of TG-FileStreamBot

import sys
import asyncio
import traceback
import logging
import logging.handlers as handlers

from aiohttp import web
from WebStreamer.bot import StreamBot, BotInfo
from WebStreamer.server import web_server
from WebStreamer.utils.keepalive import ping_server
from WebStreamer.utils.util import load_plugins, startup
from WebStreamer.bot.clients import initialize_clients
from .vars import Var

# Setup Logging (Only WARNING and ERROR will be shown)
logging.basicConfig(
    level=logging.WARNING,  # Hides INFO and DEBUG logs
    datefmt="%d/%m/%Y %H:%M:%S",
    format="[%(asctime)s][%(name)s][%(levelname)s] ==> %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
        handlers.RotatingFileHandler("streambot.log", mode="a", maxBytes=104857600, backupCount=2, encoding="utf-8")
    ],
)

# Suppress logs from other libraries
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)
logging.getLogger("telethon").setLevel(logging.ERROR)

server = web.AppRunner(web_server())
loop = asyncio.get_event_loop()

async def start_services():
    try:
        await StreamBot.start(bot_token=Var.BOT_TOKEN)
        await startup(StreamBot)

        peer = await StreamBot.get_entity(Var.BIN_CHANNEL)
        bot_info = await StreamBot.get_me()
        BotInfo.username = bot_info.username
        BotInfo.fname = bot_info.first_name

        await initialize_clients()

        if peer.megagroup:
            if Var.MULTI_CLIENT:
                logging.error("Bin Channel is a group. It must be a channel; multi-client won't work with groups.")
                return
            else:
                logging.warning("Bin Channel is a group. Use a channel for multi-client support.")

        if not Var.NO_UPDATE:
            load_plugins("WebStreamer/bot/plugins")

        if Var.KEEP_ALIVE:
            asyncio.create_task(ping_server())

        await server.setup()
        await web.TCPSite(server, Var.BIND_ADDRESS, Var.PORT).start()

        await StreamBot.run_until_disconnected()

    except ValueError:
        logging.error("Bin Channel not found. Please ensure the bot has been added to the bin channel.")

async def cleanup():
    await server.cleanup()
    await StreamBot.disconnect()

if __name__ == "__main__":
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        pass
    except Exception as err:
        logging.error(traceback.format_exc())
    finally:
        loop.run_until_complete(cleanup())
        loop.stop()
