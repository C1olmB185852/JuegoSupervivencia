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

        self.item_images = { 
            "madera": self.load_item_image("MaderaCortada.png"),
            "piedra": self.load_item_image("roca.png"),
        }

    def load_item_image(self, filename):
        path = os.path.join("assets", "img", "objetos", filename)
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (40, 40))

    def draw(self, screen, world):
        screen.blit(self.image, (self.x, self.y))

        # Mostrar siempre el texto para abrir inventario
        font = pygame.font.Font(None, 32)
        inv_text = font.render("Oprima I para abrir inventario", True, (255, 255, 0))
        screen.blit(inv_text, (20, 10))

        # Mostrar el texto de interacción si está cerca de un árbol o piedra
        show_e = False
        for tree in world.trees:
            if self.is_near(tree):
                show_e = True
                break
        for stone in world.small_stones:
            if self.is_near(stone):
                show_e = True
                break
        if show_e:
            e_text = font.render("Oprima E para picar", True, (0, 255, 0))
            screen.blit(e_text, (20, 40))

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
        # Talar árboles: solo sumar 1 madera cuando el árbol desaparece
        for tree in world.trees[:]:
            if self.is_near(tree):
                if tree.chop():
                    print(f"Le quitaste madera al árbol. Le quedan {tree.wood}")
                    if tree.wood == 0:
                        self.inventario["madera"] += 1
                        print("Has talado un árbol y tienes madera")
                        world.trees.remove(tree)
                else:
                    print("no hay madera en el arbol")
                break  # Solo interactúa con un árbol por vez

        # Eliminar piedras sin piedra (solo 1 por interacción)
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
                break  # Solo recoge 1 piedra por interacción

    def draw_inventory(self, screen):
        background = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
        background.fill((0, 0, 0, 128))
        screen.blit(background, (0, 0))

        font = pygame.font.Font(None, 36)
        title = font.render("Inventario", True, (255, 255, 255))
        screen.blit(title, (constants.WIDTH // 2 - title.get_width() // 2, 10))

        item_font = pygame.font.Font(None, 24)
        y_offset = 80
        for item, quantity in self.inventario.items():
            if quantity > 0: 
                screen.blit(self.item_images[item], (constants.WIDTH // 2 - 50, y_offset))
                text = item_font.render(f"{item.capitalize()}: {quantity}", True, (255, 255, 255))
                screen.blit(text, (constants.WIDTH // 2 + 10, y_offset + 10))
                y_offset += 50

        close_text = item_font.render("Presiona 'I' para cerrar", True, (255, 255, 255))
        screen.blit(close_text, (constants.WIDTH // 2 - close_text.get_width() // 2, constants.HEIGHT - 40))