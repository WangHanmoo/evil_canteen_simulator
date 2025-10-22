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
    clock = pygame.time.Clock()
    current_state = Menu(SCREEN)

    # Main loop
    while True:
        next_state = current_state.run()
        if next_state == "QUIT":
            pygame.quit()
            sys.exit()
        elif next_state == "GAME":
            # later: import gameplay state
            pass
        clock.tick(60)

if __name__ == "__main__":
    main()
