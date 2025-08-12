#!/usr/bin/env python3
"""
Test script for WASM deployer implementation.

This script demonstrates the usage of both the base WasmDeployer
and the CPythonWasmDeployer classes.
"""

import sys
import json
from pathlib import Path

# Add lib to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from lib.wasm_deployer import WasmDeployer, ExecutionResult, ExecutionStatus
from lib.cpython_wasm_deployer import CPythonWasmDeployer, execute_python_in_wasm


def test_cpython_deployer():
    """Test the CPython WASM deployer"""
    print("=" * 50)
    print("Testing CPython WASM Deployer")
    print("=" * 50)
    
    # Test 1: Simple Python script
    print("\n1. Testing simple Python script:")
    simple_script = """
import json
import math

def main():
    # This would normally receive input_data via JSON
    result = {
        "message": "Hello from Python in WASM!",
        "pi": math.pi,
        "calculation": 2 + 2
    }
    return result

if __name__ == "__main__":
    main()
"""
    
    input_data = {"test": "data", "number": 42}
    result = execute_python_in_wasm(simple_script, input_data)
    
    print(f"Status: {result.status.value}")
    print(f"Execution time: {result.execution_time_ms:.2f}ms")
    if result.output:
        print(f"Output: {json.dumps(result.output, indent=2)}")
    if result.error:
        print(f"Error: {result.error}")
    
    # Test 2: Script with blocked imports
    print("\n2. Testing script with blocked imports (should fail):")
    dangerous_script = """
import os
import subprocess

def main():
    # This should be blocked
    os.system("echo 'This is dangerous!'")
    return {"status": "hacked"}
"""
    
    deployer = CPythonWasmDeployer()
    try:
        result = deployer.execute_python_script(dangerous_script, {})
        print(f"Status: {result.status.value}")
        if result.error:
            print(f"Error (expected): {result.error}")
    except Exception as e:
        print(f"Blocked successfully: {e}")
    
    # Test 3: Script with allowed imports
    print("\n3. Testing script with allowed imports:")
    safe_script = """
import json
import math
import random

def process_data(input_data):
    return {
        "random_number": random.randint(1, 100),
        "sqrt_of_input": math.sqrt(input_data.get("number", 1)),
        "input_keys": list(input_data.keys())
    }

def main():
    # In real implementation, this would receive actual input
    return process_data({"number": 16})
"""
    
    result = execute_python_in_wasm(safe_script, {"number": 16, "name": "test"})
    print(f"Status: {result.status.value}")
    print(f"Execution time: {result.execution_time_ms:.2f}ms")
    if result.output:
        print(f"Output: {json.dumps(result.output, indent=2)}")
    if result.error:
        print(f"Error: {result.error}")


def test_json_communication():
    """Test JSON communication channel"""
    print("\n" + "=" * 50)
    print("Testing JSON Communication Channel")
    print("=" * 50)
    
    from lib.wasm_deployer import JSONCommunicationChannel
    
    # Test valid JSON data
    valid_data = {"name": "test", "value": 42, "array": [1, 2, 3]}
    print(f"\n1. Valid JSON data: {valid_data}")
    print(f"Is valid: {JSONCommunicationChannel.validate_json_data(valid_data)}")
    
    serialized = JSONCommunicationChannel.serialize_input(valid_data)
    print(f"Serialized: {serialized}")
    
    deserialized = JSONCommunicationChannel.deserialize_output(serialized)
    print(f"Deserialized: {deserialized}")
    print(f"Round-trip successful: {valid_data == deserialized}")
    
    # Test invalid JSON data
    print(f"\n2. Invalid JSON data (function object):")
    invalid_data = {"function": lambda x: x}
    print(f"Is valid: {JSONCommunicationChannel.validate_json_data(invalid_data)}")


def test_security_features():
    """Test security features of the deployer"""
    print("\n" + "=" * 50)
    print("Testing Security Features")
    print("=" * 50)
    
    deployer = CPythonWasmDeployer(timeout_ms=1000)
    
    # Test import restrictions
    security_tests = [
        {
            "name": "Blocked os import",
            "script": "import os\nprint('Should not work')",
            "should_fail": True
        },
        {
            "name": "Blocked subprocess import",
            "script": "import subprocess\nsubprocess.run(['ls'])",
            "should_fail": True
        },
        {
            "name": "Blocked eval call",
            "script": "eval('print(\"dangerous\")')",
            "should_fail": True
        },
        {
            "name": "Allowed math import",
            "script": "import math\nresult = math.sqrt(4)",
            "should_fail": False
        }
    ]
    
    for test in security_tests:
        print(f"\nTesting: {test['name']}")
        try:
            result = deployer.execute_python_script(test['script'], {})
            if test['should_fail'] and result.status != ExecutionStatus.ERROR:
                print(f"⚠️  Security test failed - should have been blocked!")
            elif not test['should_fail'] and result.status == ExecutionStatus.ERROR:
                print(f"⚠️  Valid script was incorrectly blocked!")
            else:
                print(f"✅ Security test passed")
            
            if result.error:
                print(f"   Error: {result.error}")
                
        except Exception as e:
            if test['should_fail']:
                print(f"✅ Correctly blocked: {e}")
            else:
                print(f"⚠️  Valid script failed: {e}")


def main():
    """Run all tests"""
    print("WASM Deployer Test Suite")
    print("=" * 50)
    
    try:
        test_cpython_deployer()
        test_json_communication()
        test_security_features()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()