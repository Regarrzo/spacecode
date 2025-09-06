'''
Game physics logic and simulation
'''

from __future__ import annotations
from typing import * # pyright: ignore[reportWildcardImportFromLibrary]
from dataclasses import dataclass
from enum import Enum, auto

import math
import cmath
import itertools
import util

EPS = 1e-5

@dataclass(frozen=True)
class SimConfig:
    gravity_const: float = 1.0
    world_min: complex = 0+0j
    world_max: complex = 1+1j
    ship_thrust_force: float = 0.01
    ship_torque: float = 0.01
    ship_vision_cone: float = math.radians(30) # 30 degrees in either direction
    ship_vision_reach: float = 0.5
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
    
    def relative_angle_to(self, other: Body) -> float:
        diff = other.pos - self.pos

        return cmath.phase(diff / self.rot)
    
    def distance_to(self, other: Body) -> float:
        return abs(other.pos - self.pos)

@dataclass
class BodyView:
    '''
    Observable state of a body for each bot
    '''
    pos: complex
    vel: complex
    rot: complex
    rot_vel: complex
    radius: float
    mass: float

    @staticmethod
    def from_origin_and_body(origin: Body, body: Body):
        '''
        Gives a relative description of body's position from the view of origin
        '''
        pos = body.pos - origin.pos
        vel = body.old_pos - body.pos
        rot = body.rot
        rot_vel = body.rot / body.old_rot
        radius = body.radius
        mass = body.mass

        return BodyView(pos, vel, rot, rot_vel, radius, mass)
        
class PhysicsSystem:
    def __init__(self, cfg: SimConfig):
        self.cfg: SimConfig = cfg

    def clear_forces(self, body: Body):
        body.force = 0+0j
        body.torque = 0.0

    def intersects(self, a: Body, b: Body) -> bool:
        return a.distance_to(b) <= a.radius + b.radius
    
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
        return (self.cfg.gravity_const * a.mass * b.mass) / max(a.distance_to(b), EPS)**2
    
    
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

    def generate_relative_view(self, origin: Ship):
        '''
        Generates a view of the gamestate from ship's perspective to pass on to the bots.
        '''
        bodies_view = {}
        
        for other in self.bodies:
            if origin.distance_to(other) > self.phys.cfg.ship_vision_reach:
                continue

            if origin.relative_angle_to(other) > self.phys.cfg.ship_vision_cone:
                continue

            body_view = BodyView.from_origin_and_body(origin, other)
            bodies_view[type(other)] = body_view

        top_left = self.phys.cfg.world_min
        bottom_right = self.phys.cfg.world_max
        top_right = bottom_right.real + top_left.imag
        bottom_left = top_left.real + bottom_right.imag

        walls = [(top_left, top_right), 
                 (top_right, bottom_right), 
                 (bottom_right, bottom_left), 
                 (bottom_left, top_left)]

        raycasts = [util.raycast(origin.pos, origin.rot, l1, l2) for (l1, l2) in walls]
        raycasts = [cast for cast in raycasts if cast is not None]
        distances = [abs(cast - origin.pos) for cast in raycasts]
        front_wall_view = min(distances)
        
        return bodies_view, front_wall_view
