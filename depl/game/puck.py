'''
Game physics logic and simulation
'''

from __future__ import annotations
from typing import * # pyright: ignore[reportWildcardImportFromLibrary]
from dataclasses import dataclass, astuple
from enum import Enum, auto
import itertools
import pygame
import sys

EPS = 1e-5

### IF YOU MODIFY THE FIELDS THEN YOU MUST CHANGE BOT.H
### ### ### ### ### ### ### ### ### ### ### ### ### ###
@dataclass
class Config:
    boundary_radius: float = 1.0
    puck_radius: float = 0.1
    max_puck_accel: float = 0.5
    damping: float = 0.8

@dataclass
class State:
    pos: complex
    vel: complex

    # for now for simplicity we only allow one opponent
    enemy_pos: complex
    enemy_vel: complex
### ### ### ### ### ### ### ### ### ### ### ### ### ###


@dataclass(eq=False)
class Puck:
    pos: complex
    vel: complex = 0+0j
    
    def distance_to(self, other: Puck) -> float:
        return abs(other.pos - self.pos)
    
    def get_velocity_after_collision(self, other: Puck) -> complex:
        # normal vector
        n = self.pos - other.pos
        dist = abs(n)
        if dist < EPS:
            return self.vel
        n /= dist

        # relative velocity
        v_rel = self.vel - other.vel
        proj = (v_rel.real * n.real + v_rel.imag * n.imag)  # dot product with normal

        # if moving apart, no collision response
        if proj >= 0:
            return self.vel

        # subtract projection along normal
        return self.vel - proj * n

    
class Environment:
    def __init__(self, players, config=Config()):
        self.players: List = players
        self.config: Config = config


    def get_collisions(self) -> Generator[Tuple[Puck, Puck], None, None]:
        for a, b in itertools.combinations(self.players, 2):
            if a == b:
                continue

            if a.distance_to(b) <= self.config.puck_radius * 2:
                yield a, b

    def apply_action(self, dt: float, puck: Puck, action: complex):
        if abs(action) > self.config.max_puck_accel:
            action /= abs(action)
            action *= self.config.max_puck_accel

        puck.vel += dt * action

    def update(self, dt: float, actions: Dict[Puck, complex]):
        # resolve collisions
        for a, b in self.get_collisions():
           new_a_vel = a.get_velocity_after_collision(b)
           new_b_vel = b.get_velocity_after_collision(a)

           a.vel, b.vel = new_a_vel, new_b_vel
        
        # velocity update
        for p in self.players:
            p.pos += p.vel * dt
            p.vel *= self.config.damping ** dt

        # apply actions
        for puck, action in actions.items():
            self.apply_action(dt, puck, action)
    
    def state(self, perspective: Puck):
        enemies = self.players.copy()
        enemies.remove(perspective)
        assert len(enemies) == 1
        enemy = enemies.pop()
        return State(perspective.pos, perspective.vel, enemy.pos, enemy.vel)
