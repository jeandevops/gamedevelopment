class HPComponent:
    def __init__(self, max_hp: int, current_hp: int | None = None):
        """Initializes the HPComponent"""
        self.max_hp: int = max_hp
        self.current_hp: int = current_hp if current_hp is not None else max_hp

    def take_damage(self, damage: int) -> None:
        """Reduces the current HP by the specified damage amount"""
        self.current_hp = max(0, self.current_hp - damage)
    
    def heal(self, amount: int) -> None:
        """Increases the current HP by the specified amount, without exceeding max HP"""
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def is_alive(self) -> bool:
        """Returns True if the entity is alive (current HP > 0), otherwise False"""
        return self.current_hp > 0