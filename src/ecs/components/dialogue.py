from helpers.constants import DEFAULT_TEXT_SPEED_CHAR_PER_SEC
from pygame import Rect

class DialogueComponent:
    """Component for handling dialogue interactions between characters"""
    def __init__(self, text: str):
        self.text = text
        self.chars_per_second = DEFAULT_TEXT_SPEED_CHAR_PER_SEC
        # Runtime state
        self.pages = []
        self.current_page = 0
        self.visible_chars = 0
        self.timer = 0
        self.finished_page = False

class DialogueBoxComponent:
    """Component to hold text from dialogues"""
    def __init__(self, rect: Rect):
        self.rect = rect