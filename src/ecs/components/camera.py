class CameraComponent:
    def __init__(self, x: float, y: float, viewport_width: int, viewport_height: int, lerp_speed: float):
        """Initializes the Camera with x and y coordinates and viewport size"""
        self.x = x
        self.y = y
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.lerp_speed = lerp_speed

    def follow_target(self, target_x: float, target_y: float, trigger_margin: int, delta_time: float):
        """Centers the camera on the target coordinates"""
        camera_horizontal_position = abs((self.x + self.viewport_width / 2) - target_x)
        camera_vertical_position = abs((self.y + self.viewport_height / 2) - target_y)
        movement_factor = delta_time * self.lerp_speed

        if camera_horizontal_position > trigger_margin:
            camera_horizontal_destiny = target_x - self.viewport_width / 2
            self.x = self._lerp(self.x, camera_horizontal_destiny, movement_factor)
            
        if camera_vertical_position > trigger_margin:
            camera_vertical_destiny = target_y - self.viewport_height / 2
            self.y = self._lerp(self.y, camera_vertical_destiny, movement_factor)

    def _lerp(self, start: float, end: float, movement_factor: float) -> float:
        """Linearly interpolates between start and end by lerp_speed"""
        clamped_factor = min(movement_factor, 1.0)  # Ensure delta_time does not exceed 1 second for stability
        return start + (end - start) * clamped_factor