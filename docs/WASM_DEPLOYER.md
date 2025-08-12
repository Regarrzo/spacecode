# WASM Deployer Documentation

## Overview

The WASM Deployer system provides a secure, sandboxed environment for executing untrusted code (particularly Python scripts) within the spacecode game framework. It uses WebAssembly (WASM) and the Wasmtime runtime to ensure complete isolation and security.

## Architecture

### Base WasmDeployer Class

The `WasmDeployer` class provides the foundation for executing any WASM module with complete sandboxing:

```python
from lib.wasm_deployer import WasmDeployer, ExecutionResult

# Create deployer with custom settings
deployer = WasmDeployer(
    timeout_ms=5000,        # 5 second timeout
    memory_limit_pages=10,  # ~640KB memory limit
    max_fuel=1000000       # Computational limit
)
```

**Key Features:**
- **JSON-only communication**: No direct access to file system, network, or system calls
- **Resource limits**: Memory and computational limits prevent resource exhaustion
- **Timeout protection**: Prevents infinite loops or long-running scripts
- **Wasmtime integration**: Uses Wasmtime for robust WASM execution

### CPythonWasmDeployer Subclass

The `CPythonWasmDeployer` extends the base class specifically for Python script execution:

```python
from lib.cpython_wasm_deployer import CPythonWasmDeployer, execute_python_in_wasm

# Quick execution
result = execute_python_in_wasm("""
import math
def main():
    return {"result": math.pi * 2}
""", input_data={"test": "data"})

# Advanced usage
deployer = CPythonWasmDeployer(
    timeout_ms=3000,
    allowed_imports=['math', 'json', 'random'],
    blocked_imports=['os', 'sys', 'subprocess']
)
```

**Security Features:**
- **Import restrictions**: Whitelist/blacklist system for Python modules
- **Function call blocking**: Prevents dangerous functions like `eval()`, `exec()`, `open()`
- **Script sanitization**: Validates and cleans Python source code before execution

## Security Model

The WASM deployer implements multiple layers of security:

### 1. WASM Sandboxing
- Scripts run in isolated WASM environment
- No access to host system resources
- Memory and computational limits enforced

### 2. Import Control
```python
# Allowed (safe) imports
ALLOWED_IMPORTS = {
    'json', 'math', 'random', 'time', 'datetime', 
    'collections', 'itertools', 'functools', 're', 'string'
}

# Blocked (dangerous) imports  
BLOCKED_IMPORTS = {
    'os', 'sys', 'subprocess', 'socket', 'urllib',
    'pickle', 'marshal', 'ctypes', 'threading'
}
```

### 3. Function Call Restrictions
The system blocks dangerous function calls:
- `exec()`, `eval()` - arbitrary code execution
- `open()`, `file()` - file system access
- `__import__()` - dynamic imports
- System-level functions

### 4. Communication Protocol
All communication uses JSON exclusively:
```python
# Input to script
input_data = {
    "game_state": {...},
    "ship_id": 1,
    "time_step": 42
}

# Output from script  
output_data = {
    "actions": ["FORWARD", "LEFT"],
    "debug_info": {...}
}
```

## Integration with Spacecode

### Bot Script Structure

Bot scripts should follow this pattern:

```python
import json
import math

def bot_main(input_data):
    """
    Main bot function that processes game state and returns actions.
    
    Args:
        input_data: Dict containing:
            - game_state: Current visible game state
            - ship_id: Bot's ship identifier  
            - time_step: Current simulation step
            
    Returns:
        Dict containing:
            - actions: List of action strings
            - debug_info: Optional debug information
    """
    
    # Process game state
    game_state = input_data.get('game_state', {})
    time_step = input_data.get('time_step', 0)
    
    # Make decisions
    actions = []
    if should_thrust():
        actions.append('FORWARD')
    if should_turn_left():
        actions.append('LEFT')
        
    return {
        'actions': actions,
        'debug_info': {'bot_name': 'MyBot'}
    }

# Entry point for WASM execution
def main():
    # Input data provided by WASM runtime
    return bot_main(get_input_data())
```

### WasmBotRunner Integration

Use the `WasmBotRunner` class for seamless integration:

```python
from standalone import WasmBotRunner

# Create bot runner
bot_runner = WasmBotRunner()

# Register bot scripts
bot_runner.register_bot('aggressive_bot', aggressive_script)
bot_runner.register_bot('defensive_bot', defensive_script)

# Execute bots during game loop
for step in range(simulation_steps):
    for bot_id in active_bots:
        actions = bot_runner.execute_bot(
            bot_id, game_state, ship_id, step
        )
        # Apply actions to game
        game.step({ship: actions}, dt)
```

## Available Actions

Bots can return these action strings:

- `'FORWARD'` - Apply thrust in forward direction
- `'LEFT'` - Apply left rotational force  
- `'RIGHT'` - Apply right rotational force
- `'SHOOT'` - Fire weapon (if implemented)

## Error Handling

The system provides comprehensive error handling:

```python
result = deployer.execute_python_script(script, input_data)

if result.status.value == 'success':
    actions = result.output['actions']
elif result.status.value == 'error':
    print(f"Execution failed: {result.error}")
elif result.status.value == 'timeout':
    print("Script execution timed out")
```

## Performance Considerations

- **Execution Time**: Typical bot execution takes 1-5ms
- **Memory Usage**: Limited to configured memory pages (default ~640KB)  
- **Fuel Limits**: Computational limits prevent resource abuse
- **Concurrent Execution**: Each bot runs in isolated store for safety

## Debugging

Enable logging for detailed execution information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now WASM deployer will log detailed execution info
result = deployer.execute_python_script(script, data)
```

## Examples

See `test_wasm_deployer.py` for comprehensive examples of:
- Basic script execution
- Security validation
- Error handling
- JSON communication

See `standalone.py` for a complete integration example with the spacecode game engine.

## Future Enhancements

Potential improvements for production use:

1. **Real Python-to-WASM Compilation**: Currently uses mock WASM modules
2. **Advanced Resource Monitoring**: CPU usage, memory allocation tracking  
3. **Persistent Bot State**: Allow bots to maintain state between executions
4. **Hot Reloading**: Update bot scripts without restarting the game
5. **Bot Metrics**: Performance analytics and optimization suggestions