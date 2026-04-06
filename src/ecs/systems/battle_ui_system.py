from ecs.components.hp import HPComponent
from ecs.entity_manager import EntityManager
import pygame

class BattleUISystem:
    def __init__(self, entity_manager: EntityManager, screen: pygame.Surface):
        self.entity_manager = entity_manager
        self.screen = screen
        self.original_player_images = None
        self.original_enemy_images = None

    def _get_hud_entity(self, entity_id: str) -> dict:
        """Get and validate an HUD entity"""
        hud_entity = self.entity_manager.get_entity_by_id(entity_id)
        if not hud_entity:
            raise ValueError(f"HUD entity with ID '{entity_id}' not found in EntityManager")
        return hud_entity

    def _calculate_hp_percentage(self, hp_component: HPComponent) -> float:
        """Calculate the HP percentage (0.0 to 1.0)"""
        return hp_component.current_hp / hp_component.max_hp if hp_component.max_hp > 0 else 0

    def _crop_hp_bar_images(self, hud_entity: dict, original_images: list, filled_width: int, bar_height: int) -> None:
        """Crop all HP bar frames based on filled_width"""
        for i, original_image in enumerate(original_images):
            if filled_width > 0:
                cropped = original_image.subsurface((0, 0, filled_width, bar_height))
            else:
                cropped = pygame.Surface((0, bar_height))
            hud_entity["animated_sprite"].sprite.images[i] = cropped

    def update(self, enemy_id: str) -> None:
        # Get entities
        player = self.entity_manager.get_entity_by_id("player")
        if not player:
            raise ValueError("Player entity not found in EntityManager")

        player_hud_entity = self._get_hud_entity("hp_hud_player")
        enemy_hud_entity = self._get_hud_entity(f"hp_hud_{enemy_id}")

        # Store original images on first call
        if self.original_player_images is None:
            self.original_player_images = [img.copy() for img in player_hud_entity["animated_sprite"].sprite.images]
        if self.original_enemy_images is None:
            self.original_enemy_images = [img.copy() for img in enemy_hud_entity["animated_sprite"].sprite.images]

        # Update player HP bar
        player_hp = player["hp"]
        player_hp_percentage = self._calculate_hp_percentage(player_hp)
        player_filled_width = int(96 * player_hp_percentage)
        self._crop_hp_bar_images(player_hud_entity, self.original_player_images, player_filled_width, 32)

        # Update enemy HP bar
        enemy = self.entity_manager.get_entity_by_id(enemy_id)
        if not enemy:
            return
        
        if "hp" not in enemy:
            raise ValueError(f"Health component not found for enemy entity with ID '{enemy_id}'")
        
        enemy_hp = enemy["hp"]
        enemy_hp_percentage = self._calculate_hp_percentage(enemy_hp)
        enemy_filled_width = int(96 * enemy_hp_percentage)
        self._crop_hp_bar_images(enemy_hud_entity, self.original_enemy_images, enemy_filled_width, 32)