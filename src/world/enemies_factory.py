from ecs.entity_manager import EntityManager
from ecs.components.position import PositionComponent
from ecs.components.velocity import VelocityComponent
from ecs.components.direction import DirectionComponent
from ecs.entity_manager import EntityManager
from ecs.components.sprite import SpriteComponent
from ecs.components.ai import AIBehaviorComponent
from .sprites_maker import AnimatedSprite
from helpers.constants import (
    ENEMY_SPRITES_PATH,
    ENEMIES_SPECS,
    SIZE_MAP
)
from helpers.logger import logger
import json

class EnemiesSpritePool:
    def __init__(self, enemy_name: str) -> None:
        """ Initializes the sprite pool with preloaded sprites for different enemy states and directions """
        logger.debug("Initializing tiles sprite pool...")
        enemy_file = f"{enemy_name}.png"
        enemies_size = ENEMIES_SPECS[enemy_name]["size"]
        sprite_size = SIZE_MAP[enemies_size]
        self.sprites = {
            "up": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=(2*sprite_size), 
                coordinate_y=(4*sprite_size), 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "down": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=(2*sprite_size), 
                coordinate_y=0, 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "left": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=(2*sprite_size), 
                coordinate_y=(6*sprite_size), 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "right": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=(2*sprite_size), 
                coordinate_y=(2*sprite_size), 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "up_right": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=(2*sprite_size), 
                coordinate_y=(3*sprite_size), 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "up_left": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=(2*sprite_size), 
                coordinate_y=(5*sprite_size), 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "down_right": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=(2*sprite_size), 
                coordinate_y=(1*sprite_size), 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "down_left": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=(2*sprite_size), 
                coordinate_y=(7*sprite_size), 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "idle_up": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=0, 
                coordinate_y=(4*sprite_size), 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "idle_down": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=0, 
                coordinate_y=0, 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "idle_left": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=0, 
                coordinate_y=(6*sprite_size), 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "idle_right": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=0, 
                coordinate_y=(2*sprite_size), 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "idle_up_right": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=0, 
                coordinate_y=(3*sprite_size), 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "idle_up_left": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=0, 
                coordinate_y=(5*sprite_size), 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "idle_down_right": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=0, 
                coordinate_y=(1*sprite_size), 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
            "idle_down_left": AnimatedSprite(
                file_path=ENEMY_SPRITES_PATH,
                file_name=enemy_file, 
                coordinate_x=0, 
                coordinate_y=(7*sprite_size), 
                width=sprite_size, 
                height=sprite_size, 
                horizontal_steps=2
            ),
        }
            

class EnemiesFactory:
    """Factory for creating enemy entities"""

    def __init__(self, entity_manager: EntityManager, map_data: str):
        self.entity_manager = entity_manager
        enemies_data = json.loads(map_data)["enemies"]
        self.enemies_data = enemies_data

    def create_enemies(self) -> None:
        """
        Creates an enemy entity with the necessary components and adds it to the EntityManager
        """
        
        if not self.enemies_data:
            logger.warning("No enemies data provided, skipping enemy creation")
            return
        
        # List of tuples containing enemy types and sizes:
        enemy_types = [enemy["type"] for enemy in self.enemies_data]

        # For each type listed create the sprites:
        enemies_sprites_pools = {enemy_type: EnemiesSpritePool(enemy_type) for enemy_type in enemy_types}

        # Create an enemy component for each enemy in the enemies_data list:
        _enemy_index = 0
        for enemy in self.enemies_data:
            _enemy_index += 1
            enemy_type = enemy["type"]
            enemy_x = enemy["position"]["x"]
            enemy_y = enemy["position"]["y"]
            vision_range = ENEMIES_SPECS[enemy_type]["vision_range"]
            interaction_range = ENEMIES_SPECS[enemy_type]["interaction_range"]
            aggressive = ENEMIES_SPECS[enemy_type]["aggressive"]
            wander_speed = ENEMIES_SPECS[enemy_type]["wander_speed"]
            chase_speed = ENEMIES_SPECS[enemy_type]["chase_speed"]
            sprites_pool = enemies_sprites_pools.get(enemy_type)
            if not sprites_pool:
                logger.warning(f"No sprite pool found for enemy type: {enemy_type}, skipping enemy creation")
                continue

            enemy_components = {
                "position": PositionComponent(x=enemy_x, y=enemy_y),
                "velocity": VelocityComponent(vx=0, vy=0),
                "direction": DirectionComponent(),
                "animated_sprite": SpriteComponent(sprite=sprites_pool.sprites["idle_down"]), # Default facing down
                "ai_behavior": AIBehaviorComponent(behavior_type="wander", vision_range=vision_range, interaction_range=interaction_range, aggressive=aggressive, wander_speed=wander_speed, chase_speed=chase_speed),
                "sprite_pool": sprites_pool.sprites
            }
            self.entity_manager.add_entity(f"enemy_{_enemy_index}", enemy_components)
            logger.debug("Created {} enemy at position ({}, {})".format(enemy_type, enemy_x, enemy_y))