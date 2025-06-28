import pygame
import constants
import os
import json

class Character:
    def __init__(self, x, y):
        self.global_x = x
        self.global_y = y
        self.inventario = [[None, 0] for _ in range(constants.INVENTORY_SLOTS)] # [item_name, quantity]
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
            "inventario": self.inventario, # Ahora es una lista de listas
            "crafting_grid": self.crafting_grid,
            """crafting_qty""": self.crafting_qty
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
            # Cargar el inventario con la nueva estructura
            loaded_inventory = data.get("inventario", [])
            self.inventario = [[None, 0] for _ in range(constants.INVENTORY_SLOTS)]
            for i, item_data in enumerate(loaded_inventory):
                if i < constants.INVENTORY_SLOTS and isinstance(item_data, list) and len(item_data) == 2:
                    self.inventario[i] = item_data
            
            self.crafting_grid = data.get("crafting_grid", [None, None, None, None])
            self.crafting_qty = data.get("crafting_qty", [0, 0, 0, 0])

    def load_item_image(self, filename):
        path = os.path.join("assets", "img", "objetos", filename)
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (40, 40))

    def get_item_quantity(self, item_name):
        # Esta función ya no es tan relevante con la nueva estructura, pero la mantendremos por si acaso
        total_qty = 0
        for item, qty in self.inventario:
            if item == item_name:
                total_qty += qty
        return total_qty

    def add_item_to_inventory(self, item_name, quantity):
        # Intentar apilar en stacks existentes
        for i, (item, qty) in enumerate(self.inventario):
            if item == item_name and qty < constants.MAX_STACK_SIZE:
                space_left = constants.MAX_STACK_SIZE - qty
                add_amount = min(quantity, space_left)
                self.inventario[i][1] += add_amount
                quantity -= add_amount
                if quantity == 0:
                    return True # Todo el item fue añadido
        
        # Si aún quedan items, buscar slots vacíos
        if quantity > 0:
            for i, (item, qty) in enumerate(self.inventario):
                if item is None or qty == 0: # Slot vacío
                    add_amount = min(quantity, constants.MAX_STACK_SIZE)
                    self.inventario[i] = [item_name, add_amount]
                    quantity -= add_amount
                    if quantity == 0:
                        return True # Todo el item fue añadido
        
        if quantity > 0:
            print(f"Inventario lleno, no se pudo añadir {quantity} de {item_name}")
            return False # No se pudo añadir todo
        return True

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
                        self.add_item_to_inventory("madera", 1)
                        print("Has talado un árbol y tienes madera")
                        world.trees.remove(tree)
                else:
                    print("no hay madera en el arbol")
                break
        for stone in world.small_stones[:]:
            if self.is_near(stone):
                if stone.stone > 0:
                    self.add_item_to_inventory("piedra", 1)
                    stone.stone -= 1
                    print("has recogido piedra")
                    if stone.stone == 0:
                        world.small_stones.remove(stone)
                else:
                    print("no hay piedra en la roca")
                break

    def draw_inventory(self, screen, fullscreen=False):
        # Dimensiones y posición del fondo del inventario
        inv_width = 750  # Ancho aumentado
        inv_height = 500 # Alto aumentado
        inv_x = (screen.get_width() - inv_width) // 2
        inv_y = (screen.get_height() - inv_height) // 2

        # Fondo con transparencia y borde
        inv_bg = pygame.Surface((inv_width, inv_height), pygame.SRCALPHA)
        inv_bg.fill((30, 30, 30, 220))  # Fondo más oscuro y transparente
        pygame.draw.rect(inv_bg, (70, 70, 70), (0, 0, inv_width, inv_height), 5, border_radius=15) # Borde más grueso
        screen.blit(inv_bg, (inv_x, inv_y))

        # Título
        font = pygame.font.Font(None, 52) # Fuente un poco más grande
        title = font.render("INVENTARIO", True, (255, 255, 255))
        screen.blit(title, (inv_x + inv_width // 2 - title.get_width() // 2, inv_y + 20))

        # Slots de inventario (ajustados para 20 slots en 5x4)
        slot_size = 60 # Slots un poco más grandes
        margin = 12 # Margen ligeramente mayor
        cols, rows = 5, 4 # 20 slots en total
        
        # Calcular el punto de inicio para centrar los slots de inventario
        inv_slots_total_width = cols * slot_size + (cols - 1) * margin
        inv_slots_total_height = rows * slot_size + (rows - 1) * margin
        start_x_inv = inv_x + (inv_width // 2 - inv_slots_total_width // 2) - 100 # Ajuste para mover a la izquierda
        start_y_inv = inv_y + 80

        # Dibuja los slots y los items del inventario
        self.inv_slot_rects = []
        for i in range(constants.INVENTORY_SLOTS):
            row = i // cols
            col = i % cols
            rect = pygame.Rect(start_x_inv + col * (slot_size + margin), start_y_inv + row * (slot_size + margin), slot_size, slot_size)
            self.inv_slot_rects.append(rect)
            pygame.draw.rect(screen, (100, 100, 100), rect, border_radius=8) # Fondo de slot más oscuro
            pygame.draw.rect(screen, (150, 150, 150), rect, 3, border_radius=8) # Borde de slot más claro y grueso

            item_name, item_qty = self.inventario[i]

            if item_name is not None and item_qty > 0 and not (self.drag_origin == ("inv", i) and self.drag_item is not None):
                img = self.item_images[item_name]
                img_rect = img.get_rect(center=rect.center)
                screen.blit(img, img_rect)
                qty_font = pygame.font.Font(None, 30) # Fuente de cantidad ligeramente más grande
                qty_text = qty_font.render(str(item_qty), True, (255,255,255))
                screen.blit(qty_text, (rect.right - 25, rect.bottom - 28)) # Posición ajustada

        # Área de crafteo (2x2)
        craft_slot_size = 60
        craft_margin = 12
        craft_cols, craft_rows = 2, 2
        
        # Calcular el punto de inicio para centrar los slots de crafteo
        craft_slots_total_width = craft_cols * craft_slot_size + (craft_cols - 1) * craft_margin
        craft_slots_total_height = craft_rows * craft_slot_size + (craft_rows - 1) * craft_margin
        start_x_craft = inv_x + (inv_width // 2 - craft_slots_total_width // 2) + 150 # Ajuste para mover a la derecha
        start_y_craft = inv_y + 120

        self.craft_slot_rects = []
        for i in range(4):
            row = i // 2
            col = i % 2
            rect = pygame.Rect(start_x_craft + col * (craft_slot_size + craft_margin), start_y_craft + row * (craft_slot_size + craft_margin), craft_slot_size, craft_slot_size)
            self.craft_slot_rects.append(rect)
            pygame.draw.rect(screen, (100, 100, 100), rect, border_radius=8)
            pygame.draw.rect(screen, (150, 150, 150), rect, 3, border_radius=8)
            
            item = self.crafting_grid[i]
            qty = self.crafting_qty[i]
            if item is not None and not (self.drag_origin == ("craft", i) and self.drag_item is not None):
                img = self.item_images[item]
                img_rect = img.get_rect(center=rect.center)
                screen.blit(img, img_rect)
                qty_font = pygame.font.Font(None, 30)
                qty_text = qty_font.render(str(qty), True, (255,255,255))
                screen.blit(qty_text, (rect.right - 25, rect.bottom - 28))

        # Flecha y resultado
        arrow_font = pygame.font.Font(None, 60) # Flecha más grande
        arrow = arrow_font.render("→", True, (200,200,200)) # Color más suave
        screen.blit(arrow, (start_x_craft + craft_slots_total_width + 15, start_y_craft + craft_slots_total_height // 2 - 20))
        
        result_rect = pygame.Rect(start_x_craft + craft_slots_total_width + 60, start_y_craft + craft_slots_total_height // 2 - craft_slot_size // 2, craft_slot_size, craft_slot_size)
        pygame.draw.rect(screen, (100, 100, 100), result_rect, border_radius=8)
        pygame.draw.rect(screen, (150, 150, 150), result_rect, 3, border_radius=8)

        # Si estás arrastrando un item, dibújalo en el mouse
        if self.drag_item is not None:
            mx, my = pygame.mouse.get_pos()
            img = self.item_images[self.drag_item]
            img_rect = img.get_rect(center=(mx, my))
            screen.blit(img, img_rect)
            qty_font = pygame.font.Font(None, 30)
            qty_text = qty_font.render(str(self.drag_qty), True, (255,255,255))
            screen.blit(qty_text, (mx + 15, my + 15)) # Posición ajustada para el texto de cantidad

        # Texto para cerrar
        close_font = pygame.font.Font(None, 32) # Fuente ligeramente más grande
        close_text = close_font.render("Presiona 'I' para cerrar", True, (200, 200, 200)) # Color más suave
        screen.blit(close_text, (inv_x + inv_width // 2 - close_text.get_width() // 2, inv_y + inv_height - 40))

    def handle_inventory_event(self, event):
        mx, my = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Click izquierdo (recoger stack completo)
            if event.button == 1:
                # Si no hay item arrastrándose
                if self.drag_item is None:
                    # Intentar recoger de inventario
                    for idx, rect in enumerate(self.inv_slot_rects):
                        if rect.collidepoint(mx, my):
                            item_name, item_qty = self.inventario[idx]
                            if item_name is not None and item_qty > 0:
                                self.drag_item = item_name
                                self.drag_qty = item_qty
                                self.drag_origin = ("inv", idx)
                                self.inventario[idx] = [None, 0] # Vaciar slot de origen
                                return
                    # Intentar recoger de crafting
                    for idx, rect in enumerate(self.craft_slot_rects):
                        if rect.collidepoint(mx, my):
                            item_name = self.crafting_grid[idx]
                            item_qty = self.crafting_qty[idx]
                            if item_name is not None and item_qty > 0:
                                self.drag_item = item_name
                                self.drag_qty = item_qty
                                self.drag_origin = ("craft", idx)
                                self.crafting_grid[idx] = None
                                self.crafting_qty[idx] = 0
                                return
                # Si ya hay un item arrastrándose, intentar soltarlo (manejará en MOUSEBUTTONUP)

            # Click derecho (dividir stack)
            elif event.button == 3:
                # Si no hay item arrastrándose
                if self.drag_item is None:
                    # Intentar recoger la mitad de un stack de inventario
                    for idx, rect in enumerate(self.inv_slot_rects):
                        if rect.collidepoint(mx, my):
                            item_name, item_qty = self.inventario[idx]
                            if item_name is not None and item_qty > 1: # Solo si hay más de 1
                                self.drag_item = item_name
                                self.drag_qty = (item_qty + 1) // 2 # Redondear hacia arriba
                                self.drag_origin = ("inv", idx)
                                self.inventario[idx][1] -= self.drag_qty
                                return
                    # Intentar recoger la mitad de un stack de crafting
                    for idx, rect in enumerate(self.craft_slot_rects):
                        if rect.collidepoint(mx, my):
                            item_name = self.crafting_grid[idx]
                            item_qty = self.crafting_qty[idx]
                            if item_name is not None and item_qty > 1:
                                self.drag_item = item_name
                                self.drag_qty = (item_qty + 1) // 2
                                self.drag_origin = ("craft", idx)
                                self.crafting_qty[idx] -= self.drag_qty
                                return
                # Si ya hay un item arrastrándose, intentar soltar uno (manejará en MOUSEBUTTONUP)

        if event.type == pygame.MOUSEBUTTONUP and self.drag_item is not None:
            mx, my = event.pos
            dropped_in_slot = False

            # Intentar soltar en un slot de inventario
            for idx, rect in enumerate(self.inv_slot_rects):
                if rect.collidepoint(mx, my):
                    target_item, target_qty = self.inventario[idx]

                    # Click izquierdo (soltar stack completo)
                    if event.button == 1:
                        # Si el slot de destino está vacío
                        if target_item is None or target_qty == 0:
                            self.inventario[idx] = [self.drag_item, self.drag_qty]
                            dropped_in_slot = True
                        # Si el slot de destino tiene el mismo item y hay espacio
                        elif target_item == self.drag_item and target_qty < constants.MAX_STACK_SIZE:
                            space_left = constants.MAX_STACK_SIZE - target_qty
                            add_amount = min(self.drag_qty, space_left)
                            self.inventario[idx][1] += add_amount
                            self.drag_qty -= add_amount
                            if self.drag_qty == 0:
                                dropped_in_slot = True
                        # Si el slot de destino tiene un item diferente o está lleno, y el origen es inventario, swap
                        elif self.drag_origin[0] == "inv":
                            original_idx = self.drag_origin[1]
                            # Swap de items
                            self.inventario[original_idx] = [target_item, target_qty]
                            self.inventario[idx] = [self.drag_item, self.drag_qty]
                            dropped_in_slot = True
                    
                    # Click derecho (soltar un solo item)
                    elif event.button == 3:
                        # Si el slot está vacío
                        if target_item is None or target_qty == 0:
                            self.inventario[idx] = [self.drag_item, 1]
                            self.drag_qty -= 1
                            dropped_in_slot = True
                        # Si el slot tiene el mismo item y hay espacio
                        elif target_item == self.drag_item and target_qty < constants.MAX_STACK_SIZE:
                            self.inventario[idx][1] += 1
                            self.drag_qty -= 1
                            dropped_in_slot = True
                    break

            # Si no se soltó en un slot de inventario, intentar soltar en un slot de crafteo
            if not dropped_in_slot:
                for idx, rect in enumerate(self.craft_slot_rects):
                    if rect.collidepoint(mx, my):
                        target_item_craft = self.crafting_grid[idx]
                        target_qty_craft = self.crafting_qty[idx]

                        # Click izquierdo (soltar stack completo)
                        if event.button == 1:
                            # Si el slot de destino está vacío
                            if target_item_craft is None or target_qty_craft == 0:
                                self.crafting_grid[idx] = self.drag_item
                                self.crafting_qty[idx] = self.drag_qty
                                dropped_in_slot = True
                            # Si el slot de destino tiene el mismo item y hay espacio
                            elif target_item_craft == self.drag_item and target_qty_craft < constants.MAX_STACK_SIZE:
                                space_left = constants.MAX_STACK_SIZE - target_qty_craft
                                add_amount = min(self.drag_qty, space_left)
                                self.crafting_qty[idx] += add_amount
                                self.drag_qty -= add_amount
                                if self.drag_qty == 0:
                                    dropped_in_slot = True
                            # Si el slot de destino tiene un item diferente o está lleno, y el origen es crafting, swap
                            elif self.drag_origin[0] == "craft":
                                original_idx = self.drag_origin[1]
                                # Swap de items
                                self.crafting_grid[original_idx] = target_item_craft
                                self.crafting_qty[original_idx] = target_qty_craft
                                self.crafting_grid[idx] = self.drag_item
                                self.crafting_qty[idx] = self.drag_qty
                                dropped_in_slot = True
                        
                        # Click derecho (soltar un solo item)
                        elif event.button == 3:
                            # Si el slot está vacío
                            if target_item_craft is None or target_qty_craft == 0:
                                self.crafting_grid[idx] = self.drag_item
                                self.crafting_qty[idx] = 1
                                self.drag_qty -= 1
                                dropped_in_slot = True
                            # Si el slot tiene el mismo item y hay espacio
                            elif target_item_craft == self.drag_item and target_qty_craft < constants.MAX_STACK_SIZE:
                                self.crafting_qty[idx] += 1
                                self.drag_qty -= 1
                                dropped_in_slot = True
                        break

            # Si no se soltó completamente en ningún slot válido, devolver el item restante a su origen
            if not dropped_in_slot or self.drag_qty > 0:
                if self.drag_origin[0] == "inv":
                    original_idx = self.drag_origin[1]
                    # Si el slot original está vacío, o tiene el mismo item y hay espacio
                    if self.inventario[original_idx][0] is None or \
                       (self.inventario[original_idx][0] == self.drag_item and self.inventario[original_idx][1] < constants.MAX_STACK_SIZE):
                        self.inventario[original_idx][0] = self.drag_item
                        self.inventario[original_idx][1] += self.drag_qty
                    else: # Buscar un slot vacío si el original no es adecuado
                        self.add_item_to_inventory(self.drag_item, self.drag_qty)
                elif self.drag_origin[0] == "craft":
                    original_idx = self.drag_origin[1]
                    # Si el slot original está vacío, o tiene el mismo item y hay espacio
                    if self.crafting_grid[original_idx] is None or \
                       (self.crafting_grid[original_idx] == self.drag_item and self.crafting_qty[original_idx] < constants.MAX_STACK_SIZE):
                        self.crafting_grid[original_idx] = self.drag_item
                        self.crafting_qty[original_idx] += self.drag_qty
                    else: # Buscar un slot vacío en inventario si el original no es adecuado
                        self.add_item_to_inventory(self.drag_item, self.drag_qty)

            # Resetear el estado de arrastre
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

        items = [item_data for item_data in self.inventario if item_data[0] is not None and item_data[1] > 0]
        for idx, (item_name, qty) in enumerate(items[:slots]):
            if item_name in self.item_images: # Añadir esta verificación
                img = self.item_images[item_name]
                rect = pygame.Rect(start_x + idx * (slot_size + margin), y, slot_size, slot_size)
                img_rect = img.get_rect(center=rect.center)
                screen.blit(img, img_rect)
                font = pygame.font.Font(None, 28)
                qty_text = font.render(str(qty), True, (255,255,255))
                screen.blit(qty_text, (rect.right - 22, rect.bottom - 26))