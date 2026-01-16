from world.entity_manager import EntityManager
from components.tile import TileComponent  
from components.position import PositionComponent
from utils.constants import TILE_SIZE, GRASS, SAND, WATER

class MapLoader:
    def __init__(self, map_data):
        self.map_data = map_data

    def load_map(self, entity_manager: EntityManager) -> None:
        """Parses the map data and add tiles to the EntityManager"""
        
        parsed_map_data = self._parse_map_data()
        for row_index, row in enumerate(parsed_map_data):
            for col_index, tile_type in enumerate(row):
                entity_id = f"tile_{row_index}_{col_index}"
                position = PositionComponent(x=col_index * TILE_SIZE, y=row_index * TILE_SIZE)
                tile = TileComponent(width=TILE_SIZE, height=TILE_SIZE, tile_type=tile_type)
                components = {
                    "position": position,
                    "tile": tile
                }
                entity_manager.add_entity(entity_id, components)

    def _parse_map_data(self) -> list[list[int]]:
        """Parses the raw map data into a usable format"""

        value_conversion = {
            '.': GRASS,
            '~': WATER,
            '#': SAND
        }
        
        parsed_map_data = []
        for line in self.map_data:
            parsed_line = []
            for tile in line.split():
                # Use .get() with GRASS as default for invalid tiles
                parsed_line.append(value_conversion.get(tile, GRASS))
            parsed_map_data.append(parsed_line)
        return parsed_map_data