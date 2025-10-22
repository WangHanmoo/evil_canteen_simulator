import pygame
import sys
from utils.button import Button

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.bg = pygame.image.load("assets/images/title_bg.png")
        self.font = pygame.font.Font("assets/fonts/pixel_font.ttf", 64)
        self.title_text = self.font.render("EVIL CANTEEN SIMULATOR", True, (230, 230, 230))
        self.buttons = [
            Button(300, 350, 200, 60, "START", (0, 200, 0), (0, 255, 0)),
            Button(300, 430, 200, 60, "QUIT", (200, 0, 0), (255, 0, 0))
        ]
        try:
            pygame.mixer.music.load("assets/sounds/bgm_title.mp3")
            pygame.mixer.music.play(-1)
        except:
            pass

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            for button in self.buttons:
                if button.is_hovered(mouse_pos):
                    button.color = button.hover_color
                    if mouse_pressed[0]:
                        if button.text == "START":
                            return "GAME"
                        elif button.text == "QUIT":
                            return "QUIT"
                else:
                    button.color = button.default_color

            # Draw
            self.screen.blit(self.bg, (0, 0))
            self.screen.blit(self.title_text, (60, 150))
            for button in self.buttons:
                button.draw(self.screen)

            pygame.display.flip()
