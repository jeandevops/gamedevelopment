from helpers.constants import SPEED
from ecs.entity_manager import EntityManager
import pygame
from pygame.locals import QUIT, K_w, K_s, K_a, K_d

class EventHandlerSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    def process_events(self, events):
        """Processes input events and updates player velocity"""

        for event in events:
            if event.type == QUIT:
                pygame.quit()
                exit()

        # Get player entity
        player = self.entity_manager.get_entity_by_id("player")
        if player is None:
            return
        
        player_velocity = player["velocity"]
        
        # Check which keys are currently pressed
        keys = pygame.key.get_pressed()
        
        # Reset velocity
        vx = 0
        vy = 0
        
        # Update velocity based on currently pressed keys
        if keys[K_w]:
            vy = -SPEED
        if keys[K_s]:
            vy = SPEED
        if keys[K_a]:
            vx = -SPEED
        if keys[K_d]:
            vx = SPEED
        
        # Set the velocity
        player_velocity.set_velocity(vx, vy)