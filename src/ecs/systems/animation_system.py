from ecs.components.sprite import SpriteComponent
from ecs.entity_manager import EntityManager
from helpers.logger import logger
from helpers.constants import (
    ERROR_INVALID_DELTA_TIME,
    ERROR_INVALID_SPRITE_OBJECT,
    ERROR_ANIMATION_SYSTEM_FAILED,
)

class AnimationSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
        logger.debug("AnimationSystem initialized")

    def animate(self, delta_time: float) -> None:
        """Updates all animated sprites based on the elapsed time"""
        if delta_time <= 0:
            error_msg = ERROR_INVALID_DELTA_TIME.format(value=delta_time)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            for entity_id, components in self.entity_manager.get_entities_with_components(['animated_sprite']):
                if not components['animated_sprite'].animate:
                    continue  # Skip if animation is disabled
                animated_sprite: SpriteComponent = components['animated_sprite']
                
                # Validate sprite object
                if not hasattr(animated_sprite.sprite, 'images') or not animated_sprite.sprite.images:
                    error_msg = ERROR_INVALID_SPRITE_OBJECT.format(entity_id=entity_id)
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
                
                animated_sprite.elapsed_time += delta_time * 1000  # Convert to milliseconds

                if animated_sprite.elapsed_time >= animated_sprite.frame_duration:
                    # Advance the frame index (each component has its own)
                    animated_sprite.frame_index += 1
                    if animated_sprite.frame_index >= len(animated_sprite.sprite.images):
                        animated_sprite.frame_index = 0

                    # Update the sprite's current_image to match this component's frame
                    animated_sprite.sprite.image = animated_sprite.sprite.get_frame(animated_sprite.frame_index)

                    animated_sprite.elapsed_time = 0.0
        except ValueError:
            raise  # Re-raise ValueError as-is
        except RuntimeError:
            raise  # Re-raise RuntimeError as-is
        except Exception as e:
            error_msg = ERROR_ANIMATION_SYSTEM_FAILED.format(error=str(e))
            logger.error(error_msg)
            raise RuntimeError(error_msg)