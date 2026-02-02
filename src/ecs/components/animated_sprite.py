from helpers.sprites_maker import AnimatedSprite
from helpers.constants import DEFAULT_ANIMATION_FRAME_DURATION

class AnimatedSpriteComponent:
    def __init__(self, sprite: AnimatedSprite):
        """Initializes the AnimatedSpriteComponent"""
        self.sprite = sprite
        self.width = sprite.rect.width
        self.height = sprite.rect.height
        self.animate = True
        self.elapsed_time = 0.0
        self.frame_duration = DEFAULT_ANIMATION_FRAME_DURATION
        self.frame_index = 0  # Each component tracks its own frame

    def disable_animation(self) -> None:
        """Disables the animation"""
        self.animate = False

    def enable_animation(self) -> None:
        """Enables the animation"""
        self.animate = True