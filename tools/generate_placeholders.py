import os
import pygame

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'ui')
os.makedirs(OUTPUT_DIR, exist_ok=True)

pygame.init()

def rounded_rect(surface, rect, color, radius=12):
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def make_image(name, size, bg_color, text_color=(240,240,240), fontsize=32):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    # subtle background
    surf.fill((0,0,0,0))
    rounded_rect(surf, (0,0,size[0], size[1]), bg_color, radius=18)
    # decorative inner shadow band
    try:
        band = pygame.Surface((size[0]-40, 8), pygame.SRCALPHA)
        band.fill((0,0,0,40))
        surf.blit(band, (20, size[1] - 28))
    except Exception:
        pass

    try:
        font = pygame.font.SysFont('Segoe UI', fontsize, bold=True)
    except Exception:
        font = pygame.font.Font(None, fontsize)
    label = name.replace('_', ' ')
    txt = font.render(label, True, text_color)
    rect = txt.get_rect(center=(size[0]//2, size[1]//2))
    surf.blit(txt, rect)
    # outline
    pygame.draw.rect(surf, (20,20,20,120), (0,0,size[0],size[1]), width=2, border_radius=18)
    path = os.path.join(OUTPUT_DIR, name + '.png')
    pygame.image.save(surf, path)
    print('Saved', path)


# nicer definitions: (filename without ext, size, bg color)
items = [
    ('PICTURE_background', (1280, 720), (40, 38, 48)),
    ('PICTURE_background2', (1280, 720), (60, 48, 58)),
    ('PICTURE_background3', (1280, 720), (48, 60, 58)),
    ('PICTURE_figure', (300, 300), (120, 90, 90)),
    ('PICTURE_button1', (360, 64), (70, 95, 160)),
    ('PICTURE_button2', (360, 64), (160, 95, 70)),
    ('PICTURE_text box', (800, 200), (26, 26, 28)),
]

for name, size, color in items:
    make_image(name, size, color)

pygame.quit()
print('All placeholders generated.')
