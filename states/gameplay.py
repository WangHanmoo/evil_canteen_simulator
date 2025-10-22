import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Evil Canteen Simulator")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 30, 30)
GRAY = (180, 180, 180)

# Font
font = pygame.font.SysFont("arial", 28)

# Game variables
money = 100
evil_score = 0
day = 1

# Food events (name, effect on evil_score, effect on money)
events = [
    ("Use cheaper oil", 5, 10),
    ("Reuse yesterday's leftovers", 10, 20),
    ("Add extra salt to hide the taste", 3, 5),
    ("Ignore customer complaint", 8, 15),
    ("Fake good reviews online", 12, 25),
    ("Serve cold rice", 6, 10),
    ("Buy low-quality meat", 15, 30),
    ("Raise price secretly", 10, 20),
    ("Cockroach in the soup", 25, 40),
    ("Report student who posted bad review", 18, 35)
]

# Game loop
def gameplay():
    global money, evil_score, day
    clock = pygame.time.Clock()

    running = True
    while running:
        screen.fill((240, 235, 220))

        # Draw stats
        stats_text = font.render(f"Day: {day}   Money: ${money}   Evil Score: {evil_score}", True, BLACK)
        screen.blit(stats_text, (50, 40))

        # Display random event
        event = random.choice(events)
        event_text = font.render(f"Event: {event[0]}", True, BLACK)
        screen.blit(event_text, (50, 150))

        # Buttons
        yes_rect = pygame.Rect(150, 300, 180, 80)
        no_rect = pygame.Rect(470, 300, 180, 80)

        pygame.draw.rect(screen, RED, yes_rect, border_radius=12)
        pygame.draw.rect(screen, GRAY, no_rect, border_radius=12)

        yes_text = font.render("Do it", True, WHITE)
        no_text = font.render("Skip", True, WHITE)
        screen.blit(yes_text, (yes_rect.x + 50, yes_rect.y + 25))
        screen.blit(no_text, (no_rect.x + 60, no_rect.y + 25))

        pygame.display.flip()

        # Event handling
        for event_handler in pygame.event.get():
            if event_handler.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event_handler.type == pygame.MOUSEBUTTONDOWN:
                if yes_rect.collidepoint(event_handler.pos):
                    money += event[2]
                    evil_score += event[1]
                    day += 1
                elif no_rect.collidepoint(event_handler.pos):
                    day += 1

        # End condition
        if evil_score >= 100:
            end_screen(True)
            running = False
        elif day > 10:
            end_screen(False)
            running = False

        clock.tick(30)


def end_screen(evil_win):
    screen.fill((0, 0, 0))
    if evil_win:
        msg = "You became the most evil canteen ever!"
    else:
        msg = "Semester ends... The canteen survived another term."

    text = font.render(msg, True, WHITE)
    screen.blit(text, (100, 250))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    gameplay()
