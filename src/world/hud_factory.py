from ecs.entity_manager import EntityManager
from ecs.components.sprite import SpriteComponent
from ecs.components.position import PositionComponent
from ecs.components.dialogue import DialogueComponent
from ecs.components.dialogue import DialogueBoxComponent
from .sprites_maker import AnimatedSprite
from helpers.constants import (
    HUD_SPRITES_PATH,
    HUD_FILE
)
import pygame

class HUDSpritePool:
    def __init__(self):
        """ Initializes the sprite pool with preloaded sprites for different HUD elements """
        hud_sheet = AnimatedSprite.load_sprite_sheet(HUD_SPRITES_PATH, HUD_FILE)
        self.sprites = {
            "hp_bar": AnimatedSprite(
                sprite_sheet=hud_sheet,
                coordinate_x=0,
                coordinate_y=0,
                width=96,
                height=32,
                horizontal_steps=3
            ),
            "enemy_hp_bar": AnimatedSprite(
                sprite_sheet=hud_sheet,
                coordinate_x=0,
                coordinate_y=64,
                width=96,
                height=32,
                horizontal_steps=3
            ),
            "background": AnimatedSprite(
                sprite_sheet=hud_sheet,
                coordinate_x=0,
                coordinate_y=32,
                width=96,
                height=32,
                horizontal_steps=1
            )
        }

class HUDFactory:
    """Factory for creating HUD elements like HP bars"""

    @staticmethod
    def create_battle_hud(entity_manager: EntityManager, enemy_id: str) -> None:       
        """Creates an HP bar sprite component and adds it to the specified entity"""

        hud_background = HUDSpritePool().sprites["background"]
        hp_hud_player = HUDSpritePool().sprites["hp_bar"]
        hp_hud_enemy = HUDSpritePool().sprites["enemy_hp_bar"]

        # Create enemy HP bar:
        enemy_position = entity_manager.get_entity_by_id(enemy_id)
        if not enemy_position:
            raise ValueError(f"Enemy entity {enemy_id} does not have a position component, cannot create HUD")
        
        #@TODO: Hardcoded values
        enemy_x = enemy_position["position"].x + 16 - 48  # Center the HP bar on the enemy (x + half enemy width - half HP bar width)
        enemy_y = enemy_position["position"].y - 32  # Position the HP bar above the enemy (y - HP bar height)
        components = {
            "position": PositionComponent(x=enemy_x, y=enemy_y),
            "animated_sprite": SpriteComponent(sprite=hp_hud_enemy),
            "hud": None  # Add a marker component to identify this entity as a HUD element
        }
        entity_manager.add_entity(f"hp_hud_{enemy_id}", components)

        components = {
            "position": PositionComponent(x=enemy_x, y=enemy_y),
            "animated_sprite": SpriteComponent(sprite=hud_background),
            "hud": None
        }
        entity_manager.add_entity(f"hp_hud_background_{enemy_id}", components)

        # Create player HP bar:
        player_components = entity_manager.get_entity_by_id("player")
        if not player_components:
            raise ValueError("Player entity does not have a position component, cannot create HUD")
        
        player_x = player_components["position"].x + 16 - 48  # Center the HP bar on the player (x + half player width - half HP bar width)
        player_y = player_components["position"].y - 32       # Position the HP bar above the player (y - HP bar height)
        components = {
            "position": PositionComponent(x=player_x, y=player_y),
            "animated_sprite": SpriteComponent(sprite=hp_hud_player),
            "hud": None
        }
        entity_manager.add_entity("hp_hud_player", components)

        components = {
            "position": PositionComponent(x=player_x, y=player_y),
            "animated_sprite": SpriteComponent(sprite=hud_background),
            "hud": None
        }
        entity_manager.add_entity("hp_hud_background_player", components)

    @staticmethod
    def create_dialogue_box(entity_manager: EntityManager, enemy_id: str, box_width: int = 100, box_height: int = 48) -> None:
        """Creates a dialogue box for the enemy entity with dialogue component.
        
        Args:
            entity_manager: The EntityManager instance
            enemy_id: The ID of the enemy entity that has a dialogue component
            box_width: Width of the dialogue box in pixels (default: 100)
            box_height: Height of the dialogue box in pixels (default: 48)
        
        Raises:
            ValueError: If the enemy entity doesn't exist or doesn't have position component
        """
        enemy = entity_manager.get_entity_by_id(enemy_id)
        if not enemy:
            raise ValueError(f"Enemy entity {enemy_id} not found, cannot create dialogue box")
        
        if "position" not in enemy:
            raise ValueError(f"Enemy entity {enemy_id} does not have a position component, cannot create dialogue box")
        
        if "dialogue" not in enemy:
            raise ValueError(f"Enemy entity {enemy_id} does not have a dialogue component, cannot create dialogue box")
        
        # Position dialogue box above the enemy's head
        enemy_x = enemy["position"].x
        enemy_y = enemy["position"].y
        
        # Center the dialogue box horizontally on the enemy (x + half enemy width - half box width)
        dialogue_x = enemy_x + 16 - (box_width // 2)
        # Place the dialogue box 3 lines above the enemy's head
        dialogue_y = enemy_y - 96
        
        # Create dialogue box rectangle
        dialogue_rect = pygame.Rect(dialogue_x, dialogue_y, box_width, box_height)
        
        # Add dialogue_box component directly to the enemy entity
        enemy["dialogue_box"] = DialogueBoxComponent(dialogue_rect)