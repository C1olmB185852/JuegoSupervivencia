import pygame
import sys
import constants
from character import Character
from world import World    

pygame.init()

ventana = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
pygame.display.set_caption("Mi Ventana")

def main():
    clock = pygame.time.Clock()
    world = World(constants.WIDTH, constants.HEIGHT)
    character = Character(constants.WIDTH // 2, constants.HEIGHT // 2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            character.move(-5, 0)
        if keys[pygame.K_RIGHT]:
            character.move(5, 0)
        if keys[pygame.K_UP]:
            character.move(0, -5)
        if keys[pygame.K_DOWN]:
            character.move(0, 5)

        world.draw(ventana)
        character.draw(ventana)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()