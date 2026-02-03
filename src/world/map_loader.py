from ecs.entity_manager import EntityManager
from ecs.components.tile import TileComponent  
from ecs.components.position import PositionComponent
from ecs.components.animated_sprite import AnimatedSpriteComponent
from helpers.constants import MAPS_PATH, TILE_SIZE, GRASS, SAND, WATER, WOOD, TILE_SET_SPRITE_FILE, TERRAIN_SPRITES_PATH
import os
from world.sprites_maker import AnimatedSprite
import json
from typing import Any

class SpritePool:
    def __init__(self):
        """ Initializes the sprite pool with preloaded sprites for different tile types """
        root_path = os.path.dirname(os.path.abspath(__file__))
        terrain_textures_path = os.path.join(root_path, "..", *TERRAIN_SPRITES_PATH.split("/"))

        sprites_pool = {
            GRASS: AnimatedSprite(file_path = terrain_textures_path, file_name=TILE_SET_SPRITE_FILE, coordinate_x=0, coordinate_y=0, width=TILE_SIZE["width"], height=TILE_SIZE["height"], horizontal_steps=4),
            WATER: AnimatedSprite(file_path = terrain_textures_path, file_name=TILE_SET_SPRITE_FILE, coordinate_x=0, coordinate_y=128, width=TILE_SIZE["width"], height=TILE_SIZE["height"], horizontal_steps=2),
            SAND: AnimatedSprite(file_path = terrain_textures_path, file_name=TILE_SET_SPRITE_FILE, coordinate_x=128, coordinate_y=96, width=TILE_SIZE["width"], height=TILE_SIZE["height"], horizontal_steps=3),
            WOOD: AnimatedSprite(file_path = terrain_textures_path, file_name=TILE_SET_SPRITE_FILE, coordinate_x=0, coordinate_y=128, width=TILE_SIZE["width"], height=TILE_SIZE["height"], horizontal_steps=2)
        }
        self.pool = sprites_pool

    def get_sprite(self, tile_type: int) -> AnimatedSprite | None:
        return self.pool.get(tile_type)
        
class MapFactory:
    def __init__(self):
        self.map_data: Any = None

    def load_map(self, entity_manager: EntityManager, map_name: str) -> None:
        """Parses the map data and add tiles entities to the EntityManager"""
        try:
            with open(f"{MAPS_PATH}{map_name}.json", "r") as file:
                self.map_data = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Map file '{map_name}.json' not found in path '{MAPS_PATH}'")
        except IOError as e:
            raise RuntimeError(f"An error occurred while reading the map file: {e}")
        
        sprites_pool = SpritePool()

        try:
            parsed_map_data = self._parse_map_data()
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error parsing map JSON data: {e}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred while parsing map data: {e}")

        if not parsed_map_data:
            raise ValueError("Parsed map data is empty or invalid.")
        
        try:
            for row_index, row in enumerate(parsed_map_data):
                for col_index, tile_type in enumerate(row):
                    entity_id = f"tile_{row_index}_{col_index}"
                    position = PositionComponent(x=col_index * TILE_SIZE["width"], y=row_index * TILE_SIZE["height"])
                    tile = TileComponent(tile_type=tile_type)
                    animation = sprites_pool.get_sprite(tile_type)
                    if not animation:
                        continue  # Skip if no sprite available for this tile type
                    animated_sprite = AnimatedSpriteComponent(animation)
                    components = {
                        "position": position,
                        "tile": tile,
                        "animated_sprite": animated_sprite
                    }
                    entity_manager.add_entity(entity_id, components)
        except Exception as e:
            raise RuntimeError(f"An error occurred while creating tile entities: {e}")

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