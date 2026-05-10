import pygame

class BitmapFont:
    def __init__(self, image_path, char_width, char_height, chars_order):
        """
        image_path: path to sprite sheet
        char_width, char_height: size of each character tile
        chars_order: string with all characters in order in the sheet
                     e.g. "abcdefghijklmnopqrstuvwxyz"
        """
        self.image = pygame.image.load(image_path)
        self.char_width = char_width
        self.char_height = char_height
        self.chars = {}

        self._load_characters(chars_order)

    def _load_characters(self, chars_order):
        sheet_width = self.image.get_width()
        sheet_height = self.image.get_height()

        for index, char in enumerate(chars_order):
            x = (index * self.char_width) % sheet_width
            y = (index * self.char_width) // sheet_width * self.char_height

            # Validate that the character position is within the sprite sheet
            if x + self.char_width > sheet_width or y + self.char_height > sheet_height:
                raise ValueError(
                    f"Character '{char}' at index {index} would be at position ({x}, {y}) "
                    f"with size ({self.char_width}, {self.char_height}), "
                    f"but sprite sheet is only {sheet_width}x{sheet_height} pixels. "
                    f"Sprite sheet can fit {(sheet_width // self.char_width) * (sheet_height // self.char_height)} characters."
                )

            rect = pygame.Rect(x, y, self.char_width, self.char_height)
            self.chars[char] = self.image.subsurface(rect)