from ecs.components.camera import CameraComponent
from helpers.constants import CAMERA_TRIGGER_MARGIN
from helpers.math import lerp


class CameraSystem:
    def __init__(self, camera: CameraComponent):
        """Initializes the CameraSystem with a camera component"""
        self.camera = camera
        self.trigger_margin = CAMERA_TRIGGER_MARGIN

    def update(self, target_x: float, target_y: float, delta_time: float) -> None:
        """Updates the camera position to follow the target coordinates with lerp"""
        # Calculate distances from camera center to target
        camera_center_x = self.camera.x + self.camera.viewport_width / 2
        camera_center_y = self.camera.y + self.camera.viewport_height / 2
        
        horizontal_distance = abs(camera_center_x - target_x)
        vertical_distance = abs(camera_center_y - target_y)
        
        # Calculate movement factor for this frame
        movement_factor = delta_time * self.camera.lerp_speed
        
        # Move horizontally if outside trigger margin
        if horizontal_distance > self.trigger_margin:
            target_camera_x = target_x - self.camera.viewport_width / 2
            self.camera.x = lerp(self.camera.x, target_camera_x, movement_factor)
        
        # Move vertically if outside trigger margin
        if vertical_distance > self.trigger_margin:
            target_camera_y = target_y - self.camera.viewport_height / 2
            self.camera.y = lerp(self.camera.y, target_camera_y, movement_factor)
