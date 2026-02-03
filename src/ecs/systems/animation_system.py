from ecs.components.animated_sprite import AnimatedSpriteComponent
from ecs.entity_manager import EntityManager

class AnimationSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    def animate(self, delta_time: float) -> None:
        """Updates all animated sprites based on the elapsed time"""
        if delta_time <= 0:
            raise ValueError("delta_time must be positive")
        
        try:
            for entity_id, components in self.entity_manager.get_entities_with_components(['animated_sprite']):
                if not components['animated_sprite'].animate:
                    continue  # Skip if animation is disabled
                animated_sprite: AnimatedSpriteComponent = components['animated_sprite']
                animated_sprite.elapsed_time += delta_time * 1000  # Convert to milliseconds

                if animated_sprite.elapsed_time >= animated_sprite.frame_duration:
                    # Advance the frame index (each component has its own)
                    animated_sprite.frame_index += 1
                    if animated_sprite.frame_index >= len(animated_sprite.sprite.images):
                        animated_sprite.frame_index = 0

                    # Update the sprite's current_image to match this component's frame
                    animated_sprite.sprite.image = animated_sprite.sprite.get_frame(animated_sprite.frame_index)

                    animated_sprite.elapsed_time = 0.0
        except Exception as e:
            raise RuntimeError(f"An error occurred during animation update: {e}")