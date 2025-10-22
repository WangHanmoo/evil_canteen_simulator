"""
Evil Canteen Simulator
----------------------
Major redesign: project restructured and rewritten around new concept.
Previous direction deprecated; now focuses on satire and black humor gameplay.

Author: Wang Hanmoo
Date: 2025-10-22
"""

import pygame
import sys
from states.menu import Menu

# Initialize pygame
pygame.init()

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Evil Canteen Simulator")

# Icon (optional)
try:
    icon = pygame.image.load("assets/images/icon.png")
    pygame.display.set_icon(icon)
except:
    pass

# Game state manager
def main():
    from states.gameplay import Gameplay  # ✅ 只需在函数内引入，避免循环引用
    clock = pygame.time.Clock()
    current_state = Menu(SCREEN)

    while True:
        next_state = current_state.run()

        if next_state == "QUIT":
            pygame.quit()
            sys.exit()
        elif next_state == "GAME":
            current_state = Gameplay(SCREEN)
        elif next_state in ["ENDING_EVIL", "ENDING_SHUTDOWN"]:
            # Simple ending display
            SCREEN.fill((0, 0, 0))
            font = pygame.font.Font(None, 60)
            text = "You became the most corrupt canteen!" if next_state == "ENDING_EVIL" else "The canteen was shut down!"
            label = font.render(text, True, (255, 0, 0))
            SCREEN.blit(label, (100, 250))
            pygame.display.flip()
            pygame.time.wait(4000)
            current_state = Menu(SCREEN)

        clock.tick(60)

