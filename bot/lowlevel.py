# We generally communicate to the host using standard input. Wrappers are to allow a later switch
# to something with less latency.
def send(message: str):
    '''
    Send a message to the host.
    '''
    print(message)

def receive() -> str:
    '''
    Wait for the next message from the host and receive it.
    '''
    return input()

