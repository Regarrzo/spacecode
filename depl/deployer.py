from typing import * # type: ignore
import tempfile
import logging
import sys

import wasmtime

class BotSandbox:
    def __init__(self, path: str, logger=logging.Logger("dummy")):
        self.path = path
        self.logger = logger
        
        self._store = wasmtime.Store()
        self._linker = wasmtime.Linker(self._store.engine)

        self._module = wasmtime.Module.from_file(self._store.engine, path)


        action_type = wasmtime.FuncType([wasmtime.ValType.i32()], [])

        self._linker.define(self._store, 
                            "env", 
                            "send_actions", 
                            wasmtime.Func(self._store, action_type, lambda flags: self._py_set_actions(flags))

        )

        self._instance = self._linker.instantiate(self._store, self._module)
        self.wasm_init = self._instance.exports(self._store)["init"]
        self.wasm_update = self._instance.exports(self._store)["update"]

        self.actions = set()
        



    def init(self):
        self.wasm_init(self._store)
    
    def update(self):
        return self.wasm_update(self._store)

    def info(self):
        self.wasm_info(self._store)

    def _py_set_actions(self, action_flags: int):
        print(action_flags)

        




if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    s = BotSandbox("c/out.wasm")
    while True:
        print(s.update())
