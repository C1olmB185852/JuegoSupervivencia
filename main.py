import pygame
import sys
import constants
from character import Character
from world import World

pygame.init()

# Configuración inicial de la ventana en pantalla completa
fullscreen = True
ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Mi Ventana")

def main():
    global ventana, fullscreen
    clock = pygame.time.Clock()
    
    # El mundo se inicializa con las dimensiones de la pantalla completa
    world = World(ventana.get_width(), ventana.get_height())
    
    character = Character(0, 0)
    character.load()  # Cargar partida al iniciar
    show_inventory = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                character.save()  # Guardar partida al salir
                pygame.quit()
                sys.exit()
            if show_inventory:
                character.handle_inventory_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    character.interact(world)
                if event.key == pygame.K_i:
                    show_inventory = not show_inventory
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        ventana = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
                    world.update_size(ventana.get_width(), ventana.get_height())
                    pygame.display.set_caption("Mi Ventana")

        keys = pygame.key.get_pressed()
        moving = False
        if not show_inventory:  # Solo moverse si el inventario está cerrado
            if keys[pygame.K_a]:
                character.move(-5, 0, world)
                moving = True
            if keys[pygame.K_d]:
                character.move(5, 0, world)
                moving = True
            if keys[pygame.K_w]:
                character.move(0, -5, world)
                moving = True
            if keys[pygame.K_s]:
                character.move(0, 5, world)
                moving = True

            if not moving:
                character.stop_steps()

        character.update()  # Actualiza el cooldown del sonido de pasos

        world.draw(ventana, character)
        character.draw(ventana, world)
        character.draw_hotbar(ventana)  # Dibuja la barra de inventario tipo Minecraft

        if show_inventory:
            character.draw_inventory(ventana, fullscreen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()