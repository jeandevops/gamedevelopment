from ecs.entity_manager import EntityManager
from ecs.components.tile import TileComponent  
from ecs.components.position import PositionComponent
from ecs.components.sprite import SpriteComponent
from helpers.constants import MAPS_PATH, TILE_SIZE, GRASS, SAND, WATER, WOOD
import json

class MapFactory:
    def __init__(self):
        self.map_data = None

    def load_map(self, entity_manager: EntityManager, map_name: str) -> None:
        """Parses the map data and add tiles to the EntityManager"""
        
        with open(f"{MAPS_PATH}{map_name}.json", "r") as file:
            self.map_data = file.read()

        parsed_map_data = self._parse_map_data()
        for row_index, row in enumerate(parsed_map_data):
            for col_index, tile_type in enumerate(row):
                entity_id = f"tile_{row_index}_{col_index}"
                position = PositionComponent(x=col_index * TILE_SIZE["width"], y=row_index * TILE_SIZE["height"])
                sprite = SpriteComponent(width=TILE_SIZE["width"], height=TILE_SIZE["height"])
                tile = TileComponent(tile_type=tile_type)
                components = {
                    "position": position,
                    "tile": tile,
                    "sprite": sprite
                }
                entity_manager.add_entity(entity_id, components)

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