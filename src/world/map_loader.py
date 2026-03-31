from ecs.entity_manager import EntityManager
from ecs.components.tile import TileComponent  
from ecs.components.collision import CollisionComponent
from ecs.components.position import PositionComponent
from ecs.components.sprite import SpriteComponent
from helpers.constants import (
    TILE_SIZE, GRASS, SAND, WATER, WOOD,
    TERRAIN_SPRITES_PATH, CRISTALS_SPRITES_PATH,
    TILE_SET_SPRITE_FILE, GREY_CRISTAL_SPRITE_FILE, TREE_AND_WATER_FILE,
    ERROR_MAP_PARSE_FAILED,
    ERROR_MAP_EMPTY,
    ERROR_TILE_LOADING_FAILED,
)
from helpers.logger import logger
import os
from world.sprites_maker import AnimatedSprite
import json

class TileSpritePool:
    def __init__(self):
        """ Initializes the sprite pool with preloaded sprites for different tile types """
        logger.debug("Initializing tiles sprite pool...")
        root_path = os.path.dirname(os.path.abspath(__file__))
        terrain_textures_path = os.path.join(root_path, "..", *TERRAIN_SPRITES_PATH.split("/"))
        cristals_textures_path = os.path.join(root_path, "..", *CRISTALS_SPRITES_PATH.split("/"))

        try:
            sprites_pool = {
                GRASS: AnimatedSprite(file_path = terrain_textures_path, file_name=TILE_SET_SPRITE_FILE, coordinate_x=0, coordinate_y=0, width=TILE_SIZE["width"], height=TILE_SIZE["height"], horizontal_steps=4),
                WATER: AnimatedSprite(file_path = terrain_textures_path, file_name=TREE_AND_WATER_FILE, coordinate_x=0, coordinate_y=0, width=TILE_SIZE["width"], height=TILE_SIZE["height"], horizontal_steps=3),
                SAND: AnimatedSprite(file_path = terrain_textures_path, file_name=TILE_SET_SPRITE_FILE, coordinate_x=128, coordinate_y=96, width=TILE_SIZE["width"], height=TILE_SIZE["height"], horizontal_steps=3),
                WOOD: AnimatedSprite(file_path = cristals_textures_path, file_name=GREY_CRISTAL_SPRITE_FILE, coordinate_x=0, coordinate_y=0, width=TILE_SIZE["width"], height=TILE_SIZE["height"], horizontal_steps=8)
            }
            self.pool = sprites_pool
            logger.info(f"Sprite pool initialized with {len(sprites_pool)} sprite types")
        except Exception as e:
            logger.critical(f"Failed to initialize sprite pool: {e}")
            raise

    def get_sprite(self, tile_type: int) -> AnimatedSprite | None:
        """Get sprite from pool by tile type"""
        sprite = self.pool.get(tile_type)
        if not sprite:
            logger.warning(f"No sprite found for tile type: {tile_type}")
        return sprite
        
class MapFactory:
    def __init__(self, map_data: str|None = None):
        self.map_data = map_data

    def _create_collision_from_tile_type(self, tile_type: int) -> CollisionComponent|None:
        """Create collision component based on tile type"""
        # Tolerance map: if tile_type not in this map, it's walkable (no collision component needed)
        # Values represent collision tolerance in pixels
        collision_map = {
            WATER: 16,
            WOOD: 0,
        }
        
        if tile_type in collision_map:
            tolerance = collision_map[tile_type]
            return CollisionComponent(tolerance=tolerance)
        
        # Walkable tiles don't need a collision component
        return None

    def load_tiles(self, entity_manager: EntityManager) -> None:
        """Loads the map from a file and creates tile entities in the EntityManager"""
        if not self.map_data:
            error_msg = ERROR_MAP_EMPTY
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        sprites_pool = TileSpritePool()

        try:
            parsed_map_data = self._parse_map_data()
            logger.debug(f"Map parsed: {len(parsed_map_data)} rows")
        except json.JSONDecodeError as e:
            error_msg = ERROR_MAP_PARSE_FAILED.format(error=str(e))
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = ERROR_MAP_PARSE_FAILED.format(error=str(e))
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        if not parsed_map_data or (parsed_map_data and not parsed_map_data[0]):
            error_msg = ERROR_MAP_EMPTY
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            tile_count = 0
            for row_index, row in enumerate(parsed_map_data):
                for col_index, tile_type in enumerate(row):
                    entity_id = f"tile_{row_index}_{col_index}"
                    position = PositionComponent(x=col_index * TILE_SIZE["width"], y=row_index * TILE_SIZE["height"])
                    tile = TileComponent(tile_type=tile_type)
                    animation = sprites_pool.get_sprite(tile_type)
                    if not animation:
                        logger.warning(f"No sprite available for tile type {tile_type} at ({row_index}, {col_index}), skipping")
                        continue
                    animated_sprite = SpriteComponent(animation)
                    
                    # Build components dict - only add collision if it's a solid tile
                    components = {
                        "position": position,
                        "tile": tile,
                        "animated_sprite": animated_sprite
                    }
                    collision = self._create_collision_from_tile_type(tile_type)
                    if collision is not None:
                        components["collision"] = collision
                    
                    entity_manager.add_entity(entity_id, components)
                    tile_count += 1
            logger.info(f"Map loaded successfully: {tile_count} tiles created")
        except Exception as e:
            error_msg = ERROR_TILE_LOADING_FAILED.format(error=str(e))
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _parse_map_data(self) -> list[list[int]]:
        """Parses the raw map data into a usable format"""

        value_conversion = {
            '.': GRASS,
            '~': WATER,
            '^': SAND,
            '#': WOOD
        }

        self.map_data = json.loads(self.map_data)
        
        parsed_map_data = []
        for line in self.map_data["tiles"]:
            parsed_line = []
            for tile in line.split():
                # Use .get() with GRASS as default for invalid tiles
                parsed_line.append(value_conversion.get(tile, GRASS))
            parsed_map_data.append(parsed_line)
        return parsed_map_data