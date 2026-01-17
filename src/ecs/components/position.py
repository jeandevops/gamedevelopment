class PositionComponent:
    def __init__(self, x=0.0, y=0.0):
        """Initializes the PositionComponent with x and y coordinates"""
        self.x = x
        self.y = y

    def set_position(self, x, y):
        """Sets the x and y coordinates of the PositionComponent"""
        self.x = x
        self.y = y

    def get_position(self):
        """Returns the current position as a tuple (x, y)"""
        return (self.x, self.y)
