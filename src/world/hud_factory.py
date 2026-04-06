from ecs.entity_manager import EntityManager
from ecs.components.sprite import SpriteComponent
from ecs.components.position import PositionComponent
from .sprites_maker import AnimatedSprite
from helpers.constants import (
    HUD_SPRITES_PATH,
    HUD_FILE
)

class HUDSpritePool:
    def __init__(self):
        """ Initializes the sprite pool with preloaded sprites for different HUD elements """
        self.sprites = {
            "hp_bar": AnimatedSprite(
                file_path=HUD_SPRITES_PATH,
                file_name=HUD_FILE,
                coordinate_x=0,
                coordinate_y=0,
                width=96,
                height=32,
                horizontal_steps=3
            ),
            "enemy_hp_bar": AnimatedSprite(
                file_path=HUD_SPRITES_PATH,
                file_name=HUD_FILE,
                coordinate_x=0,
                coordinate_y=64,
                width=96,
                height=32,
                horizontal_steps=3
            ),
            "background": AnimatedSprite(
                file_path=HUD_SPRITES_PATH,
                file_name=HUD_FILE,
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

        enemy_position = entity_manager.get_entity_by_id(enemy_id)
        if not enemy_position:
            raise ValueError(f"Enemy entity {enemy_id} does not have a position component, cannot create HUD")
        
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

        player_position = entity_manager.get_entity_by_id("player")
        if not player_position:
            raise ValueError("Player entity does not have a position component, cannot create HUD")
        
        player_x = player_position["position"].x + 16 - 48  # Center the HP bar on the player (x + half player width - half HP bar width)
        player_y = player_position["position"].y - 32  # Position the HP bar above the player (y - HP bar height)
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