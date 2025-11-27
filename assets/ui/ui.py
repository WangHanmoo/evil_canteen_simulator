import pygame

class Button:
    def __init__(self, text, pos, size, font, color=(40, 40, 40), hover=(90, 90, 90)):
        self.text = text
        self.rect = pygame.Rect(pos, size)
        self.font = font
        self.base_color = color
        self.hover_color = hover
        self.clicked = False

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse) else self.base_color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

