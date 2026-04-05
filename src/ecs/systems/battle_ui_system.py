from ecs.components.hp import HPComponent
from helpers.constants import UNNARMED_STRIKE_DAMAGE, DEFAULT_CRITICAL_CHANCE
from ecs.entity_manager import EntityManager
import pygame

class BattleUISystem:
    def __init__(self, entity_manager: EntityManager, screen: pygame.Surface):
        self.entity_manager = entity_manager
        self.screen = screen

    def update(self, enemy_id: str) -> None:
        # Get player entity:
        player = self.entity_manager.get_entity_by_id("player")
        if not player:
            raise ValueError("Player entity not found in EntityManager")

        # Get player's health component:
        health_component = player["hp"]
        if not health_component:
            raise ValueError("Health component not found for player entity")

        # Update health bar UI based on player's current HP
        current_hp = health_component.current_hp
        max_hp = health_component.max_hp
        hp_percentage = current_hp / max_hp if max_hp > 0 else 0

        bar_width = 200
        bar_height = 20
        filled_width = int(bar_width * hp_percentage)
        pygame.draw.rect(self.screen, (255, 0, 0), (10, 10, bar_width, bar_height))  # Red background
        pygame.draw.rect(self.screen, (0, 255, 0), (10, 10, filled_width, bar_height))  # Green foreground

        # Display enemy HP bar if enemy is still alive
        enemy = self.entity_manager.get_entity_by_id(enemy_id)

        if not enemy:
            raise ValueError(f"Enemy entity with ID '{enemy_id}' not found in EntityManager")
        
        if not "hp" in enemy:
            raise ValueError(f"Health component not found for enemy entity with ID '{enemy_id}'")
        
        enemy_hp_component = enemy["hp"]
        enemy_current_hp = enemy_hp_component.current_hp
        enemy_max_hp = enemy_hp_component.max_hp
        enemy_hp_percentage = enemy_current_hp / enemy_max_hp if enemy_max_hp > 0 else 0

        enemy_bar_width = 200
        enemy_bar_height = 20
        enemy_filled_width = int(enemy_bar_width * enemy_hp_percentage)
        pygame.draw.rect(self.screen, (255, 0, 0), (10, 40, enemy_bar_width, enemy_bar_height))  # Red background
        pygame.draw.rect(self.screen, (0, 255, 0), (10, 40, enemy_filled_width, enemy_bar_height))  # Green foreground