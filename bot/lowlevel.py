from typing import Any
import json

# We generally communicate to the host using standard input. Wrappers are to allow a later switch
# to something with less latency.
def send(object: Any):
    '''
    Send an object to the host. The object must be serializable.
    '''
    print(json.dumps(object))

def receive() -> str:
    '''
    Wait for the next message from the host and receive it.
    '''
    return input()

