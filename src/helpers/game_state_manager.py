class GameStateManager:
    def __init__(self):
        self.state = "PLAYING"  # Default state
        self.enemy_in_battle = None  # Track the current enemy in battle

    def change_state(self, new_state: str) -> None:
        """Change the current game state"""
        self.state = new_state

    def get_state(self) -> str:
        """Get the current game state"""
        return self.state

    def start_battle(self, enemy_id: str) -> str:
        """Transition to battle state and set up necessary components"""
        self.change_state("BATTLE_BEGIN")
        self.enemy_in_battle = enemy_id
        return enemy_id

    def get_current_enemy(self) -> str | None:
        """Get the ID of the current enemy in battle"""
        return self.enemy_in_battle