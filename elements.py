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

    def draw(self, screen, character):
        # Dibuja el árbol en posición relativa al personaje
        rel_x = self.x - character.global_x + screen.get_width() // 2
        rel_y = self.y - character.global_y + screen.get_height() // 2
        screen.blit(self.image, (rel_x, rel_y))

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

    def draw(self, screen, character):
        # Dibuja la piedra en posición relativa al personaje
        rel_x = self.x - character.global_x + screen.get_width() // 2
        rel_y = self.y - character.global_y + screen.get_height() // 2
        screen.blit(self.image, (rel_x, rel_y))