# Protocol
This document describes the way in which bots interact with the host.

## General Information
Communication happens through stdin/stdout. 
Bots must check for input in a loop, parse the input and send appropriate 
outputs. It works a bit similarily to the UCI protocol for chess engines 
or REST protocols.
Messages are encoded in json.

A wrapper for the communication protocol is already provided.

## Messages
### info
The host requests metadata about the bot.

#### Message:
```json
{
    "type": "info"
}
```
#### Response (Example):
```json
{
    "name" : "MyBotName",
    "creator" : "MyName",
    "version" : "Beta 1 Test",
    "color": "#1d232b"
}
```

### newmatch
The host tells the bot that the next match is about to start.
It also provides information about the result of the last match.

Possible values for the `result` field are `win`, `draw` or `lose`.

#### Message (Example):
```json
{
    "type": "newmatch",
    "result": "win" 
}
```
#### Response:
```json
"ok"
```

### step
The host provides the bot with the information given by the sensors 
of its ship and waits for its action.

#### Message
```json
{
    "bodies": [Bodyviews...]
    "front_raycast": 0.23
}
```
#### Response (Example):
```json
["front", "left", "shoot"]
```
