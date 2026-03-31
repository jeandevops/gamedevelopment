class AIBehaviorComponent:
    def __init__(self, behavior_type: str, vision_range: int, interaction_range: int, aggressive: bool = False, wander_speed: int = 0, chase_speed: int = 0):
        self.behavior_type = behavior_type
        self.aggressive = aggressive
        self.vision_range = vision_range
        self.interaction_range = interaction_range
        self.wander_speed = wander_speed
        self.chase_speed = chase_speed