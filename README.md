# spacecode

All components:
- the game code for the environment in which the agents compete
- the match manager that manages single fights between two programs
- the communication protocol between programs and the match manager
- **✅ the wasm wrapper that loads the programs in a sandbox** ⭐ *NEW*
- the tournament manager that orchestrates battles between programs and manages all available ones in a folder
- the discord bot that:
  - downloads all python programs sent to a certain channel
  - validates that the code is valid and runs, makes sure that it's not unpacking a zip bomb, then saves it to a folder
  - regularily uses the tournament manager to compare strategies
  - posts the results in a channel
- the GUI to visualise battles and debug agents
- some developer tools to make it easier to develop bots, for example allowing running unsandboxed code locally to allow for debugging

## 🛡️ WASM Deployer (NEW!)

**Complete sandboxed execution system for bot scripts using WebAssembly.**

### Features
- **🔒 Complete Sandboxing**: Scripts run in isolated WASM environment
- **📡 JSON-only Communication**: Secure input/output channel  
- **⚡ Resource Limits**: Memory, CPU, and execution time limits
- **🐍 CPython Support**: Specialized subclass for Python bot execution
- **🛡️ Security**: Import restrictions, dangerous function blocking
- **⚙️ Wasmtime Integration**: Uses industry-standard WASM runtime

### Quick Start
```python
from lib.cpython_wasm_deployer import execute_python_in_wasm

# Execute a bot script safely
result = execute_python_in_wasm("""
import math
def bot_main(input_data):
    return {"actions": ["FORWARD", "SHOOT"]}
""", input_data={"game_state": {}})

print(result.output["actions"])  # ['FORWARD', 'SHOOT']
```

### Examples
- `standalone.py` - Complete integration demo
- `example_bots.py` - 5 different bot strategies
- `test_wasm_deployer.py` - Comprehensive test suite
- `docs/WASM_DEPLOYER.md` - Full documentation

Other things:
- rely mostly on the Python standard library for everything that is feasible
  - Why: this makes contributing easier and also makes bot development itself easier
- make sure bot developers only need a singular import that contains everything they need. It should be as easy as possible to set up a bot with very very little boilerplate necessary
  - Why: having less hurdles makes it more likely that anyone will actually be interested in making a bot for this
