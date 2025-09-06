import lowlevel
import json
import threading

actions = set()

def left():
    actions.add("left")

def right():
    actions.add("right")

def forward():
    actions.add("forward")

def shoot():
    actions.add("shoot")

def submit_actions():
    lowlevel.send(json.dumps(list(actions)))
    actions.clear()

def mainloop(on_ready, on_update, on_timeout):
    '''
    Runs the bot in a loop compliant with the protocol.
    '''
    while True:
        lowlevel.receive()