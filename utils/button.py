import pygame

class Button:
    def __init__(self, x, y, w, h, text, font, color=(80,80,200), hover_color=(120,120,255), radius=12):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.default_color = color
        self.hover_color = hover_color
        self.color = self.default_color
        self.radius = radius
        self.disabled = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=self.radius)
        txt = self.font.render(self.text, True, (255,255,255))
        txt_r = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_r)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos) and (not self.disabled)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and not self.disabled:
            if self.rect.collidepoint(event.pos):
                return True
        return False

