from helpers.constants import (
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
    def __init__(
        self,
        file_path: str | None = None,
        file_name: str | None = None,
        sprite_sheet: pygame.Surface | None = None,
        coordinate_x: int = 0,
        coordinate_y: int = 0,
        width: int = 0,
        height: int = 0,
        horizontal_steps: int = 1,
        vertical_steps: int = 1,
    ):
        pygame.sprite.Sprite.__init__(self)
        sheet_name = file_name if sprite_sheet is None else "shared sprite sheet"
        logger.debug(f"Creating AnimatedSprite: {sheet_name} with {horizontal_steps}x{vertical_steps} frames")
        self.images = self._load_images(
            sprite_sheet,
            file_path,
            file_name,
            coordinate_x,
            coordinate_y,
            width,
            height,
            horizontal_steps,
            vertical_steps,
        )
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        logger.debug(f"AnimatedSprite loaded successfully: {len(self.images)} frames")
    
    def get_frame(self, frame_index: int) -> pygame.Surface:
        """Returns the image at the specified frame index (stateless)"""
        return self.images[frame_index % len(self.images)]

    @staticmethod
    def load_sprite_sheet(file_path: str, file_name: str) -> pygame.Surface:
        """Loads and returns a sprite sheet surface from disk."""
        texture_path = os.path.join(file_path, file_name)
        logger.debug(f"Loading sprite sheet from: {texture_path}")

        if not os.path.exists(texture_path):
            error_msg = ERROR_SPRITE_SHEET_NOT_FOUND.format(path=texture_path)
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            sprite_sheet = pygame.image.load(texture_path)
            logger.debug(f"Sprite sheet loaded: {sprite_sheet.get_size()}")
            return sprite_sheet
        except pygame.error as e:
            error_msg = ERROR_SPRITE_SHEET_LOAD_FAILED.format(file=file_name, error=str(e))
            logger.critical(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = ERROR_SPRITE_SHEET_LOAD_FAILED.format(file=file_name, error=str(e))
            logger.critical(error_msg)
            raise RuntimeError(error_msg)

    def _load_images(
        self,
        sprite_sheet: pygame.Surface | None,
        file_path: str | None,
        file_name: str | None,
        coordinate_x: int,
        coordinate_y: int,
        width: int,
        height: int,
        horizontal_steps: int,
        vertical_steps: int,
    ) -> list[pygame.Surface]:
        """Loads sprite images from a sprite sheet with error handling"""
        if horizontal_steps <= 0 or vertical_steps <= 0:
            error_msg = ERROR_INVALID_FRAME_COUNT.format(h=horizontal_steps, v=vertical_steps)
            logger.error(error_msg)
            raise ValueError(error_msg)

        if sprite_sheet is None:
            if file_path is None or file_name is None:
                raise ValueError("file_path and file_name must be provided when sprite_sheet is not passed")
            loaded_sprite_sheet = self.load_sprite_sheet(file_path, file_name)
        else:
            loaded_sprite_sheet = sprite_sheet
            logger.debug("Using shared sprite sheet surface")

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