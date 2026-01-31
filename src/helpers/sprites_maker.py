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
        self.index = 0
        self.current_image = self.images[self.index]
        self.rect = self.current_image.get_rect()
    
    def update(self):
        """Update the grass sprite animation frame"""
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.current_image = self.images[self.index]

    def _load_images(self, file_path: str, file_name: str, coordinate_x: int, coordinate_y: int, width: int, height: int, horizontal_steps: int, vertical_steps: int) -> list[pygame.Surface]:
        """Loads grass tile images"""
        sprite_list=[]
        texture_path = os.path.join(file_path, file_name)
        loaded_sprite_sheet = pygame.image.load(texture_path)#.convert_alpha() for transparency
        vertical_loop_counter = vertical_steps or 1
        horizontal_loop_counter = horizontal_steps or 1
        for j in range(vertical_loop_counter):
            for i in range(horizontal_loop_counter):
                image = loaded_sprite_sheet.subsurface(pygame.Rect(coordinate_x + i * width, coordinate_y + j * height, width, height))
                sprite_list.append(image)
        return sprite_list