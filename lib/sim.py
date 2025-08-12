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


GRAVITATIONAL_CONSTANT = 1.0
EPS = 1e-5

MIN_POS = complex(0.0)
MAX_POS = complex(0.0)

class Action(Enum):
    FORWARD = auto()
    LEFT = auto()
    RIGHT = auto()
    SHOOT = auto()


def spheres_intersect(pos_a: complex, rad_a: float, pos_b: complex, rad_b: float) -> bool:
    return abs(pos_b - pos_a) <= rad_a + rad_b


def attraction_force_between(mass_a: float, mass_b: float, distance: float) -> float:
    arithmetic_safe_distance = max(distance, EPS)
    return (GRAVITATIONAL_CONSTANT * mass_a * mass_b) / arithmetic_safe_distance


def force_to_acceleration(force: float, mass: float):
    return force / mass


def verlet_integrator(old_pos: complex, pos: complex, accel: float, dt: float) -> complex:
    '''
    Performs verlet integration, i.e. determines the next position from the two previous
    positions, velocity and the time step size
    '''
    return 2 * pos - old_pos + accel * dt ** 2


@dataclass
class PhysicsObject:
    '''
    Everything that has a position, velocity, mass, rotation, rotational velocity, i.e. can be drawn and simulated
    '''
    old_pos: complex = complex(0.0, 0.0)
    pos: complex = complex(0.0, 0.0)

    # store as normalized complex number
    rot: complex = complex(1.0, 0.0) 
    rotv : complex = complex(1.0, 0.0) # = 0 rotational velocity

    mass: float = 1.0
    radius: float = 0.0

    def vel(self, dt: float):
        '''
        Since we are using verlet integration we don't directly need velocity, here it is anyways if somehow needed
        '''
        return (self.pos - self.old_pos) / dt

class Ship:
    '''
    Main object of interest
    '''
    def __init__(self, physics_object: PhysicsObject):
        self.physics_object: PhysicsObject = physics_object
        

class Game:
    def __init__(self) -> None:
        pass

    def step(self, dt: float):
        pass