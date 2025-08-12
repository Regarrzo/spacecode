# Spacecode - Space-based AI Agent Competition Platform

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Project Overview

Spacecode is a Python-based physics simulation platform for AI agent competitions in space. The system includes:
- Physics simulation engine for space combat/movement
- Pygame-based visualization for debugging and demonstrations  
- Agent communication protocols
- Tournament management system (planned)
- Discord bot integration (planned)

## Working Effectively

### Bootstrap and Setup
The repository uses pure Python with minimal external dependencies. No build process is required.

**Initial Setup (from fresh clone):**
```bash
# Install the primary dependency
pip3 install pygame
```
- Time required: 10-30 seconds. NEVER CANCEL.
- This is the only required external dependency for core functionality.
- **NOTE**: If network issues cause timeouts, retry the installation. The pygame dependency is essential for visualization but core simulation in `lib/sim.py` works without it.

**Optional Development Tools:**
```bash
# Install development tools for code quality
pip3 install flake8 black pytest
```
- Time required: 30-45 seconds. NEVER CANCEL.

### Testing and Validation

**Basic functionality test:**
```bash
python3 -c "from lib.sim import *; print('Core library imported successfully')"
```

**Complete simulation test:**
```bash
python3 -c "
from lib.sim import *
from collections import defaultdict
cfg = SimConfig(gravity_const=1e-5, seed=42)
game = Game(cfg)
ship = Ship(pos=0.25+0.25j, old_pos=0.25+0.25j, rot=1+0j, old_rot=1+0j, mass=0.01, inertia=0.1, radius=0.015)
game.bodies.append(ship)
actions = defaultdict(set)
actions[ship].add(Action.FORWARD)
game.step(actions, 0.016)
print('Simulation step completed successfully')
"
```

**Compilation check:**
```bash
python3 -m py_compile lib/sim.py ai_slop_visualisation.py
```
- Time required: 2-3 seconds. NEVER CANCEL.

### Running the Application

**Visualization (Debug/Demo Mode):**
```bash
python3 ai_slop_visualisation.py
```
- **IMPORTANT**: This will hang in headless environments (servers, CI). Only run this in environments with display capability.
- In headless environments, the app attempts to initialize but hangs at pygame display initialization.
- Controls: W/UP=thrust, A/LEFT=turn left, D/RIGHT=turn right
- Physics runs at 60 FPS with real-time visualization

### Code Quality and Linting

**Run linter:**
```bash
python3 -m flake8 --max-line-length=120 lib/ ai_slop_visualisation.py
```
- Time required: 5-10 seconds. NEVER CANCEL.
- **NOTE**: Current codebase has style issues (star imports, spacing) but functionality is correct.

**Format code:**
```bash
python3 -m black --line-length=120 lib/ ai_slop_visualisation.py
```

**Run tests:**
```bash
python3 -m pytest
```
- **NOTE**: No tests currently exist. Pytest returns "no tests collected" but setup is ready.

## Validation Scenarios

After making changes, ALWAYS test these scenarios to ensure functionality:

### 1. Basic Import and Simulation
```bash
python3 -c "
from lib.sim import *
from collections import defaultdict
import math

# Test configuration
cfg = SimConfig(gravity_const=1e-5, ship_thrust_force=0.001, ship_torque=0.50, seed=42)
game = Game(cfg)

# Create test ship
ship = Ship(pos=0.25+0.25j, old_pos=0.25+0.25j, rot=1+0j, old_rot=1+0j, mass=0.01, inertia=0.1, radius=0.015)
game.bodies.append(ship)

# Create gravity source
planet = Body(pos=0.75+0.75j, old_pos=0.75+0.75j, mass=300.0, inertia=10.0, radius=0.03)
game.bodies.append(planet)

# Test ship actions
actions = defaultdict(set)
actions[ship].add(Action.FORWARD)
actions[ship].add(Action.LEFT)

# Run simulation step
initial_pos = ship.pos
game.step(actions, 0.016)
final_pos = ship.pos

# Validate movement occurred
assert abs(final_pos - initial_pos) > 1e-6, 'Ship should have moved'

# Test view generation
view = game.generate_relative_view(ship)
assert len(view) >= 1, 'View should contain visible objects'

print('✓ Core simulation validation passed')
"
```

### 2. Physics System Validation
```bash
python3 -c "
from lib.sim import *
import math

# Test individual physics components
cfg = SimConfig()
phys = PhysicsSystem(cfg)

# Test body creation and properties
body = Body(pos=0.5+0.5j, mass=10.0, radius=0.1)
assert body.pos == 0.5+0.5j, 'Body position should be set correctly'
assert body.mass == 10.0, 'Body mass should be set correctly'

# Test distance calculation  
body2 = Body(pos=0.7+0.7j, mass=5.0, radius=0.05)
distance = body.distance_to(body2)
expected = abs(0.2+0.2j)  # sqrt(0.08) ≈ 0.283
assert abs(distance - expected) < 1e-10, f'Distance calculation failed: {distance} vs {expected}'

# Test intersection (bodies are far apart, should not intersect)
assert not phys.intersects(body, body2), 'Bodies should not intersect'

print('✓ Physics system validation passed')
"
```

### 3. Visualization Startup Test (Display Environment Only)
Only run this in environments with display capability:
```bash
# Test that visualization can start (will run until manually closed)
timeout 5s python3 ai_slop_visualisation.py 2>/dev/null || echo "Visualization startup test completed (expected timeout in headless)"
```

## Project Structure

### Repository Root
```
.
├── README.md                    # Project overview and component description
├── LICENSE                      # MIT license
├── requirements.txt            # Empty (dependencies installed via pip)
├── lib/                        # Core simulation library
│   ├── __init__.py            # Empty module init  
│   └── sim.py                 # Physics engine and game logic
├── ai_slop_visualisation.py   # Pygame-based visualization/demo
└── standalone.py              # Empty placeholder file
```

### Key Files

**lib/sim.py** - Core simulation engine containing:
- `SimConfig`: Configuration for physics parameters
- `Body`: Basic physics object with position, rotation, mass
- `Ship`: Controllable agent extending Body
- `Action`: Enum for ship actions (FORWARD, LEFT, RIGHT, SHOOT)
- `PhysicsSystem`: Verlet integration and force calculations
- `Game`: Main simulation coordinator

**ai_slop_visualisation.py** - Interactive visualization:
- Real-time physics visualization using pygame
- Manual ship control for testing and debugging
- Displays ship position, velocity, angle, and FPS
- Useful for validating physics changes

## Development Guidelines

### Making Changes
- **ALWAYS** run the validation scenarios after making changes to core physics
- **ALWAYS** test basic import: `python3 -c "from lib.sim import *"`
- **ALWAYS** check compilation: `python3 -m py_compile lib/sim.py`
- Run linting with: `python3 -m flake8 --max-line-length=120 lib/`

### Common Development Tasks

**Adding new physics features:**
1. Modify `SimConfig` to add configuration parameters
2. Update `PhysicsSystem` to implement the physics  
3. Test with validation scenario #2
4. Update `Game.step()` if needed for integration
5. Test with full simulation in validation scenario #1

**Modifying ship behavior:**
1. Update `Ship` class or `Action` enum as needed
2. Modify `Game._process_inputs()` for new actions
3. Test with validation scenario #1
4. Verify changes in visualization if display available

**Performance optimization:**
1. Profile with: `python3 -m cProfile -s cumtime -c "your_test_code_here"`
2. Focus on `Game.step()` and `PhysicsSystem` methods
3. Validate performance doesn't break physics accuracy

### Code Quality Standards
- Follow PEP 8 style (use `python3 -m black --line-length=120`)
- Avoid star imports in new code (existing code uses them for API convenience)
- Add type hints for new public methods
- Keep line length ≤ 120 characters
- Use meaningful variable names following physics conventions

### Troubleshooting

**Import errors:** Ensure you're running from repository root and `lib/` is in Python path

**Pygame issues:** 
- In headless environments, pygame import works but display creation hangs
- Use `pip3 install pygame` if module not found
- For testing visualization, use timeout: `timeout 5s python3 ai_slop_visualisation.py`

**Physics behaving unexpectedly:** 
- Check `SimConfig` parameters (gravity_const, forces, torques)
- Validate with step-by-step simulation test
- Use visualization to debug visually if display available

**Performance issues:**
- Physics is O(n²) for gravity calculations between all bodies
- Large numbers of bodies (>100) may slow down significantly
- Consider spatial partitioning for optimization if needed

## Time Expectations
All operations are very fast in this lightweight Python project:
- **Dependency installation**: 10-15 seconds (pygame only)
- **Code compilation check**: 2-3 seconds  
- **Linting entire codebase**: 5-10 seconds
- **Basic simulation test**: <1 second
- **Full validation scenarios**: <5 seconds total

**NEVER CANCEL** any of these operations - they complete quickly.

## Common Command Reference

```bash
# Quick development cycle
pip3 install pygame                                    # One-time setup
python3 -c "from lib.sim import *"                    # Import test
python3 -m py_compile lib/sim.py                      # Syntax check  
python3 -m flake8 --max-line-length=120 lib/         # Style check

# Full validation (run after changes)
python3 -c "[validation_scenario_1_code]"            # Core sim test
python3 -c "[validation_scenario_2_code]"            # Physics test
python3 ai_slop_visualisation.py                     # Visual test (display only)
```