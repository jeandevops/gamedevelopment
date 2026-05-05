from helpers.bitmap_font_loader import BitmapFont
from ecs.entity_manager import EntityManager

class DialoguePreparation:
    def __init__(self, font: BitmapFont):
        self.font = font

    def _wrap_text(self, text, rect) -> list[str]:
        words = text.split(" ")
        lines = []
        current_line = ""

        max_chars = rect.width // self.font.char_width

        for word in words:
            test = current_line + (" " if current_line else "") + word

            if len(test) <= max_chars:
                current_line = test
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def _paginate(self, lines, rect) -> list[list[str]]:
        max_lines = rect.height // self.font.char_height

        pages = []
        for i in range(0, len(lines), max_lines):
            pages.append(lines[i:i + max_lines])

        return pages

    def run(self, entity_manager: EntityManager, entity_id: str):
        talking_entity = entity_manager.get_entity_by_id(entity_id)
        if not talking_entity:
            raise ValueError(f"Entity with ID '{entity_id}' not found in EntityManager, cannot prepare dialogue")
        
        if "dialogue" in talking_entity and "dialogue_box" in talking_entity:
            if not talking_entity["dialogue"].pages:  # only prepare once
                lines = self._wrap_text(talking_entity["dialogue"].text, talking_entity["dialogue_box"].rect)
                talking_entity["dialogue"].pages = self._paginate(lines, talking_entity["dialogue_box"].rect)

class DialogueSystem:
    def run(self, entities, dt):
        """Legacy method for updating dialogue with typewriter effect. 
        
        Args:
            entities: List of entities with dialogue components
            dt: Delta time since last update in seconds
        """
        for e in entities:
            if not hasattr(e, "dialogue"):
                continue

            d = e.dialogue

            if d.finished_page:
                continue

            d.timer += dt
            char_delay = 1.0 / d.chars_per_second

            while d.timer >= char_delay:
                d.timer -= char_delay
                d.visible_chars += 1

                if d.visible_chars >= self.page_length(d):
                    d.visible_chars = self.page_length(d)
                    d.finished_page = True
                    break
    
    def update(self, entity_manager: 'EntityManager', dt: float) -> None:
        """Update dialogue typewriter effect for all entities with dialogue components.
        
        Advances the visible character count over time to create a typewriter effect.
        
        Args:
            entity_manager: The EntityManager instance containing dialogue entities
            dt: Delta time since last update in seconds
        """
        # Get all entities with dialogue components
        dialogue_entities = entity_manager.get_entities_with_components(["dialogue", "dialogue_box"])
        
        for entity_id, components in dialogue_entities:
            d = components["dialogue"]
            
            # Skip if page is already fully shown
            if d.finished_page:
                continue
            
            # Skip if no pages yet
            if not d.pages:
                continue
            
            # Update timer and show more characters
            d.timer += dt
            char_delay = 1.0 / d.chars_per_second
            
            while d.timer >= char_delay:
                d.timer -= char_delay
                d.visible_chars += 1
                
                # Check if we've shown all characters on this page
                if d.visible_chars >= self.page_length(d):
                    d.visible_chars = self.page_length(d)
                    d.finished_page = True
                    break

    def page_length(self, d):
        """Calculate the total number of characters on a page."""
        if not d.pages or d.current_page >= len(d.pages):
            return 0
        page = d.pages[d.current_page]
        return sum(len(line) for line in page)