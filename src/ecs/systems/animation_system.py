from ecs.components.animated_sprite import AnimatedSpriteComponent
from ecs.entity_manager import EntityManager

class AnimationSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    def animate(self, delta_time: float) -> None:
        """Updates all animated sprites based on the elapsed time"""
        for entity_id, components in self.entity_manager.get_entities_with_components(['animated_sprite']):
            if not components['animated_sprite'].animate:
                continue  # Skip if animation is disabled
            animated_sprite: AnimatedSpriteComponent = components['animated_sprite']
            animated_sprite.elapsed_time += delta_time * 1000  # Convert to milliseconds

            if animated_sprite.elapsed_time >= animated_sprite.frame_duration:
                animated_sprite.sprite.update()
                animated_sprite.elapsed_time = 0.0