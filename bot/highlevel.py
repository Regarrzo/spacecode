import lowlevel
import json
import threading
from dataclasses import dataclass, asdict

@dataclass
class BotInfo:
    name: str = ""
    creator: str = ""
    version: str = ""
    color: str = "#FFFFFF"

actions = set()
info = BotInfo()

def left():
    actions.add("left")

def right():
    actions.add("right")

def forward():
    actions.add("forward")

def shoot():
    actions.add("shoot")

def submit_actions():
    lowlevel.send(list(actions))
    actions.clear()

def set_info(name: str, creator: str, version: str, color: str):
    info.name = name
    info.creator = creator
    info.version = version
    info.color = color

def timeout():
    '''
    Checks whether the bot has received the timeout signal.
    '''


async def main(on_ready, on_update):
    '''
    Runs the bot in a loop compliant with the protocol.
    '''
    while True:
        msg = json.loads(lowlevel.receive())
        
        match msg["type"]:
            case "ready":
                await on_ready()
                lowlevel.send("ok")
            case "info":
                lowlevel.send(asdict(info))
            case "step":
                await on_update()
                submit_actions()

