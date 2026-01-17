import pygame
from pygame.locals import QUIT

from sys import exit

from world.map_loader import MapLoader
from world.entity_manager import EntityManager
from systems.render_system import RenderingSystem

pygame.init()
pygame.display.set_caption("World of Tiles")

width, height = 800, 600
screen = pygame.display.set_mode((width, height))


entity_manager = EntityManager()
map_loader = MapLoader()
map_loader.load_map(entity_manager, "forest")

rendering_system = RenderingSystem(screen, entity_manager)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
    
    screen.fill((0, 0, 0))
    rendering_system.render()
    pygame.display.update()