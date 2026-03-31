from helpers.constants import (
    MAPS_PATH,
    ERROR_MAP_FILE_NOT_FOUND,
    ERROR_MAP_READ_FAILED,
)
from helpers.logger import logger

def load_map(map_name: str) -> str:
    """Parses the map data and add tiles entities to the EntityManager"""
    logger.info(f"Loading map: {map_name}")
    
    try:
        with open(f"{MAPS_PATH}{map_name}.json", "r") as file:
            map_data = file.read()
            logger.debug(f"Map file read successfully: {map_name}.json")
    except FileNotFoundError:
        error_msg = ERROR_MAP_FILE_NOT_FOUND.format(map_name=map_name)
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    except IOError as e:
        error_msg = ERROR_MAP_READ_FAILED.format(map_name=map_name, error=str(e))
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    return map_data