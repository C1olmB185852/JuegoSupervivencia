import pygame
import constants
import os

class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.wood = 5

        image_path = os.path.join("assets", "img", "objetos", "arbol.png")
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (constants.ARBOL, constants.ARBOL))
        self.size = self.image.get_width()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))