from typing import * # type: ignore
import tempfile
import logging
import sys
import math
import wasmtime

from dataclasses import astuple

from game.puck import State, Config

class BotSandbox:
    def __init__(self, path: str, logger=logging.Logger("dummy")):
        self.path = path
        self.logger = logger
        self._store = wasmtime.Store()
        self._linker = wasmtime.Linker(self._store.engine)
        self._module = wasmtime.Module.from_file(self._store.engine, path)

        action_type = wasmtime.FuncType([wasmtime.ValType.f32(), wasmtime.ValType.f32()], [])

        self._linker.define(self._store, 
                            "env", 
                            "send_action", 
                            wasmtime.Func(self._store, action_type, lambda x_accel, y_accel: self._py_set_action(x_accel, y_accel))
        )

        self._instance = self._linker.instantiate(self._store, self._module)
        self.wasm_init = self._instance.exports(self._store)["init"]
        self.wasm_update = self._instance.exports(self._store)["update"]
        self.action = 0+0j
        
    def init(self, config: Config):
        self.wasm_init(self._store, *astuple(config))

    def update(self, state: State):
        pos = state.pos.real, state.pos.imag
        vel = state.vel.real, state.vel.imag
        enemy_pos = state.enemy_pos.real, state.enemy_pos.imag
        enemy_vel = state.enemy_vel.real, state.enemy_vel.imag
        
        return self.wasm_update(self._store, *pos, *vel, *enemy_pos, *enemy_vel)

    def _py_set_action(self, x_accel: float, y_accel: float):
        if not math.isfinite(x_accel) or not math.isfinite(y_accel):
            return
        
        self.action = complex(x_accel, y_accel)


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
        print(s.init())
