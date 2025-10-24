import pygame

class DialogBox:
    def __init__(self, font, width=1000, height=180):
        self.font = font
        self.rect = pygame.Rect(140, 500, width, height)
        self.active = False
        self.text = ""
        self.alpha = 255

    def show(self, text):
        self.text = text
        self.active = True
        self.alpha = 255

    def hide(self):
        self.active = False

    def draw(self, screen):
        if not self.active:
            return
        box_surface = pygame.Surface((self.rect.width, self.rect.height))
        box_surface.set_alpha(self.alpha)
        box_surface.fill((25, 25, 25))
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=8)
        screen.blit(box_surface, self.rect)

        words = self.text.split(" ")
        lines, current = [], ""
        for w in words:
            test = current + w + " "
            if self.font.size(test)[0] < self.rect.width - 40:
                current = test
            else:
                lines.append(current)
                current = w + " "
        lines.append(current)

        y = self.rect.y + 20
        for line in lines:
            surf = self.font.render(line, True, (255,255,255))
            screen.blit(surf, (self.rect.x + 20, y))
            y += 30

