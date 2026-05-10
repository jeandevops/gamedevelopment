# gamedevelopment
This repo was made to store game development assets using (or trying to) ECS architecture

Wanna see about how it works? Got to ./docs/

@TODOs:
- Fix the DRY over the run.py related to the FPS treatment, maybe implemented at the main class Game something like:
    ```
    def _render_base(self, delta_time: float):
        """Common rendering pipeline for all game modes"""
        self.systems["character_animation_system"].update()
        self.screen.fill((114, 117, 27))         # Fill with color #72751B
        self.systems["animation_system"].animate(delta_time=delta_time)
        self.systems["rendering_system"].render()
        pygame.display.update()

    def _run_fixed_timestep_loop(self, update_callback, condition_func):
        """
        Common fixed timestep loop pattern.
        
        Args:
            update_callback: Function that takes delta_time and updates physics/logic
            condition_func: Function that returns True while loop should run
        """
        clock = pygame.time.Clock()
        _FIXED_DELTA_TIME = 1.0 / FPS
        time_accumulator = 0.0

        while condition_func():
            milliseconds_elapsed = clock.tick(FPS)
            delta_time = milliseconds_elapsed / 1000.0
            time_accumulator += delta_time
            
            yield delta_time, time_accumulator, _FIXED_DELTA_TIME
    ```
    And instead in the game loops of:
    ```
    while self.state_manager.get_state() == "BATTLE_STARTED":
            # Get elapsed time since last frame and limit to target FPS
            milliseconds_elapsed = clock.tick(FPS)
            delta_time = milliseconds_elapsed / 1000.0
    ```
    Whe should implement this:
    ```
    for delta_time, time_accumulator, _FIXED_DELTA_TIME in self._run_fixed_timestep_loop(
            None,
            lambda: self.state_manager.get_state() == "PLAYING"
        ):
    ```
    Also the condition to render based in the time accumulator changes from this:
    ```
    while time_accumulator >= _FIXED_DELTA_TIME:
        self._render(delta_time)
        time_accumulator -= _FIXED_DELTA_TIME
    ```
    To this:
    ```
    accumulator_remaining = time_accumulator
    while accumulator_remaining >= _FIXED_DELTA_TIME:
        self._render_battle(delta_time)
        accumulator_remaining -= _FIXED_DELTA_TIME
    ```
- Fix the code architecture