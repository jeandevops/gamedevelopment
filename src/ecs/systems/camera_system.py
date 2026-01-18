from ecs.components.camera import CameraComponent
from helpers.constants import CAMERA_TRIGGER_MARGIN

class CameraSystem:
    def __init__(self, camera: CameraComponent):
        """Initializes the CameraSystem with a camera component"""
        self.camera = camera
        self.trigger_margin = CAMERA_TRIGGER_MARGIN

    def update(self, target_x: float, target_y: float):
        """Updates the camera position to follow the target coordinates"""
        self.camera.follow_target(target_x, target_y, self.trigger_margin)
