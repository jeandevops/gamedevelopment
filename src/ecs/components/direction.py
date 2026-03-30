class DirectionComponent:
    def __init__(self):
        self.direction = "down"

    def set_direction(self, direction: str) -> None:
        """Sets the current direction of the entity"""
        self.direction = direction