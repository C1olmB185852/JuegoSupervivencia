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

    def chop(self):
        if self.wood > 0:
            self.wood -= 1
            return True
        return False

class SmallStone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.stone = 1

        small_stone_path = os.path.join("assets", "img", "objetos", "roca.png")
        self.image = pygame.image.load(small_stone_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (constants.PIEDRA, constants.PIEDRA))
        self.size = self.image.get_width()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))