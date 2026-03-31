from world.sprites_maker import AnimatedSprite
from helpers.constants import DEFAULT_ANIMATION_FRAME_DURATION

class SpriteComponent:
    def __init__(self, sprite: AnimatedSprite, frame_duration: int = DEFAULT_ANIMATION_FRAME_DURATION):
        """Initializes the AnimatedSpriteComponent"""
        self.sprite: AnimatedSprite = sprite
        self.width: float | int = sprite.rect.width # type: ignore
        self.height: float | int = sprite.rect.height # type: ignore
        self.animate: bool = True
        self.elapsed_time: float = 0.0
        self.frame_duration: int = frame_duration
        self.frame_index: int = 0  # Each component tracks its own frame

    def disable_animation(self) -> None:
        """Disables the animation"""
        self.animate = False

    def enable_animation(self) -> None:
        """Enables the animation"""
        self.animate = True