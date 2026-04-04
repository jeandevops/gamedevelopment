from helpers.constants import PLAYER_SPEED
from ecs.entity_manager import EntityManager
from helpers.game_state_manager import GameStateManager
import pygame
from pygame.locals import QUIT, K_w, K_s, K_a, K_d, K_q, K_k
from sys import exit

class EventHandlerSystem:
    def __init__(self, entity_manager: EntityManager, state_manager: GameStateManager):
        self.entity_manager = entity_manager
        self.state_manager = state_manager

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

        state = self.state_manager.get_state()

        if state != "PLAYING" and state != "BATTLE_STARTED":
            return
        
        if state == "PLAYING":
            player_velocity = player["velocity"]
            
            # Check which keys are currently pressed
            keys = pygame.key.get_pressed()

            # Reset velocity
            vx = 0
            vy = 0

            # Update velocity based on currently pressed keys
            if keys[K_w]:
                vy = -PLAYER_SPEED
            if keys[K_s]:
                vy = PLAYER_SPEED
            if keys[K_a]:
                vx = -PLAYER_SPEED
            if keys[K_d]:
                vx = PLAYER_SPEED
            if keys[K_q]:
                pygame.quit()
                exit()

            # Set the velocity
            player_velocity.set_velocity(vx, vy)
        
        if state == "BATTLE_STARTED":
            keys = pygame.key.get_pressed()

            if keys[K_q]:
                pygame.quit()
                exit()
            # Insta-kill enemy for testing:
            if keys[K_k]:
                current_enemy_id = self.state_manager.get_current_enemy()
                if current_enemy_id:
                    self.entity_manager.delete_entity(current_enemy_id)
                self.state_manager.change_state("PLAYING")