import pygame
from ui import Button
from dialog import DialogBox

class GameplayState:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font("assets/fonts/m6x11.ttf", 24)

        # UI Buttons
        self.buttons = [
            Button("Use Expired Vegetables", (80, 100), (300, 60), self.font),
            Button("Use Less Meat", (80, 180), (300, 60), self.font),
            Button("Overcharge Customers", (80, 260), (300, 60), self.font),
        ]

        self.dialog = DialogBox(self.font)
        self.black_heart_value = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()

            for btn in self.buttons:
                if btn.is_clicked(event):
                    self.on_button_click(btn.text)

    def on_button_click(self, name):
        if name == "Use Expired Vegetables":
            self.black_heart_value += 1
            self.dialog.show("You secretly used expired vegetables. The customers might notice... (+1 Corruption)")
        elif name == "Use Less Meat":
            self.black_heart_value += 1
            self.dialog.show("You cut down on meat to save costs. The dish looks a bit sad... (+1 Corruption)")
        elif name == "Overcharge Customers":
            self.black_heart_value += 1
            self.dialog.show("You increased the price. Some customers look angry... (+1 Corruption)")

    def update(self):
        pass

    def render(self):
        self.screen.fill((30, 25, 25))
        title = self.font.render(f"Corruption: {self.black_heart_value}", True, (255, 100, 100))
        self.screen.blit(title, (1000, 50))

        for btn in self.buttons:
            btn.draw(self.screen)

        self.dialog.draw(self.screen)
