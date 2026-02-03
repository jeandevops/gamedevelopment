from helpers.constants import TERRAIN_SPRITES_PATH
import os
import pygame

class AnimatedSprite(pygame.sprite.Sprite):
    """
    Factory class to create sprite objects based on coordinates from a sprite sheet.
    """
    def __init__(self, file_path: str, file_name: str, coordinate_x: int, coordinate_y: int, width: int, height: int, horizontal_steps: int=0, vertical_steps: int=0):
        pygame.sprite.Sprite.__init__(self)
        self.images = self._load_images(file_path, file_name, coordinate_x, coordinate_y, width, height, horizontal_steps, vertical_steps)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
    
    def get_frame(self, frame_index: int) -> pygame.Surface:
        """Returns the image at the specified frame index (stateless)"""
        return self.images[frame_index % len(self.images)]

    def _load_images(self, file_path: str, file_name: str, coordinate_x: int, coordinate_y: int, width: int, height: int, horizontal_steps: int, vertical_steps: int) -> list[pygame.Surface]:
        """Loads grass tile images"""
        if (horizontal_steps == 0 and vertical_steps == 0) or horizontal_steps < 0 or vertical_steps < 0:
            raise ValueError("Either horizontal_steps or vertical_steps must be greater than zero.")

        try:
            texture_path = os.path.join(file_path, file_name)
            if not os.path.exists(texture_path):
                raise FileNotFoundError(f"Sprite sheet not found at path: {texture_path}")
            
            loaded_sprite_sheet = pygame.image.load(texture_path)#.convert_alpha() for transparency
        except pygame.error as e:
            raise RuntimeError(f"Unable to load sprite sheet image: {texture_path}\n{e}")
        except Exception as e:
            raise RuntimeError(f"An error occurred while loading the sprite sheet: {e}")
        
        sprite_list=[]
        vertical_loop_counter = vertical_steps or 1
        horizontal_loop_counter = horizontal_steps or 1

        try:
            for j in range(vertical_loop_counter):
                for i in range(horizontal_loop_counter):
                    image = loaded_sprite_sheet.subsurface(pygame.Rect(coordinate_x + i * width, coordinate_y + j * height, width, height))
                    sprite_list.append(image)
        except ValueError as e:
            raise RuntimeError(f"Invalid sprite coordinates or dimensions: {e}")
        
        if not sprite_list:
            raise RuntimeError("No sprites were loaded; please check the provided parameters.")

        return sprite_list