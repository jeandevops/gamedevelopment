from helpers.constants import GRASS, SAND, WATER, WOOD

class TileComponent:
    def __init__(self, tile_type: int):
        """Initializes the TileComponent with tile type"""
        self.tile_type = tile_type
