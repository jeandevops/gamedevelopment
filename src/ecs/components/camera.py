class CameraComponent:
    """
    Camera data component - pure data, no logic.
    Stores camera position and configuration.
    """
    
    def __init__(self, x: float, y: float, viewport_width: int, viewport_height: int, lerp_speed: float):
        """Initializes the Camera with position, viewport size, and lerp speed"""
        self.x = x
        self.y = y
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.lerp_speed = lerp_speed
