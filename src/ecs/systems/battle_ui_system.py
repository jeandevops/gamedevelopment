from ecs.entity_manager import EntityManager
import pygame

class BattleUISystem:
    def __init__(self, entity_manager: EntityManager, screen: pygame.Surface):
        self.entity_manager = entity_manager
        self.screen = screen
        self.original_player_images = None
        self.original_enemy_images = None

    def update(self, enemy_id: str) -> None:
        # Get player entity:
        player = self.entity_manager.get_entity_by_id("player")
        if not player:
            raise ValueError("Player entity not found in EntityManager")

        # Get player's health component:
        health_component = player["hp"]
        if not health_component:
            raise ValueError("Health component not found for player entity")

        # Get enemy hp hud entity:
        enemy_hud_entity = self.entity_manager.get_entity_by_id(f"hp_hud_{enemy_id}")
        if not enemy_hud_entity:
            raise ValueError(f"Enemy HP HUD entity with ID 'hp_hud_{enemy_id}' not found in EntityManager")

        player_hud_entity = self.entity_manager.get_entity_by_id("hp_hud_player")
        if not player_hud_entity:
            raise ValueError("Player HP HUD entity with ID 'hp_hud_player' not found in EntityManager")

        # Store original images on first call
        if self.original_player_images is None:
            self.original_player_images = [img.copy() for img in player_hud_entity["animated_sprite"].sprite.images]
        if self.original_enemy_images is None:
            self.original_enemy_images = [img.copy() for img in enemy_hud_entity["animated_sprite"].sprite.images]

        # Update health bar UI based on player's current HP
        current_hp = health_component.current_hp
        max_hp = health_component.max_hp
        hp_percentage = current_hp / max_hp if max_hp > 0 else 0

        bar_width = 96
        bar_height = 32
        filled_width = int(bar_width * hp_percentage)

        # Crop player HP bar (show only the filled portion from left)
        for i, original_image in enumerate(self.original_player_images):
            if filled_width > 0:
                cropped = original_image.subsurface((0, 0, filled_width, bar_height))
            else:
                # If HP is 0, show empty surface
                cropped = pygame.Surface((0, bar_height))
            player_hud_entity["animated_sprite"].sprite.images[i] = cropped

        # Display enemy HP bar if enemy is still alive
        enemy = self.entity_manager.get_entity_by_id(enemy_id)

        if not enemy:
            return
        
        if not "hp" in enemy:
            raise ValueError(f"Health component not found for enemy entity with ID '{enemy_id}'")
        
        enemy_hp_component = enemy["hp"]
        enemy_current_hp = enemy_hp_component.current_hp
        enemy_max_hp = enemy_hp_component.max_hp
        enemy_hp_percentage = enemy_current_hp / enemy_max_hp if enemy_max_hp > 0 else 0

        enemy_bar_width = 96
        enemy_bar_height = 32
        enemy_filled_width = int(enemy_bar_width * enemy_hp_percentage)
        
        # Crop enemy HP bar (show only the filled portion from left)
        for i, original_image in enumerate(self.original_enemy_images):
            if enemy_filled_width > 0:
                cropped = original_image.subsurface((0, 0, enemy_filled_width, enemy_bar_height))
            else:
                # If HP is 0, show empty surface
                cropped = pygame.Surface((0, enemy_bar_height))
            enemy_hud_entity["animated_sprite"].sprite.images[i] = cropped