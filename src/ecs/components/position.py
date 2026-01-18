class PositionComponent:
    def __init__(self, x: float, y: float):
        """Initializes the PositionComponent with x and y coordinates"""
        self.x = x
        self.y = y

    def set_position(self, x: float, y: float) -> None:
        """Sets the x and y coordinates of the PositionComponent"""
        self.x = x
        self.y = y

    def get_position(self) -> tuple[float, float]:
        """Returns the current position as a tuple (x, y)"""
        return (self.x, self.y)