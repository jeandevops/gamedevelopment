class VelocityComponent:
    def __init__(self, vx: float, vy: float):
        self.vx = vx
        self.vy = vy
    
    def set_velocity(self, vx: float, vy: float) -> None:
        self.vx = vx
        self.vy = vy