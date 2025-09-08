

HAPPY_EMOTE = "<:happy:1404699694776582164>"
NO_EMOTE = "<:no:1404699704876466357>"
INFO_EMOTE = "<:phonecall:1414650211732553859>"
WARNING_EMOTE = "<:tja:1404699700862386186>"

def success(s: str):
    return f"{HAPPY_EMOTE} :white_check_mark: " + s

def info(s: str):
    return f"{INFO_EMOTE} :information_source: " + s

def warning(s: str):
    return f"{WARNING_EMOTE} :warning: " + s

def error(s: str):
    return f"{NO_EMOTE} :no_entry: " + s

