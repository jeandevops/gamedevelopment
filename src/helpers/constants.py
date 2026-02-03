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

CAMERA_TRIGGER_MARGIN = 200

CAMERA_WIDTH = 800
CAMERA_HEIGHT = 600

SPEED = 240
FPS = 30
DEFAULT_ANIMATION_FRAME_DURATION = 150  # in milliseconds

# ============ ERROR MESSAGES ============

# Sprite Loading Errors
ERROR_SPRITE_SHEET_NOT_FOUND = "Sprite sheet not found: {path}"
ERROR_SPRITE_SHEET_LOAD_FAILED = "Failed to load sprite sheet '{file}': {error}"
ERROR_INVALID_SPRITE_COORDINATES = "Invalid sprite coordinates or dimensions: {error}"
ERROR_NO_SPRITES_LOADED = "No sprite frames loaded from sprite sheet"
ERROR_INVALID_FRAME_COUNT = "Frame counts must be positive: horizontal={h}, vertical={v}"

# Map Loading Errors
ERROR_MAP_FILE_NOT_FOUND = "Map file not found: {map_name}.json"
ERROR_MAP_READ_FAILED = "Error reading map file '{map_name}': {error}"
ERROR_MAP_PARSE_FAILED = "Error parsing map data: {error}"
ERROR_MAP_EMPTY = "Map data is empty"
ERROR_TILE_LOADING_FAILED = "Error loading tiles: {error}"

# Animation Errors
ERROR_INVALID_DELTA_TIME = "delta_time must be non-negative, got {value}"
ERROR_INVALID_SPRITE_OBJECT = "Entity {entity_id} has invalid sprite with no images"
ERROR_ANIMATION_SYSTEM_FAILED = "Error in animation system: {error}"

# Entity Manager Errors
ERROR_ENTITY_NOT_FOUND = "Entity not found: {entity_id}"

# General Errors
ERROR_UNEXPECTED = "Unexpected error: {error}"