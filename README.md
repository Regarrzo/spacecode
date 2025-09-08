# spacecode [Everything is W.I.P and not functional as of yet]

## Contents
- A Python-WASM interface allowing sandboxed WASM code to interface with Python
- Multiple environments that allow for competition between bots scripted using WASM
- A Discord bot that organises tournaments between user-submitted scripts, computes their ELO and generates replays
- A script for packaging Python modules with a precompiled, stripped down Python interpreter compiled to WASM to allow user-submitted Python scripts to run in the same sandbox.

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

Other things:
- rely mostly on the Python standard library for everything that is feasible
  - Why: this makes contributing easier and also makes bot development itself easier
- make sure bot developers only need a singular import that contains everything they need. It should be as easy as possible to set up a bot with very very little boilerplate necessary
  - Why: having less hurdles makes it more likely that anyone will actually be interested in making a bot for this
