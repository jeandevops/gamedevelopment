from helpers.constants import (
    TERRAIN_SPRITES_PATH,
    ERROR_SPRITE_SHEET_NOT_FOUND,
    ERROR_SPRITE_SHEET_LOAD_FAILED,
    ERROR_INVALID_SPRITE_COORDINATES,
    ERROR_NO_SPRITES_LOADED,
    ERROR_INVALID_FRAME_COUNT,
)
from helpers.logger import logger
import os
import pygame

class AnimatedSprite(pygame.sprite.Sprite):
    """
    Factory class to create sprite objects based on coordinates from a sprite sheet.
    """
    def __init__(self, file_path: str, file_name: str, coordinate_x: int, coordinate_y: int, width: int, height: int, horizontal_steps: int=1, vertical_steps: int=1):
        pygame.sprite.Sprite.__init__(self)
        logger.debug(f"Creating AnimatedSprite: {file_name} with {horizontal_steps}x{vertical_steps} frames")
        self.images = self._load_images(file_path, file_name, coordinate_x, coordinate_y, width, height, horizontal_steps, vertical_steps)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        logger.info(f"AnimatedSprite loaded successfully: {len(self.images)} frames")
    
    def get_frame(self, frame_index: int) -> pygame.Surface:
        """Returns the image at the specified frame index (stateless)"""
        return self.images[frame_index % len(self.images)]

    def _load_images(self, file_path: str, file_name: str, coordinate_x: int, coordinate_y: int, width: int, height: int, horizontal_steps: int, vertical_steps: int) -> list[pygame.Surface]:
        """Loads sprite images from a sprite sheet with error handling"""
        # Validate frame counts
        if horizontal_steps <= 0 or vertical_steps <= 0:
            error_msg = ERROR_INVALID_FRAME_COUNT.format(h=horizontal_steps, v=vertical_steps)
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            texture_path = os.path.join(file_path, file_name)
            logger.debug(f"Loading sprite sheet from: {texture_path}")
            
            if not os.path.exists(texture_path):
                error_msg = ERROR_SPRITE_SHEET_NOT_FOUND.format(path=texture_path)
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            loaded_sprite_sheet = pygame.image.load(texture_path)  # .convert_alpha() for transparency
            logger.debug(f"Sprite sheet loaded: {loaded_sprite_sheet.get_size()}")
            
        except pygame.error as e:
            error_msg = ERROR_SPRITE_SHEET_LOAD_FAILED.format(file=file_name, error=str(e))
            logger.critical(error_msg)
            raise RuntimeError(error_msg)
        except FileNotFoundError as e:
            logger.critical(str(e))
            raise
        except Exception as e:
            error_msg = ERROR_SPRITE_SHEET_LOAD_FAILED.format(file=file_name, error=str(e))
            logger.critical(error_msg)
            raise RuntimeError(error_msg)
        
        sprite_list = []

        try:
            logger.debug(f"Extracting {vertical_steps}x{horizontal_steps} sprite frames")
            for j in range(vertical_steps):
                for i in range(horizontal_steps):
                    image = loaded_sprite_sheet.subsurface(pygame.Rect(coordinate_x + i * width, coordinate_y + j * height, width, height))
                    sprite_list.append(image)
        except ValueError as e:
            error_msg = ERROR_INVALID_SPRITE_COORDINATES.format(error=str(e))
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        if not sprite_list:
            error_msg = ERROR_NO_SPRITES_LOADED
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        return sprite_list