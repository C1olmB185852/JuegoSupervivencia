import pygame
import constants
import os

class Character:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.inventario = {"madera": 0, "piedra": 0}
        image_path = os.path.join("assets", "img", "personaje", "personaje1.png")
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (constants.PERSONAJE, constants.PERSONAJE))
        self.size = self.image.get_width()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self, dx, dy, world):
        new_x = self.x + dx
        new_y = self.y + dy

        for tree in world.trees:
            if self.check_collision(new_x, new_y, tree):
                return

        self.x = new_x
        self.y = new_y
        self.x = max(0, min(self.x, constants.WIDTH - self.size))
        self.y = max(0, min(self.y, constants.HEIGHT - self.size))

    def check_collision(self, x, y, obj):
        return (x < obj.x + obj.size and
                x + self.size > obj.x and
                y < obj.y + obj.size and
                y + self.size > obj.y)

    def is_near(self, obj):
        return (abs(self.x - obj.x) <= max(self.size, obj.size) and
                abs(self.y - obj.y) <= max(self.size, obj.size))

    def interact(self, world):
        # Eliminar árboles sin madera
        for tree in world.trees[:]:
            if self.is_near(tree):
                if tree.chop():
                    self.inventario["madera"] += 1
                    print("has cortado un arbol y tienes madera")
                    if tree.wood == 0:
                        world.trees.remove(tree)
                else:
                    print("no hay madera en el arbol")

        # Eliminar piedras sin piedra
        for stone in world.small_stones[:]:
            if self.is_near(stone):
                if stone.stone > 0:
                    self.inventario["piedra"] += 1
                    stone.stone -= 1
                    print("has recogido piedra")
                    if stone.stone == 0:
                        world.small_stones.remove(stone)
                else:
                    print("no hay piedra en la roca")