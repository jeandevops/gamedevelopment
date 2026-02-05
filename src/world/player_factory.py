from ecs.components.position import PositionComponent
from ecs.components.velocity import VelocityComponent
from ecs.components.player import PlayerComponent
from ecs.entity_manager import EntityManager
from ecs.components.sprite import SpriteComponent
from .sprites_maker import AnimatedSprite
from helpers.constants import (
    BLUE_CRISTAL_SPRITE_FILE,
    CRISTALS_SPRITES_PATH
)

class PlayerFactory:
    """Factory for creating player entities"""

    @staticmethod
    def create_player(entity_manager: EntityManager, x: float, y: float) -> None:
        """
        Creates a player entity at the specified position.
        
        Args:
            entity_manager: The entity manager to add the player to
            x: Starting x position in world coordinates
            y: Starting y position in world coordinates
        """
        animation = AnimatedSprite(file_path=CRISTALS_SPRITES_PATH, file_name=BLUE_CRISTAL_SPRITE_FILE, coordinate_x=0, coordinate_y=0, width=32, height=32, horizontal_steps=8)

        player_components = {
            "position": PositionComponent(x=x, y=y),
            "velocity": VelocityComponent(vx=0, vy=0),
            "player_component": PlayerComponent(),
            "animated_sprite": SpriteComponent(sprite=animation)
        }
        entity_manager.add_entity("player", player_components)
