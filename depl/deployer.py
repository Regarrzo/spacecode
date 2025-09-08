from typing import * # type: ignore
import tempfile
import logging
import sys
import math
import wasmtime

from dataclasses import astuple
import depl.game.puck
from depl.game.puck import State, Config


class BotSandbox:
    def __init__(self, path: str, logger=logging.Logger("dummy")):
        self.path = path
        self.logger = logger
        self._store = wasmtime.Store()
        self._linker = wasmtime.Linker(self._store.engine)
        self._module = wasmtime.Module.from_file(self._store.engine, path)

        self._linker.define_wasi()

        send_action_type = wasmtime.FuncType([wasmtime.ValType.f32(), wasmtime.ValType.f32()], [])
        
        self._linker.define(self._store, 
                            "env", 
                            "send_action", 
                            wasmtime.Func(self._store, send_action_type, lambda x_accel, y_accel: self._py_set_action(x_accel, y_accel))
        )

        set_color_type = wasmtime.FuncType([wasmtime.ValType.f32(), wasmtime.ValType.f32(), wasmtime.ValType.f32()], [])
        
        self._linker.define(self._store, 
                            "env", 
                            "set_color", 
                            wasmtime.Func(self._store, set_color_type, lambda r, g, b: self._py_set_color(r, g, b))
        )

        self._instance = self._linker.instantiate(self._store, self._module)
        self.wasm_init = self._instance.exports(self._store)["init"]
        self.wasm_update = self._instance.exports(self._store)["update"]
        self.action = 0+0j
        self.color = 1.0, 1.0, 1.0
        
    def init(self, config: Config):
        self.wasm_init(self._store, *astuple(config))

    def update(self, state: State):
        pos = state.pos.real, state.pos.imag
        vel = state.vel.real, state.vel.imag
        enemy_pos = state.enemy_pos.real, state.enemy_pos.imag
        enemy_vel = state.enemy_vel.real, state.enemy_vel.imag
        
        self.wasm_update(self._store, *pos, *vel, *enemy_pos, *enemy_vel)

        return self.action

    def _py_set_action(self, x_accel: float, y_accel: float):
        if not math.isfinite(x_accel) or not math.isfinite(y_accel):
            self.logger.error(f"Bot executed invalid _py_set_action command with {(x_accel, y_accel)}")
            return
            
        self.action = complex(x_accel, y_accel)

    def _py_set_color(self, r: float, g: float, b: float):
        if not math.isfinite(r) or not math.isfinite(g) or not math.isfinite(b):
            self.logger.error(f"Bot executed invalid _py_set_color command with {(r, g, b)}")
            return
        
        if not (0 <= r <= 1 and 0 <= g <= 1 and 0 <= b <= 1):
            self.logger.error(f"Bot executed invalid _py_set_color command with {(r, g, b)}")
            return
        
        self.color = r, g, b


if __name__ == "__main__":
    default_config = Config()
    s = BotSandbox("c/simple_rammer.wasm")
    s.init(default_config)


