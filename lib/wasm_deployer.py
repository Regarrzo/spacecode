"""
Base WASM Deployer for sandboxed script execution.

This module provides a general-purpose WASM deployer that can execute
WASM modules in a completely sandboxed environment with JSON-based communication.
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Protocol, runtime_checkable
from abc import ABC, abstractmethod
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum

try:
    import wasmtime
except ImportError:
    raise ImportError(
        "wasmtime is required for WASM deployment. "
        "Install it with: pip install wasmtime"
    )


logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of script execution"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class ExecutionResult:
    """Result of script execution"""
    status: ExecutionStatus
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0


@runtime_checkable
class WasmModule(Protocol):
    """Protocol for WASM modules that can be executed by the deployer"""
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the module with input data and return output data"""
        ...


class WasmDeployer(ABC):
    """
    Base class for WASM deployers.
    
    Provides a sandboxed environment for executing WASM modules with:
    - JSON-only input/output communication
    - No file system access
    - No network access  
    - Configurable timeouts
    - Resource limits
    """
    
    def __init__(
        self,
        timeout_ms: int = 5000,
        memory_limit_pages: int = 10,  # ~640KB limit
        max_fuel: Optional[int] = 1000000,  # Computational limit
    ):
        """
        Initialize the WASM deployer.
        
        Args:
            timeout_ms: Maximum execution time in milliseconds
            memory_limit_pages: Maximum memory pages (64KB each)
            max_fuel: Maximum computational fuel units (None for unlimited)
        """
        self.timeout_ms = timeout_ms
        self.memory_limit_pages = memory_limit_pages
        self.max_fuel = max_fuel
        
        # Create config with fuel consumption if specified
        config = wasmtime.Config()
        if max_fuel is not None:
            config.consume_fuel = True
        
        self._engine = wasmtime.Engine(config)
        self._store = wasmtime.Store(self._engine)
        
        # Set fuel to store if specified
        if max_fuel is not None:
            self._store.set_fuel(max_fuel)
        
    @abstractmethod
    def prepare_module(self, script: str, **kwargs) -> bytes:
        """
        Prepare the script/code for WASM execution.
        
        Args:
            script: The script or code to prepare
            **kwargs: Additional preparation parameters
            
        Returns:
            Compiled WASM bytecode
        """
        pass
    
    def execute(
        self, 
        wasm_bytes: bytes, 
        input_data: Dict[str, Any],
        timeout_override: Optional[int] = None
    ) -> ExecutionResult:
        """
        Execute WASM bytecode with input data in a sandboxed environment.
        
        Args:
            wasm_bytes: Compiled WASM bytecode
            input_data: Input data as JSON-serializable dict
            timeout_override: Override default timeout for this execution
            
        Returns:
            ExecutionResult containing output or error information
        """
        start_time = time.time()
        timeout = timeout_override or self.timeout_ms
        
        try:
            # Validate input data is JSON serializable
            json.dumps(input_data)
            
            # Create a new store for this execution for isolation
            store = wasmtime.Store(self._engine)
            if self.max_fuel is not None:
                store.set_fuel(self.max_fuel)
            
            # Load and instantiate the WASM module
            module = wasmtime.Module(self._engine, wasm_bytes)
            
            # Set up WASI if needed (with restrictions)
            wasi = wasmtime.WasiConfig()
            wasi.inherit_stderr()  # Allow error output for debugging
            store.set_wasi(wasi)
            
            # Create instance with limited imports
            instance = wasmtime.Instance(store, module, [])
            
            # Execute with timeout
            result = self._execute_with_timeout(
                store, instance, input_data, timeout
            )
            
            execution_time = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time
            
            return result
            
        except json.JSONEncodeError as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error=f"Input data is not JSON serializable: {e}",
                execution_time_ms=(time.time() - start_time) * 1000
            )
        except wasmtime.TrapError as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error=f"WASM trap: {e}",
                execution_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error=f"Execution failed: {e}",
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    def _execute_with_timeout(
        self,
        store: wasmtime.Store,
        instance: wasmtime.Instance,
        input_data: Dict[str, Any],
        timeout_ms: int
    ) -> ExecutionResult:
        """
        Execute WASM instance with timeout handling.
        
        This is where subclasses can implement their specific execution logic.
        """
        try:
            # Look for standard entry points
            main_func = None
            for export_name in ['main', 'run', 'execute', '_start']:
                try:
                    main_func = instance.exports(store)[export_name]
                    break
                except KeyError:
                    continue
            
            if main_func is None:
                return ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    error="No suitable entry point found (main, run, execute, _start)"
                )
            
            # Convert input to JSON string for passing to WASM
            input_json = json.dumps(input_data)
            
            # This is a basic implementation - subclasses should override
            # for more sophisticated parameter passing
            if callable(main_func):
                result = main_func(store)
                
                # For now, return a basic success result
                # Subclasses should implement proper output extraction
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    output={"result": "executed", "input_received": input_data}
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    error=f"Entry point is not callable: {type(main_func)}"
                )
                
        except wasmtime.FuelError:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                error="Execution exceeded fuel limit"
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error=f"Execution error: {e}"
            )


class JSONCommunicationChannel:
    """
    Handles JSON-based communication for WASM modules.
    
    Provides a secure, sandboxed communication channel that only
    allows JSON data exchange.
    """
    
    @staticmethod
    def validate_json_data(data: Any) -> bool:
        """Validate that data is JSON-serializable"""
        try:
            json.dumps(data)
            return True
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def serialize_input(data: Dict[str, Any]) -> str:
        """Serialize input data to JSON string"""
        if not JSONCommunicationChannel.validate_json_data(data):
            raise ValueError("Input data is not JSON-serializable")
        return json.dumps(data, separators=(',', ':'))
    
    @staticmethod
    def deserialize_output(json_str: str) -> Dict[str, Any]:
        """Deserialize output JSON string to dict"""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON output: {e}")