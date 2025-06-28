import pygame
import constants
import os
import json

class Character:
    def __init__(self, x, y):
        self.global_x = x
        self.global_y = y
        self.inventario = {"madera": 0, "piedra": 0}
        self.crafting_grid = [None, None, None, None]  # 2x2 crafting grid
        self.crafting_qty = [0, 0, 0, 0]
        self.drag_item = None
        self.drag_qty = 0
        self.drag_origin = None  # ("inv", idx) o ("craft", idx)
        image_path = os.path.join("assets", "img", "personaje", "personaje1.png")
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (constants.PERSONAJE, constants.PERSONAJE))
        self.size = self.image.get_width()

        self.item_images = { 
            "madera": self.load_item_image("MaderaCortada.png"),
            "piedra": self.load_item_image("roca.png"),
        }

        pasos_path = os.path.join("assets", "sounds", "Pasos.mp3")
        self.sonido_pasos = pygame.mixer.Sound(pasos_path)
        self.paso_cooldown = 0
        self.paso_channel = None

    def save(self, filename="savegame.json"):
        data = {
            "global_x": self.global_x,
            "global_y": self.global_y,
            "inventario": self.inventario,
            "crafting_grid": self.crafting_grid,
            "crafting_qty": self.crafting_qty
        }
        with open(filename, "w") as f:
            json.dump(data, f)

    def load(self, filename="savegame.json"):
        if not os.path.exists(filename):
            return
        with open(filename, "r") as f:
            data = json.load(f)
            self.global_x = data.get("global_x", self.global_x)
            self.global_y = data.get("global_y", self.global_y)
            self.inventario = data.get("inventario", self.inventario)
            self.crafting_grid = data.get("crafting_grid", [None, None, None, None])
            self.crafting_qty = data.get("crafting_qty", [0, 0, 0, 0])

    def load_item_image(self, filename):
        path = os.path.join("assets", "img", "objetos", filename)
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (40, 40))

    def draw(self, screen, world):
        self.x = screen.get_width() // 2
        self.y = screen.get_height() // 2
        screen.blit(self.image, (self.x, self.y))

    def move(self, dx, dy, world):
        new_x = self.global_x + dx
        new_y = self.global_y + dy

        # Comprueba colisiones antes de mover al personaje
        if not world.check_collision(new_x, new_y, self.size):
            self.global_x = new_x
            self.global_y = new_y
            if self.paso_cooldown <= 0:
                if self.paso_channel is None or not self.paso_channel.get_busy():
                    self.paso_channel = self.sonido_pasos.play()
                self.paso_cooldown = 15

    def stop_steps(self):
        if self.paso_channel is not None and self.paso_channel.get_busy():
            self.paso_channel.stop()

    def update(self):
        if self.paso_cooldown > 0:
            self.paso_cooldown -= 1

    def check_collision(self, x, y, obj):
        return (x < obj.x + obj.size and
                x + self.size > obj.x and
                y < obj.y + obj.size and
                y + self.size > obj.y)

    def is_near(self, obj):
        return (abs(self.global_x - obj.x) <= max(self.size, obj.size) and
                abs(self.global_y - obj.y) <= max(self.size, obj.size))

    def interact(self, world):
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
                break
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
                break

    def draw_inventory(self, screen, fullscreen=False):
        # Fondo central tipo ventana
        inv_width = 600
        inv_height = 340
        inv_x = (screen.get_width() - inv_width) // 2
        if fullscreen:
            inv_y = screen.get_height() - inv_height - 20
        else:
            inv_y = (screen.get_height() - inv_height) // 2
        inv_bg = pygame.Surface((inv_width, inv_height), pygame.SRCALPHA)
        inv_bg.fill((40, 40, 40, 230))
        pygame.draw.rect(inv_bg, (180, 180, 180), (0, 0, inv_width, inv_height), 4, border_radius=10)
        screen.blit(inv_bg, (inv_x, inv_y))

        # Título
        font = pygame.font.Font(None, 48)
        title = font.render("Inventario", True, (255, 255, 255))
        screen.blit(title, (inv_x + inv_width // 2 - title.get_width() // 2, inv_y + 10))

        # Slots de inventario (5x4)
        slot_size = 56
        margin = 10
        cols, rows = 5, 4
        start_x = inv_x + 30
        start_y = inv_y + 70

        # Construir lista de items y cantidades
        items = []
        for item, qty in self.inventario.items():
            if qty > 0:
                items.append((item, qty))
        # Rellenar hasta 20 slots
        while len(items) < 20:
            items.append((None, 0))

        # Dibuja los slots y los items
        self.inv_slot_rects = []
        idx = 0
        for row in range(rows):
            for col in range(cols):
                rect = pygame.Rect(start_x + col * (slot_size + margin), start_y + row * (slot_size + margin), slot_size, slot_size)
                self.inv_slot_rects.append(rect)
                pygame.draw.rect(screen, (180, 180, 180), rect, border_radius=6)
                pygame.draw.rect(screen, (80, 80, 80), rect, 2, border_radius=6)
                item, qty = items[idx]
                if item is not None and not (self.drag_origin == ("inv", idx) and self.drag_item is not None):
                    img = self.item_images[item]
                    img_rect = img.get_rect(center=rect.center)
                    screen.blit(img, img_rect)
                    qty_font = pygame.font.Font(None, 28)
                    qty_text = qty_font.render(str(qty), True, (255,255,255))
                    screen.blit(qty_text, (rect.right - 22, rect.bottom - 26))
                idx += 1

        # Área de crafteo (2x2)
        craft_x = inv_x + inv_width - 2 * slot_size - margin - 30
        craft_y = inv_y + 110
        self.craft_slot_rects = []
        for i in range(4):
            row = i // 2
            col = i % 2
            rect = pygame.Rect(craft_x + col * (slot_size + margin), craft_y + row * (slot_size + margin), slot_size, slot_size)
            self.craft_slot_rects.append(rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, border_radius=6)
            pygame.draw.rect(screen, (100, 100, 100), rect, 2, border_radius=6)
            item = self.crafting_grid[i]
            qty = self.crafting_qty[i]
            if item is not None and not (self.drag_origin == ("craft", i) and self.drag_item is not None):
                img = self.item_images[item]
                img_rect = img.get_rect(center=rect.center)
                screen.blit(img, img_rect)
                qty_font = pygame.font.Font(None, 28)
                qty_text = qty_font.render(str(qty), True, (255,255,255))
                screen.blit(qty_text, (rect.right - 22, rect.bottom - 26))

        # Flecha y resultado (solo decorativo)
        arrow_font = pygame.font.Font(None, 48)
        arrow = arrow_font.render("→", True, (255,255,255))
        screen.blit(arrow, (craft_x + 2 * (slot_size + margin) + 10, craft_y + slot_size // 2 - 10))
        result_rect = pygame.Rect(craft_x + 3 * (slot_size + margin) + 10, craft_y + slot_size // 2 - slot_size // 2, slot_size, slot_size)
        pygame.draw.rect(screen, (220, 220, 220), result_rect, border_radius=6)
        pygame.draw.rect(screen, (120, 120, 120), result_rect, 2, border_radius=6)

        # Si estás arrastrando un item, dibújalo en el mouse
        if self.drag_item is not None:
            mx, my = pygame.mouse.get_pos()
            img = self.item_images[self.drag_item]
            img_rect = img.get_rect(center=(mx, my))
            screen.blit(img, img_rect)
            qty_font = pygame.font.Font(None, 28)
            qty_text = qty_font.render(str(self.drag_qty), True, (255,255,255))
            screen.blit(qty_text, (mx + 12, my + 12))

        # Texto para cerrar
        close_font = pygame.font.Font(None, 28)
        close_text = close_font.render("Presiona 'I' para cerrar", True, (255, 255, 255))
        screen.blit(close_text, (inv_x + inv_width // 2 - close_text.get_width() // 2, inv_y + inv_height - 36))

    def handle_inventory_event(self, event):
        # Arrastrar y soltar entre inventario y crafting
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Inventario
            for idx, rect in enumerate(self.inv_slot_rects):
                if rect.collidepoint(mx, my):
                    items = [item for item, qty in self.inventario.items() if qty > 0]
                    # Rellenar hasta 20 slots
                    while len(items) < 20:
                        items.append(None)
                    item = items[idx]
                    if item is not None and self.inventario[item] > 0:
                        self.drag_item = item
                        self.drag_qty = self.inventario[item]
                        self.drag_origin = ("inv", idx)
                        break
            # Crafting
            for idx, rect in enumerate(self.craft_slot_rects):
                if rect.collidepoint(mx, my):
                    item = self.crafting_grid[idx]
                    qty = self.crafting_qty[idx]
                    if item is not None and qty > 0:
                        self.drag_item = item
                        self.drag_qty = qty
                        self.drag_origin = ("craft", idx)
                        break

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.drag_item is not None:
            mx, my = event.pos
            # Inventario
            for idx, rect in enumerate(self.inv_slot_rects):
                if rect.collidepoint(mx, my):
                    # Si venía del crafting, mueve a inventario
                    if self.drag_origin and self.drag_origin[0] == "craft":
                        cidx = self.drag_origin[1]
                        # Suma al inventario
                        self.inventario[self.drag_item] = self.inventario.get(self.drag_item, 0) + self.drag_qty
                        # Borra del crafting
                        self.crafting_grid[cidx] = None
                        self.crafting_qty[cidx] = 0
                    # Si venía del inventario, no hace nada (o podrías implementar swap)
                    self.drag_item = None
                    self.drag_qty = 0
                    self.drag_origin = None
                    return
            # Crafting
            for idx, rect in enumerate(self.craft_slot_rects):
                if rect.collidepoint(mx, my):
                    # Si venía del inventario, mueve a crafting
                    if self.drag_origin and self.drag_origin[0] == "inv":
                        # Solo permite poner si está vacío o es el mismo item
                        if self.crafting_grid[idx] is None:
                            self.crafting_grid[idx] = self.drag_item
                            self.crafting_qty[idx] = self.drag_qty
                            self.inventario[self.drag_item] -= self.drag_qty
                            if self.inventario[self.drag_item] <= 0:
                                del self.inventario[self.drag_item]
                    # Si venía del crafting, swap
                    elif self.drag_origin and self.drag_origin[0] == "craft":
                        oidx = self.drag_origin[1]
                        # Swap entre slots de crafting
                        if idx != oidx:
                            self.crafting_grid[oidx], self.crafting_grid[idx] = self.crafting_grid[idx], self.crafting_grid[oidx]
                            self.crafting_qty[oidx], self.crafting_qty[idx] = self.crafting_qty[idx], self.crafting_qty[oidx]
                    self.drag_item = None
                    self.drag_qty = 0
                    self.drag_origin = None
                    return
            # Si sueltas fuera, regresa el item a su origen
            if self.drag_origin:
                if self.drag_origin[0] == "inv":
                    # Nada que hacer, ya está en inventario
                    pass
                elif self.drag_origin[0] == "craft":
                    idx = self.drag_origin[1]
                    self.inventario[self.drag_item] = self.inventario.get(self.drag_item, 0) + self.drag_qty
                    self.crafting_grid[idx] = None
                    self.crafting_qty[idx] = 0
            self.drag_item = None
            self.drag_qty = 0
            self.drag_origin = None

    def draw_hotbar(self, screen):
        slots = 10
        slot_size = 48
        margin = 8
        total_width = slots * slot_size + (slots - 1) * margin
        start_x = (screen.get_width() - total_width) // 2
        y = screen.get_height() - slot_size - 20

        bar_bg = pygame.Surface((total_width + 16, slot_size + 16), pygame.SRCALPHA)
        bar_bg.fill((0, 0, 0, 120))
        screen.blit(bar_bg, (start_x - 8, y - 8))

        for i in range(slots):
            rect = pygame.Rect(start_x + i * (slot_size + margin), y, slot_size, slot_size)
            pygame.draw.rect(screen, (180, 180, 180), rect, border_radius=6)
            pygame.draw.rect(screen, (80, 80, 80), rect, 2, border_radius=6)

        items = [item for item, qty in self.inventario.items() if qty > 0]
        for idx, item in enumerate(items[:slots]):
            img = self.item_images[item]
            rect = pygame.Rect(start_x + idx * (slot_size + margin), y, slot_size, slot_size)
            img_rect = img.get_rect(center=rect.center)
            screen.blit(img, img_rect)
            font = pygame.font.Font(None, 28)
            qty = self.inventario[item]
            qty_text = font.render(str(qty), True, (255,255,255))
            screen.blit(qty_text, (rect.right - 22, rect.bottom - 26))