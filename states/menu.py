import pygame, sys
from config import *

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font("assets/fonts/m6x11.ttf", 60)
        self.options = ["Start Game", "Quit"]
        self.selected = 0

    def draw(self):
        self.screen.fill((20, 20, 20))
        title = self.font.render("Evil Canteen Simulator", True, (255, 200, 50))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))

        for i, option in enumerate(self.options):
            color = (255,255,255) if i == self.selected else (120,120,120)
            text = self.font.render(option, True, color)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 350 + i*80))

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN: self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.selected == 0:
                        return "dialog"
                    elif self.selected == 1:
                        pygame.quit(); sys.exit()

        self.draw()
        return None
