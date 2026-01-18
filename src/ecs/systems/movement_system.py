class MovementSystem:
    def __init__(self, entity_manager):
        self.entity_manager = entity_manager

    def update(self, delta_time: float) -> None:
        for entity_id, components in self.entity_manager.get_entities_with_components(['position', 'velocity']):
            position = components['position']
            velocity = components['velocity']

            # Update position based on velocity and delta_time
            position.x += velocity.vx * delta_time
            position.y += velocity.vy * delta_time