'''
WARNING: THIS CODE IS AI SLOP
'''

# minimal_pygame_viz.py
# Minimal Pygame visualization for the provided physics/game code.
# Drop this at the bottom of your file (or import your classes and run this).

from lib.sim import *
import pygame
import math
import cmath
from collections import defaultdict

# ---------- CONFIG ----------
WIN_W, WIN_H = 900, 900
FPS = 60
DT = 1.0 / FPS  # simulation timestep (seconds)
BG = (10, 12, 20)
SHIP_COLOR = (240, 240, 255)
PLANET_COLOR = (80, 180, 255)
TEXT_COLOR = (200, 200, 220)

# ---------- HELPERS ----------
def to_screen(p: complex) -> tuple[int, int]:
    # world [0,1]x[0,1] -> screen pixels; y up in world, down on screen
    x = int(p.real * WIN_W)
    y = int((1.0 - p.imag) * WIN_H)
    return x, y

def draw_body_circle(surf, body, color):
    pos_px = to_screen(body.pos)
    # radius is in world units, scale to pixels; clamp to 1px min so it's visible
    r_px = max(1, int(body.radius * WIN_W))
    pygame.draw.circle(surf, color, pos_px, r_px, width=0)

def draw_ship(surf, ship):
    # render a small triangle pointing along ship.rot
    base_r = max(6, int(ship.radius * WIN_W))  # visual size
    tip = ship.pos + ship.rot * (ship.radius * 1.5)
    left = ship.pos + ship.rot * cmath.rect(ship.radius * 1.0, math.radians(150))
    right = ship.pos + ship.rot * cmath.rect(ship.radius * 1.0, math.radians(-150))
    pts = [to_screen(tip), to_screen(left), to_screen(right)]
    pygame.draw.polygon(surf, SHIP_COLOR, pts)

def handle_input(ship) -> dict:
    # Build actions dict expected by Game.step
    pressed = pygame.key.get_pressed()
    actions = defaultdict(set)

    if pressed[pygame.K_w] or pressed[pygame.K_UP]:
        actions[ship].add(Action.FORWARD)
    if pressed[pygame.K_a] or pressed[pygame.K_LEFT]:
        actions[ship].add(Action.LEFT)
    if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]:
        actions[ship].add(Action.RIGHT)
    # K_SPACE could be Action.SHOOT later

    return actions

# ---------- MAIN ----------
def main():
    pygame.init()
    pygame.display.set_caption("Minimal Physics Viz")
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 18)

    cfg = SimConfig(
        gravity_const=1e-5,       # reduce a bit for stability
        ship_thrust_force=0.001, # slightly smaller thrust
        ship_torque=0.50,       # a bit more responsive
        ship_vision_reach=0.5,
        seed=None
    )
    game = Game(cfg)

    # Create a controllable ship
    ship = Ship(
        pos=0.25 + 0.25j,
        old_pos=0.25 + 0.25j,
        rot=1 + 0j,
        old_rot=1 + 0j,
        mass=0.01, 
        inertia=0.1,
        radius=0.015
    )
    game.bodies.append(ship)

    # Add a couple of "planets" (massive bodies) for gravity
    planet1 = Body(
        pos=0.75 + 0.75j,
        old_pos=0.75 + 0.75j,
        mass=300.0,
        inertia=10.0,
        radius=0.03
    )
    planet2 = Body(
        pos=0.75 + 0.25j,
        old_pos=0.75 + 0.25j,
        mass=108.0,
        inertia=10.0,
        radius=0.025
    )
    game.bodies.extend([planet1, planet2])

    running = True
    accum = 0.0
    while running:
        # --- events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- sim step (fixed dt) ---
        actions = handle_input(ship)
        game.step(actions, DT)

        # --- render ---
        screen.fill(BG)

        # world border
        pygame.draw.rect(screen, (40, 40, 60), pygame.Rect(0, 0, WIN_W, WIN_H), width=2)

        # draw bodies
        for b in game.bodies:
            if isinstance(b, Ship):
                draw_ship(screen, b)
            else:
                draw_body_circle(screen, b, PLANET_COLOR)

        # HUD
        vel = ship.vel(DT)
        ang = math.degrees(cmath.phase(ship.rot)) % 360.0
        hud_lines = [
            f"FPS: {int(clock.get_fps())}",
            f"Ship pos: ({ship.pos.real:.3f}, {ship.pos.imag:.3f})",
            f"Ship vel: ({vel.real:.3f}, {vel.imag:.3f})",
            f"Ship angle: {ang:6.2f}°",
            "Controls: W/UP thrust, A/LEFT turn left, D/RIGHT turn right",
        ]
        y = 8
        for line in hud_lines:
            txt = font.render(line, True, TEXT_COLOR)
            screen.blit(txt, (8, y))
            y += 18

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
