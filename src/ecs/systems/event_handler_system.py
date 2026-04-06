from helpers.constants import PLAYER_SPEED
from ecs.entity_manager import EntityManager
from helpers.game_state_manager import GameStateManager
import pygame
from pygame.locals import QUIT, K_w, K_s, K_a, K_d, K_q, K_k
from sys import exit
from abc import ABC, abstractmethod


class EventHandlerSystem(ABC):
    def __init__(self, entity_manager: EntityManager, state_manager: GameStateManager):
        self.entity_manager = entity_manager

    @abstractmethod
    def process_events(self, events):
        """Processes input events and updates player velocity"""
        raise NotImplementedError("Subclasses must implement this method")

class WorldEventHandlerSystem(EventHandlerSystem):
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
        
class BattleEventHandlerSystem(EventHandlerSystem):
    def __init__(self, entity_manager: EntityManager, state_manager: GameStateManager):
        self.entity_manager = entity_manager
        self.state_manager = state_manager
        self.last_attack_time = 0
        self.attack_cooldown = 0.5  # 0.5 second cooldown between attacks

    def process_events(self, events):
        """Processes input events during battle (for testing, allows insta-kill enemy)"""
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()
        if keys[K_q]:
            pygame.quit()
            exit()
        
        # Insta-kill enemy for testing (with cooldown):
        if keys[K_k]:
            import time
            current_time = time.time()
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.last_attack_time = current_time
                current_enemy_id = self.state_manager.get_current_enemy()
                if current_enemy_id:
                    enemy = self.entity_manager.get_entity_by_id(current_enemy_id)
                    if enemy and "hp" in enemy:
                        enemy["hp"].take_damage(10)
                        if not enemy["hp"].is_alive():
                            self.entity_manager.delete_entity(current_enemy_id)
                            self.state_manager.change_state("PLAYING")