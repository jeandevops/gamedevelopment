from ecs.components.position import PositionComponent
from ecs.components.velocity import VelocityComponent
from ecs.components.direction import DirectionComponent
from ecs.entity_manager import EntityManager
from ecs.components.sprite import SpriteComponent
from .sprites_maker import AnimatedSprite
from helpers.constants import (
    CHARACTER_SPRITES_PATH,
    CHARACTER_FILE
)

class PlayerFactory:
    """Factory for creating player entities"""

    @staticmethod
    def create_player(entity_manager: EntityManager, x: float, y: float) -> None:
        """
        Creates a player entity with the necessary components and adds it to the EntityManager
        """
        sprite_size = 32
        sprites = {
            "up": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=(2*sprite_size), coordinate_y=(4*sprite_size), width=sprite_size, height=sprite_size, horizontal_steps=2),
            "down": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=(2*sprite_size), coordinate_y=0, width=sprite_size, height=sprite_size, horizontal_steps=2),
            "left": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=(2*sprite_size), coordinate_y=(6*sprite_size), width=sprite_size, height=sprite_size, horizontal_steps=2),
            "right": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=(2*sprite_size), coordinate_y=(2*sprite_size), width=sprite_size, height=sprite_size, horizontal_steps=2),
            "up_right": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=(2*sprite_size), coordinate_y=(3*sprite_size), width=sprite_size, height=sprite_size, horizontal_steps=2),
            "up_left": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=(2*sprite_size), coordinate_y=(5*sprite_size), width=sprite_size, height=sprite_size, horizontal_steps=2),
            "down_right": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=(2*sprite_size), coordinate_y=(1*sprite_size), width=sprite_size, height=sprite_size, horizontal_steps=2),
            "down_left": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=(2*sprite_size), coordinate_y=(7*sprite_size), width=sprite_size, height=sprite_size, horizontal_steps=2),
            "idle_up": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=0, coordinate_y=(4*sprite_size), width=sprite_size, height=sprite_size, horizontal_steps=2),
            "idle_down": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=0, coordinate_y=0, width=sprite_size, height=sprite_size, horizontal_steps=2),
            "idle_left": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=0, coordinate_y=(6*sprite_size), width=sprite_size, height=sprite_size, horizontal_steps=2),
            "idle_right": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=0, coordinate_y=(2*sprite_size), width=sprite_size, height=sprite_size, horizontal_steps=2),
            "idle_up_right": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=0, coordinate_y=(3*sprite_size), width=sprite_size, height=sprite_size, horizontal_steps=2),
            "idle_up_left": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=0, coordinate_y=(5*sprite_size), width=sprite_size, height=sprite_size, horizontal_steps=2),
            "idle_down_right": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=0, coordinate_y=(1*sprite_size), width=sprite_size, height=sprite_size, horizontal_steps=2),
            "idle_down_left": AnimatedSprite(file_path=CHARACTER_SPRITES_PATH, file_name=CHARACTER_FILE, coordinate_x=0, coordinate_y=(7*sprite_size), width=sprite_size, height=sprite_size, horizontal_steps=2),
        }

        player_components = {
            "position": PositionComponent(x=x, y=y),
            "velocity": VelocityComponent(vx=0, vy=0),
            "direction": DirectionComponent(),
            "animated_sprite": SpriteComponent(sprite=sprites["down"]), # Default facing down
            "sprite_pool": sprites
        }
        entity_manager.add_entity("player", player_components)
