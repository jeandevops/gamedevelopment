import pygame
from pygame.locals import QUIT

from sys import exit

from world.map_loader import MapLoader
from ecs.entity_manager import EntityManager
from ecs.systems.render_system import RenderingSystem

from ecs.components.camera import CameraComponent
from ecs.systems.camera_system import CameraSystem

pygame.init()
pygame.display.set_caption("World of Tiles")

width, height = 800, 600
screen = pygame.display.set_mode((width, height))

entity_manager = EntityManager()
map_loader = MapLoader()
map_loader.load_map(entity_manager, "forest")

camera_component = CameraComponent(x=0, y=0, viewport_width=width, viewport_height=height)
camera_system = CameraSystem(camera_component)

rendering_system = RenderingSystem(screen, entity_manager, camera_component)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
    
    screen.fill((0, 0, 0))
    rendering_system.render()
    # Temporary test position, in the future this would be the player's position
    camera_system.update(target_x=800, target_y=600)
    pygame.display.update()