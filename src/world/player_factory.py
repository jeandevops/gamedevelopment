from ecs.components.position import PositionComponent
from ecs.components.velocity import VelocityComponent
from ecs.components.player import PlayerComponent
from ecs.components.sprite import SpriteComponent
from helpers.constants import WATER


class PlayerFactory:
    """Factory for creating player entities"""

    @staticmethod
    def create_player(entity_manager, x: float, y: float) -> None:
        """
        Creates a player entity at the specified position.
        
        Args:
            entity_manager: The entity manager to add the player to
            x: Starting x position in world coordinates
            y: Starting y position in world coordinates
        """
        player_components = {
            "position": PositionComponent(x=x, y=y),
            "velocity": VelocityComponent(vx=0, vy=0),
            "player_component": PlayerComponent(),
            "sprite": SpriteComponent(width=32, height=32)
        }
        entity_manager.add_entity("player", player_components)
