import pygame
import constants
from elements import Tree, SmallStone
import random
import os
import math

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.trees = []
        self.small_stones = []

        # Generar árboles evitando superposición
        for _ in range(10):
            while True:
                x = random.randint(0, width - constants.ARBOL)
                y = random.randint(0, height - constants.ARBOL)
                if not any(self.distance(x, y, t.x, t.y) < constants.ARBOL for t in self.trees):
                    self.trees.append(Tree(x, y))
                    break

        # Generar piedras evitando superposición y que estén muy pegadas
        for _ in range(20):
            while True:
                x = random.randint(0, width - constants.PIEDRA)
                y = random.randint(0, height - constants.PIEDRA)
                if (not any(self.distance(x, y, s.x, s.y) < constants.PIEDRA*1.5 for s in self.small_stones) and
                    not any(self.distance(x, y, t.x, t.y) < constants.ARBOL for t in self.trees)):
                    self.small_stones.append(SmallStone(x, y))
                    break

        gastation_path = os.path.join("assets", "img", "objetos", "Pasto.png")
        self.gastation = pygame.image.load(gastation_path).convert()
        self.gastation = pygame.transform.scale(self.gastation, (constants.PASTO, constants.PASTO))

    def distance(self, x1, y1, x2, y2):
        return math.hypot(x2 - x1, y2 - y1)

    def draw(self, screen):
        for y in range(0, self.height, constants.PASTO):
            for x in range(0, self.width, constants.PASTO):
                screen.blit(self.gastation, (x, y))

        for stone in self.small_stones:
            stone.draw(screen)

        for tree in self.trees:
            tree.draw(screen)

    def draw_inventory(self, screen, character):
        font = pygame.font.Font(None, 36)
        wood_text = font.render(f"Madera: {character.inventario['madera']}", True, (255, 255, 255))

        stone_text = font.render(f"Piedra: {character.inventario['piedra']}", True, (255, 255, 255))
        screen.blit(wood_text, (10, 10))
        screen.blit(stone_text, (10, 50))
