
import pygame
from depl.game.puck import Config, Environment, Puck
import sys
from depl.deployer import BotSandbox


def tup_mul(scalar, tup):
    return tuple(scalar * t for t in tup)

if __name__ == "__main__":
    pygame.init()
    WIDTH, HEIGHT = 600, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    config = Config(max_puck_accel=2.0)
    scale = WIDTH / (2 * config.boundary_radius)  # map radius 1.0 → screen
    center = WIDTH // 2, HEIGHT // 2

    # Create two pucks
    player_puck = Puck(pos=complex(-0.3, 0), vel=0+0j)
    ai_puck = Puck(pos=complex(0.3, 0), vel=0+0j)
    env = Environment([player_puck, ai_puck], config)

    s = BotSandbox("c/simple_rammer.wasm")
    s.init(config)

    ai_color = (1.0, 1.0, 1.0)

    def to_screen(pos: complex) -> tuple[int, int]:
        return int(center[0] + pos.real * scale), int(center[1] - pos.imag * scale)

    def draw():
        screen.fill((30, 30, 30))
        # boundary circle
        pygame.draw.circle(screen, (200, 200, 200), center, int(config.boundary_radius * scale), 2)
        # pucks
        for puck, color in [(player_puck, (0, 144, 255)), (ai_puck, tup_mul(255, ai_color))]:
            pygame.draw.circle(screen, color, to_screen(puck.pos), int(config.puck_radius * scale))

    def get_actions() -> dict[Puck, complex]:
        keys = pygame.key.get_pressed()
        a1 = 0+0j
        a2 = 0+0j

        # WASD for player
        if keys[pygame.K_w]: a1 += 0+1j
        if keys[pygame.K_s]: a1 += 0-1j
        if keys[pygame.K_a]: a1 += -1+0j
        if keys[pygame.K_d]: a1 += 1+0j

        # Arrows for p2
        a2 = s.update(env.state(ai_puck))
        print(a2)


        return {player_puck: a1, ai_puck: a2}

    # --- Main loop ---


    while True:
        dt = clock.tick(60) / 1000.0  # seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        actions = get_actions()
        env.update(dt, actions)
        ai_color = s.color

        draw()
        pygame.display.flip()