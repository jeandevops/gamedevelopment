from helpers.constants import GRASS, SAND

class TileComponent:
    def __init__(self, tile_type: int):
        """Initializes the TileComponent with width, height, and tile type"""
        self.tile_type = tile_type
        self.is_walkable = self.is_walkable()

    def is_walkable(self) -> bool:
        """Determines if the tile is walkable based on its type"""
        walkable_types = [GRASS, SAND]
        return self.tile_type in walkable_types
