class CameraComponent:
    def __init__(self, x: float, y: float, viewport_width: int, viewport_height: int):
        """Initializes the Camera with x and y coordinates and viewport size"""
        self.x = x
        self.y = y
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

    def follow_target(self, target_x: float, target_y: float, trigger_margin: int):
        """Centers the camera on the target coordinates"""
        if abs((self.x + self.viewport_width / 2) - target_x) > trigger_margin:
            self.x = target_x - self.viewport_width / 2
        if abs((self.y + self.viewport_height / 2) - target_y) > trigger_margin:
            self.y = target_y - self.viewport_height / 2