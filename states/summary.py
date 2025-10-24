import pygame, sys
from config import *

class Summary:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font("assets/fonts/m6x11.ttf", 50)
        self.small = pygame.font.Font("assets/fonts/m6x11.ttf", 30)
        self.timer = 0

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return "menu"

        self.screen.fill((15, 15, 15))
        title = self.font.render("Daily Summary", True, (255, 200, 100))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
        tip = self.small.render("Click anywhere to return to Menu", True, (200,200,200))
        self.screen.blit(tip, (SCREEN_WIDTH//2 - tip.get_width()//2, 400))
        return None
