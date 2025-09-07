import bot.highlevel as ship
import asyncio


async def on_ready():
    pass

async def on_update():
    pass


asyncio.run(ship.main(on_ready, on_update))