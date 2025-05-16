import pygame
import constants
from elements import Tree
import random
import os

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.trees = [Tree(random.randint(0, width - 40),
        random.randint(0, height - 40)) for _ in range(10)]

        gastation_path = os.path.join("assets", "img", "objetos", "Pasto.png")
        self.gastation = pygame.image.load(gastation_path).convert()
        self.gastation = pygame.transform.scale(self.gastation, (constants.PASTO, constants.PASTO))

        
    def draw(self, screen):
        for y in range(0, self.height, constants.PASTO):
            for x in range(0, self.width, constants.PASTO):
                screen.blit(self.gastation, (x, y))

        for tree in self.trees:
            tree.draw(screen)