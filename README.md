# spacecode

All components:
- the game code for the environment in which the agents compete
- the match manager that manages single fights between two programs
- the communication protocol between programs and the match manager
- the wasm wrapper that loads the programs in a sandbox
- the tournament manager that orchestrates battles between programs and manages all available ones in a folder
- the discord bot that:
  - downloads all python programs sent to a certain channel
  - validates that the code is valid and runs, makes sure that it's not unpacking a zip bomb, then saves it to a folder
  - regularily uses the tournament manager to compare strategies
  - posts the results in a channel
- the GUI to visualise battles and debug agents
- some developer tools to make it easier to develop bots, for example allowing running unsandboxed code locally to allow for debugging
