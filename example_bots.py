#!/usr/bin/env python3
"""
Example bot scripts for the spacecode WASM deployer.

These scripts demonstrate different bot strategies and behaviors
that can be executed safely in the WASM sandbox.
"""

# Simple aggressive bot
AGGRESSIVE_BOT = '''
import json
import math

def bot_main(input_data):
    """
    Aggressive bot that always moves forward and shoots frequently.
    """
    game_state = input_data.get('game_state', {})
    time_step = input_data.get('time_step', 0)
    
    actions = ['FORWARD']  # Always thrust forward
    
    # Shoot very frequently
    if time_step % 10 == 0:
        actions.append('SHOOT')
    
    # Turn toward enemies (simplified logic)
    if time_step % 50 < 25:
        actions.append('RIGHT')
    else:
        actions.append('LEFT')
    
    return {
        'actions': actions,
        'debug_info': {
            'bot_name': 'AggressiveBot',
            'strategy': 'attack',
            'actions_count': len(actions)
        }
    }

def main():
    return bot_main({
        'game_state': {'visible_objects': []},
        'ship_id': 1,
        'time_step': 0
    })
'''

# Defensive circle bot
DEFENSIVE_BOT = '''
import json
import math

def bot_main(input_data):
    """
    Defensive bot that moves in circles and shoots cautiously.
    """
    game_state = input_data.get('game_state', {})
    time_step = input_data.get('time_step', 0)
    
    actions = []
    
    # Move in defensive circles
    if time_step % 200 < 100:
        actions.append('FORWARD')
        actions.append('LEFT')
    else:
        actions.append('FORWARD')
        actions.append('RIGHT')
    
    # Shoot only when necessary
    if time_step % 60 == 0:
        actions.append('SHOOT')
    
    return {
        'actions': actions,
        'debug_info': {
            'bot_name': 'DefensiveBot',
            'strategy': 'defensive_circle',
            'circle_phase': 'left' if time_step % 200 < 100 else 'right'
        }
    }

def main():
    return bot_main({
        'game_state': {'visible_objects': []},
        'ship_id': 2,
        'time_step': 0
    })
'''

# Smart evasive bot
EVASIVE_BOT = '''
import json
import math
import random

def bot_main(input_data):
    """
    Evasive bot that uses random movements to avoid predictability.
    """
    game_state = input_data.get('game_state', {})
    time_step = input_data.get('time_step', 0)
    
    actions = []
    
    # Use time step as seed for deterministic "randomness"
    random.seed(time_step // 10)
    
    # Random evasive maneuvers
    move_choice = random.randint(1, 4)
    
    if move_choice == 1:
        actions.extend(['FORWARD', 'LEFT'])
    elif move_choice == 2:
        actions.extend(['FORWARD', 'RIGHT'])
    elif move_choice == 3:
        actions.append('LEFT')
    else:
        actions.append('RIGHT')
    
    # Opportunistic shooting
    if random.randint(1, 20) == 1:
        actions.append('SHOOT')
    
    return {
        'actions': actions,
        'debug_info': {
            'bot_name': 'EvasiveBot',
            'strategy': 'random_evasion',
            'move_choice': move_choice,
            'shooting': 'SHOOT' in actions
        }
    }

def main():
    return bot_main({
        'game_state': {'visible_objects': []},
        'ship_id': 3,
        'time_step': 0
    })
'''

# Mathematical precision bot
MATH_BOT = '''
import json
import math

def bot_main(input_data):
    """
    Bot that uses mathematical calculations for precise movements.
    """
    game_state = input_data.get('game_state', {})
    time_step = input_data.get('time_step', 0)
    ship_position = game_state.get('ship_position', [0.5, 0.5])
    
    actions = []
    
    # Calculate movement based on sine wave for smooth motion
    phase = time_step * 0.05
    
    # Sine wave determines forward thrust
    if math.sin(phase) > 0:
        actions.append('FORWARD')
    
    # Cosine wave determines turning
    if math.cos(phase) > 0.5:
        actions.append('LEFT')
    elif math.cos(phase) < -0.5:
        actions.append('RIGHT')
    
    # Shoot based on mathematical sequence
    if time_step % int(math.pi * 10) == 0:
        actions.append('SHOOT')
    
    # Calculate distance from center
    center_dist = math.sqrt((ship_position[0] - 0.5)**2 + (ship_position[1] - 0.5)**2)
    
    return {
        'actions': actions,
        'debug_info': {
            'bot_name': 'MathBot',
            'strategy': 'mathematical_precision',
            'phase': phase,
            'center_distance': center_dist,
            'sine_val': math.sin(phase),
            'cosine_val': math.cos(phase)
        }
    }

def main():
    return bot_main({
        'game_state': {
            'visible_objects': [],
            'ship_position': [0.5, 0.5]
        },
        'ship_id': 4,
        'time_step': 0
    })
'''

# Patrol bot
PATROL_BOT = '''
import json
import math

def bot_main(input_data):
    """
    Bot that patrols in a rectangular pattern.
    """
    game_state = input_data.get('game_state', {})
    time_step = input_data.get('time_step', 0)
    
    actions = []
    
    # Patrol in rectangular pattern
    cycle_length = 400  # Total cycle length
    phase = time_step % cycle_length
    
    if phase < 100:
        # Move right
        actions.extend(['FORWARD', 'RIGHT'])
    elif phase < 200:
        # Move up
        actions.append('FORWARD')
    elif phase < 300:
        # Move left
        actions.extend(['FORWARD', 'LEFT'])
    else:
        # Move down
        actions.extend(['FORWARD', 'LEFT'])
    
    # Shoot at patrol points
    if phase % 100 < 5:
        actions.append('SHOOT')
    
    return {
        'actions': actions,
        'debug_info': {
            'bot_name': 'PatrolBot',
            'strategy': 'rectangular_patrol',
            'patrol_phase': phase,
            'cycle_position': phase / cycle_length
        }
    }

def main():
    return bot_main({
        'game_state': {'visible_objects': []},
        'ship_id': 5,
        'time_step': 0
    })
'''

def main():
    """Demonstrate all example bots"""
    from lib.cpython_wasm_deployer import CPythonWasmDeployer
    
    bots = {
        'Aggressive': AGGRESSIVE_BOT,
        'Defensive': DEFENSIVE_BOT,
        'Evasive': EVASIVE_BOT,
        'Mathematical': MATH_BOT,
        'Patrol': PATROL_BOT
    }
    
    deployer = CPythonWasmDeployer(timeout_ms=2000)
    
    print("=" * 60)
    print("Example Bot Scripts Demonstration")
    print("=" * 60)
    
    for bot_name, script in bots.items():
        print(f"\n🤖 Testing {bot_name} Bot:")
        print("-" * 30)
        
        try:
            # Test bot with different time steps
            for step in [0, 25, 50, 100]:
                input_data = {
                    'game_state': {
                        'ship_position': [0.4, 0.6],
                        'visible_objects': []
                    },
                    'ship_id': 1,
                    'time_step': step
                }
                
                result = deployer.execute_python_script(script, input_data)
                
                if result.status.value == 'success' and result.output:
                    actions = result.output.get('actions', [])
                    debug_info = result.output.get('debug_info', {})
                    
                    print(f"  Step {step:3d}: Actions={actions} "
                          f"({result.execution_time_ms:.1f}ms)")
                    
                    if debug_info and 'strategy' in debug_info:
                        print(f"           Strategy: {debug_info['strategy']}")
                else:
                    print(f"  Step {step:3d}: Failed - {result.error}")
                    
        except Exception as e:
            print(f"❌ Failed to test {bot_name} bot: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All example bots demonstrated!")
    print("=" * 60)

if __name__ == "__main__":
    main()