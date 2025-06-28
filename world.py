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
        self.generated_chunks = set()  # Para saber qué chunks ya tienen objetos

        gastation_path = os.path.join("assets", "img", "objetos", "Pasto.png")
        self.gastation = pygame.image.load(gastation_path).convert()
        self.gastation = pygame.transform.scale(self.gastation, (constants.PASTO, constants.PASTO))

        self.neighbor_index = 0  # Para generar chunks vecinos de a uno por frame

    def distance(self, x1, y1, x2, y2):
        return math.hypot(x2 - x1, y2 - y1)

    def generate_chunk(self, chunk_x, chunk_y):
        if (chunk_x, chunk_y) in self.generated_chunks:
            return
        self.generated_chunks.add((chunk_x, chunk_y))
        # Menos objetos por chunk para evitar lag
        for _ in range(random.randint(1, 2)):
            x = chunk_x * constants.CHUNK_SIZE + random.randint(0, constants.CHUNK_SIZE - constants.ARBOL)
            y = chunk_y * constants.CHUNK_SIZE + random.randint(0, constants.CHUNK_SIZE - constants.ARBOL)
            self.trees.append(Tree(x, y))
        for _ in range(random.randint(1, 2)):
            x = chunk_x * constants.CHUNK_SIZE + random.randint(0, constants.CHUNK_SIZE - constants.PIEDRA)
            y = chunk_y * constants.CHUNK_SIZE + random.randint(0, constants.CHUNK_SIZE - constants.PIEDRA)
            self.small_stones.append(SmallStone(x, y))

    def update_size(self, width, height):
        self.width = width
        self.height = height

    def check_collision(self, new_x, new_y, char_size):
        char_rect = pygame.Rect(new_x - char_size // 2, new_y - char_size // 2, char_size, char_size)
        for obj_list in [self.trees, self.small_stones]:
            for obj in obj_list:
                obj_rect = pygame.Rect(obj.x, obj.y, obj.size, obj.size)
                if char_rect.colliderect(obj_rect):
                    return True
        return False

    def draw(self, screen, character):
        # Genera chunks alrededor del personaje
        cx = character.global_x // constants.CHUNK_SIZE
        cy = character.global_y // constants.CHUNK_SIZE
        for y in range(cy - 1, cy + 2):
            for x in range(cx - 1, cx + 2):
                self.generate_chunk(x, y)

        # Dibuja el pasto en toda la pantalla
        for y in range(0, self.height, constants.PASTO):
            for x in range(0, self.width, constants.PASTO):
                screen.blit(self.gastation, (x, y))

        # Dibuja solo los objetos visibles en la pantalla
        for obj_list in [self.trees, self.small_stones]:
            for obj in obj_list:
                if -obj.size < obj.x - character.global_x + character.x < self.width and \
                   -obj.size < obj.y - character.global_y + character.y < self.height:
                    obj.draw(screen, character)

    def draw_inventory(self, screen, character):
        font = pygame.font.Font(None, 36)
        instruction_text = font.render("Presiona 'E' para interactuar", True, constants.WHITE)
        screen.blit(instruction_text, (20, 20))