import pygame
import constants
import os

class Character:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.inventario = {"madera": 0}
        image_path = os.path.join("assets", "img", "personaje", "personaje11.png")
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (constants.PERSONAJE, constants.PERSONAJE))
        self.size = self.image.get_width()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.x = max(0, min(self.x, constants.WIDTH - self.size))
        self.y = max(0, min(self.y, constants.HEIGHT - self.size))
