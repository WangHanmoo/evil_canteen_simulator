import pygame
import random
from utils.button import Button

class Gameplay:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 50)

        # Game values
        self.money = 100
        self.evil = 0
        self.health = 100
        self.day = 1
        self.message = ""

        # Buttons (actions)
        self.actions = [
            Button(80, 420, 200, 60, "Raise Prices", (80, 80, 200), (100, 100, 255)),
            Button(300, 420, 200, 60, "Buy Frozen Food", (80, 160, 80), (100, 200, 100)),
            Button(520,
