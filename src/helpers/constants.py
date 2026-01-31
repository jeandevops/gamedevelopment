BLACK = (0, 0, 0)
WOOD = 0
GRASS = 1
SAND = 2
WATER = 3

MAPS_PATH = "assets/maps/"
TERRAIN_SPRITES_PATH = "assets/sprites/texture/"
TILE_SET_SPRITE_FILE = "tx-tileset-grass.png"

TILE_SIZE = {
    "width": 32,
    "height": 32
}

TILE_COLORS = {
    GRASS: (34, 139, 34),    # Forest green
    SAND: (184, 134, 11),    # Dark goldenrod
    WATER: (0, 100, 200),    # Ocean blue
    WOOD: (139, 69, 19)      # Saddle brown
}

CAMERA_TRIGGER_MARGIN = 200

CAMERA_WIDTH = 800
CAMERA_HEIGHT = 600

SPEED = 240
FPS = 30
DEFAULT_ANIMATION_FRAME_DURATION = 150  # in milliseconds