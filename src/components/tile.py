from utils.constants import GRASS, SAND, WATER

class TileComponent:
    def __init__(self, width: int, height: int, tile_type: int):
        """Initializes the TileComponent with width, height, and tile type"""
        self.width = width
        self.height = height
        self.tile_type = tile_type

    def is_walkable(self) -> bool:
        """Determines if the tile is walkable based on its type"""
        walkable_types = [GRASS, SAND]
        return self.tile_type in walkable_types