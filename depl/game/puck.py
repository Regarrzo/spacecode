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
        self.players: Dict[Puck, Puck] = players
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
            p.vel *= config.damping ** dt

        # apply actions
        for puck, action in actions.items():
            self.apply_action(dt, puck, action)
    
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

config = Config()
scale = WIDTH / (2 * config.boundary_radius)  # map radius 1.0 → screen
center = WIDTH // 2, HEIGHT // 2

# Create two pucks
p1 = Puck(pos=complex(-0.3, 0), vel=0+0j)
p2 = Puck(pos=complex(0.3, 0), vel=0+0j)
p3 = Puck(pos=complex(0, 0.3))
env = Environment([p1, p2, p3], config)

def to_screen(pos: complex) -> tuple[int, int]:
    return int(center[0] + pos.real * scale), int(center[1] - pos.imag * scale)

def draw():
    screen.fill((30, 30, 30))
    # boundary circle
    pygame.draw.circle(screen, (200, 200, 200), center, int(config.boundary_radius * scale), 2)
    # pucks
    for puck, color in [(p1, (200, 50, 50)), (p2, (50, 50, 200)), (p3, (255, 50, 200))]:
        pygame.draw.circle(screen, color, to_screen(puck.pos), int(config.puck_radius * scale))

def get_actions() -> dict[Puck, complex]:
    keys = pygame.key.get_pressed()
    a1 = 0+0j
    a2 = 0+0j

    # WASD for p1
    if keys[pygame.K_w]: a1 += 0+1j
    if keys[pygame.K_s]: a1 += 0-1j
    if keys[pygame.K_a]: a1 += -1+0j
    if keys[pygame.K_d]: a1 += 1+0j

    # Arrows for p2
    if keys[pygame.K_UP]: a2 += 0+1j
    if keys[pygame.K_DOWN]: a2 += 0-1j
    if keys[pygame.K_LEFT]: a2 += -1+0j
    if keys[pygame.K_RIGHT]: a2 += 1+0j

    return {p1: a1, p2: a2}

# --- Main loop ---

if __name__ == "__main__":
    while True:
        dt = clock.tick(60) / 1000.0  # seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        actions = get_actions()
        env.update(dt, actions)
        print(actions)

        draw()
        pygame.display.flip()