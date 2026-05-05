from helpers.constants import PLAYER_SPEED
from ecs.entity_manager import EntityManager
from helpers.game_state_manager import GameStateManager
import pygame
from pygame.locals import QUIT, K_w, K_s, K_a, K_d, K_q, K_k
from sys import exit
from abc import ABC, abstractmethod


class EventHandlerSystem(ABC):
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    @abstractmethod
    def process_events(self, events):
        """Processes input events and updates player velocity"""
        raise NotImplementedError("Subclasses must implement this method")

class WorldEventHandlerSystem(EventHandlerSystem):
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    def process_events(self, events):
        """Processes input events and updates player velocity"""

        for event in events:
            if event.type == QUIT:
                pygame.quit()
                exit()

        # Get player entity
        player = self.entity_manager.get_entity_by_id("player")
        if player is None:
            return


        
        player_velocity = player["velocity"]
        
        # Check which keys are currently pressed
        keys = pygame.key.get_pressed()

        # Reset velocity
        vx = 0
        vy = 0

        # Update velocity based on currently pressed keys
        if keys[K_w]:
            vy = -PLAYER_SPEED
        if keys[K_s]:
            vy = PLAYER_SPEED
        if keys[K_a]:
            vx = -PLAYER_SPEED
        if keys[K_d]:
            vx = PLAYER_SPEED
        if keys[K_q]:
            pygame.quit()
            exit()

        # Set the velocity
        player_velocity.set_velocity(vx, vy)
        
class BattleEventHandlerSystem(EventHandlerSystem):
    def __init__(self, entity_manager: EntityManager, state_manager: GameStateManager):
        self.entity_manager = entity_manager
        self.state_manager = state_manager
        self.last_attack_time = 0
        self.attack_cooldown = 0.5  # 0.5 second cooldown between attacks

    def process_events(self, events):
        """Processes input events during battle (for testing, allows insta-kill enemy)"""
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()
        if keys[K_q]:
            pygame.quit()
            exit()
        
        # Insta-kill enemy for testing (with cooldown):
        if keys[K_k]:
            import time
            current_time = time.time()
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.last_attack_time = current_time
                current_enemy_id = self.state_manager.get_current_enemy()
                if current_enemy_id:
                    enemy = self.entity_manager.get_entity_by_id(current_enemy_id)
                    if enemy and "hp" in enemy:
                        enemy["hp"].take_damage(10)
                        if not enemy["hp"].is_alive():
                            self.entity_manager.delete_entity(current_enemy_id)
                            self.state_manager.change_state("PLAYING")

class DialogEventHandlerSystem(EventHandlerSystem):
    def __init__(self, entity_manager: EntityManager, state_manager: GameStateManager):
        self.entity_manager = entity_manager
        self.state_manager = state_manager
        self.last_talk_time = 0
        self.talk_cooldown = 0.5  # 0.5 second cooldown between button presses

    def process_events(self, events, interlocutor_id: str):
        """Processes input events during dialogue interactions.
        
        Handles advancing through dialogue pages when the player presses the confirmation button.
        When dialogue is finished, transitions back to the appropriate game state.
        
        Args:
            events: pygame events list
            interlocutor_id: The ID of the entity the player is talking to
        """
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()
        if keys[K_q]:
            pygame.quit()
            exit()

        # Get the interlocutor entity
        interlocutor = self.entity_manager.get_entity_by_id(interlocutor_id)
        if not interlocutor:
            raise RuntimeError(f"Interlocutor with ID '{interlocutor_id}' not found, cannot process dialogue events")
        
        # Check if interlocutor has dialogue component
        if "dialogue" not in interlocutor:
            return
        
        dialogue = interlocutor["dialogue"]
        
        # Check if interlocutor has dialogue_box component (needed for text rendering)
        if "dialogue_box" not in interlocutor:
            return
        
        # Handle confirmation button press (K_k) to advance dialogue
        if keys[K_k]:
            import time
            current_time = time.time()
            if current_time - self.last_talk_time >= self.talk_cooldown:
                self.last_talk_time = current_time
                
                # If page not fully shown, show it all
                if not dialogue.finished_page:
                    dialogue.visible_chars = self._page_length(dialogue)
                    dialogue.finished_page = True
                # If page is fully shown, go to next page
                else:
                    if dialogue.current_page < len(dialogue.pages) - 1:
                        # Go to next page
                        dialogue.current_page += 1
                        dialogue.visible_chars = 0
                        dialogue.finished_page = False
                        dialogue.timer = 0
                    else:
                        # Dialogue is over, transition back to battle state
                        self.state_manager.change_state("BATTLE_STARTED")

    def _page_length(self, dialogue):
        """Calculate the number of characters on the current page."""
        if not dialogue.pages or dialogue.current_page >= len(dialogue.pages):
            return 0
        page = dialogue.pages[dialogue.current_page]
        return sum(len(line) for line in page)