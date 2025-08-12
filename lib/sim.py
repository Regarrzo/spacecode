'''
Game physics logic and simulation

Some notes:
- Coordinates are all between 0 and 1
- 0,0 is the bottom left corner and 1,1 is the top right corner
'''

from __future__ import annotations
from typing import *
from dataclasses import dataclass
from enum import Enum, auto

import cmath
import itertools

EPS = 1e-5

@dataclass(frozen=True)
class SimConfig:
    gravity_const: float = 1.0
    world_min: complex = 0+0j
    world_max: complex = 1+1j
    ship_thrust_force: float = 0.01
    ship_torque: float = 0.01
    seed: Optional[int] = None

class Action(Enum):
    FORWARD = auto()
    LEFT = auto()
    RIGHT = auto()
    SHOOT = auto()

@dataclass(eq=False)
class Body:
    '''
    Everything that has a position, mass, rotation, rotational velocity, i.e. can be drawn and simulated
    '''
    old_pos: complex = 0+0j
    pos: complex = 0+0j
    force: complex = 0+0j

    # store as normalized complex number
    old_rot: complex = 1+0j
    rot: complex = 1+0j

    # this is stored as a float because storing it as a complex number
    # wouldn't allow it to represent values larger than pi
    torque: float = 0.0
    
    mass: float = 1.0 # if this ever becomes 0 the spirit of Albert Einstein will strike you down personally
    inertia: float = 1.0
    radius: float = 0.0

    # Since we are using verlet integration we don't directly need velocity, here it is anyways if somehow needed
    def vel(self, dt: float):
        return (self.pos - self.old_pos) / dt

    @property
    def accel(self) -> complex:
        return self.force / self.mass
    
    @property
    def rot_accel(self) -> float:
        return self.torque / self.inertia 


class PhysicsSystem:
    def __init__(self, cfg: SimConfig):
        self.cfg: SimConfig = cfg

    def clear_forces(self, body: Body):
        body.force = 0+0j
        body.torque = 0.0

    def intersects(self, a: Body, b: Body) -> bool:
        return abs(b.pos - a.pos) <= a.radius + b.radius
    
    def _rotational_verlet(self, body: Body, dt) -> complex:
        next_rot = body.rot**2 * body.old_rot.conjugate() * cmath.rect(1.0, body.rot_accel * dt**2)
        return next_rot / abs(next_rot) # safeguard against funky floating points. also if this is ever 0, we deserve to crash

    def _positional_verlet(self, body: Body, dt) -> complex:
        return 2 * body.pos - body.old_pos + body.accel * dt**2
    
    def add_force(self, body: Body, force: complex):
        body.force += force

    def add_torque(self, body: Body, torque: float):
        body.torque += torque
    
    def integrate_forces(self, body: Body, dt: float):
        '''
        Integrates all forces over dt and applies forces. Clears all applied forces
        '''
        body.old_pos, body.pos = body.pos, self._positional_verlet(body, dt)
        body.old_rot, body.rot = body.rot, self._rotational_verlet(body, dt)
        self.clear_forces(body)

    def compute_attraction_force_magnitude(self, a: Body, b: Body) -> float:
        return (self.cfg.gravity_const * a.mass + b.mass) / max(abs(b.pos - a.pos), EPS)**2
    
    
class Ship(Body):
    def apply_thrust_force(self, force: float):
        '''
        Applies force in forward direction at the midpoint between old_rot and rot
        '''
        rot_delta = self.rot * self.old_rot.conjugate()
        force_dir = self.old_rot * cmath.sqrt(rot_delta)
        self.force += force * force_dir
    
    def apply_rotational_force(self, torque: float):
        self.torque += torque

    
class Game:
    def __init__(self, cfg: SimConfig = SimConfig()) -> None:
        self.bodies: List[Body] = [] # this could be a set too but list makes it more deterministic
        self.phys = PhysicsSystem(cfg)

    def _process_gravity(self):
        '''
        O(n^2) native implementation
        '''
        for a, b in itertools.combinations(self.bodies, 2):
            force = self.phys.compute_attraction_force_magnitude(a, b)
            self.phys.add_force(a, force * (b.pos - a.pos))
            self.phys.add_force(b, force * (a.pos - b.pos))

    def _process_inputs(self, actions: Dict[Ship, Set[Action]]):
        for ship, action_set in actions.items():
            for action in action_set:
                match action:
                    case Action.FORWARD: ship.apply_thrust_force(self.phys.cfg.ship_thrust_force)
                    case Action.LEFT: ship.apply_rotational_force(self.phys.cfg.ship_torque)
                    case Action.RIGHT: ship.apply_rotational_force(-self.phys.cfg.ship_torque)
                    case Action.SHOOT: pass # TODO
        
    def apply_all(self, dt: float):
        for body in self.bodies:
            self.phys.integrate_forces(body, dt)

    def step(self, actions: Dict[Ship, Set[Action]], dt: float): 
        self._process_inputs(actions)
        self._process_gravity()

        self.apply_all(dt)