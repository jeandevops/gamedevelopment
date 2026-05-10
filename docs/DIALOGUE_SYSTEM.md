# Dialogue System Architecture

## Overview

The Dialogue System is a complete ECS-based implementation for displaying character dialogue with a typewriter effect. It allows NPCs and enemies to display text pages with character-by-character animation when entering dialogue state.

## Core Components

### 1. DialogueComponent
**Location:** `src/ecs/components/dialogue.py`

Stores the dialogue state and pagination information for a single entity.

**Properties:**
- `text` (str): The raw dialogue text
- `chars_per_second` (int): Animation speed (default: 60 characters/second)
- `pages` (list[list[str]]): Paginated text (initialized by DialoguePreparation)
- `current_page` (int): Current page being displayed
- `visible_chars` (int): Number of visible characters on current page
- `timer` (float): Time accumulator for typewriter animation
- `finished_page` (bool): Whether current page is fully displayed

### 2. DialogueBoxComponent
**Location:** `src/ecs/components/dialogue.py`

Defines the rectangular area where dialogue text will be rendered.

**Properties:**
- `rect` (pygame.Rect): The rendering rectangle (x, y, width, height)

## Core Systems

### 1. DialoguePreparation
**Location:** `src/ecs/systems/text_system.py`

Prepares dialogue for display by wrapping text and creating pages.

**Key Methods:**
- `run(entity_manager, entity_id)`: Wraps text to fit box width and paginates to fit box height
- `_wrap_text(text, rect)`: Wraps dialogue text to fit within rectangle width
- `_paginate(lines, rect)`: Splits wrapped lines into pages based on rectangle height

**Usage:**
```python
dialogue_prep = DialoguePreparation(font)
dialogue_prep.run(entity_manager, enemy_id)
```

### 2. DialogueSystem
**Location:** `src/ecs/systems/text_system.py`

Updates the typewriter animation by advancing the visible character count.

**Key Methods:**
- `update(entity_manager, dt)`: Updates all dialogue animations for entities with dialogue components
  - `entity_manager`: EntityManager instance
  - `dt`: Delta time in seconds
- `page_length(dialogue)`: Returns total character count for current page

**How it works:**
- Accumulates `dt` in `dialogue.timer`
- When timer exceeds `1.0 / chars_per_second`, increments `visible_chars` and resets timer
- Sets `finished_page = True` when all characters are visible
- Respects the `chars_per_second` setting for animation speed

### 3. DialogEventHandlerSystem
**Location:** `src/ecs/systems/event_handler_system.py`

Handles keyboard input during dialogue interactions.

**Key Methods:**
- `process_events(events, interlocutor_id)`: Processes dialogue input
  - Detects confirmation button press (K_k)
  - Advances to next page or shows all text on current page
  - Transitions to BATTLE_STARTED when dialogue ends

**Behavior:**
- If page not fully shown: Shows all remaining text on press
- If page fully shown: Advances to next page
- If on last page: Transitions to BATTLE_STARTED state

**Cooldown:** 0.5 seconds between button presses

## Game States

### State Transitions

```
PLAYING (world exploration)
    ↓
BATTLE_BEGIN (collision with enemy)
    ↓ (if enemy has dialogue)
DIALOGUE (show enemy dialogue)
    ↓ (when dialogue ends)
BATTLE_STARTED (begins combat)
    ↓ (when battle ends)
PLAYING (return to exploration)
```

### DIALOGUE State Flow

1. **Setup Phase (BATTLE_BEGIN)**
   - Create battle camera
   - Check if enemy has dialogue
   - If yes: Create dialogue box and prepare dialogue
   - Transition to DIALOGUE state

2. **Dialogue Phase (DIALOGUE)**
   - DialogueSystem updates typewriter animation
   - RenderingSystem renders visible text
   - DialogEventHandlerSystem handles page advancement
   - When all pages shown: Transition to BATTLE_STARTED

## Data Flow

### 1. Enemy Creation
```
forest.json → EnemiesFactory
    ↓
Creates DialogueComponent with text from "dialogue" field
```

**Example forest.json:**
```json
{
  "enemies": [
    {
      "type": "orc",
      "position": {"x": 300, "y": 300},
      "dialogue": "Grrr! You are not welcome here! Leave this forest or face my wrath!"
    }
  ]
}
```

### 2. Dialogue Preparation
```
DialoguePreparation.run() →
  1. Gets entity's dialogue text
  2. Wraps text to fit DialogueBoxComponent width
  3. Paginates lines to fit box height
  4. Stores pages in dialogue.pages
```

### 3. Dialogue Rendering
```
DialogueSystem.update() →
  Advances visible_chars at specified speed

RenderingSystem._render_dialogues() →
  1. Gets all entities with dialogue and dialogue_box
  2. Gets current page text
  3. For each character in visible_chars:
      - Looks up bitmap font glyph
      - Renders at calculated position
```

## Bitmap Font System

### BitmapFont
**Location:** `src/helpers/bitmap_font_loader.py`

Loads characters from a sprite sheet and provides rendering glyphs.

**Initialization:**
```python
font = BitmapFont(
    image_path="assets/text/8x8text_darkGrayShadow.png",
    char_width=8,
    char_height=8,
    chars_order=r"~1234567890-+!@#$%^&*()_={}[]|\\:;\"'<,>.?/ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
)
```

**Properties:**
- `image` (pygame.Surface): Sprite sheet surface
- `char_width` (int): Width of each character in pixels
- `char_height` (int): Height of each character in pixels
- `chars` (dict): Mapping of character → pygame.Surface (pre-extracted glyphs)

## Integration with Game Loop

### SystemManager
- Creates and manages all systems including DialogueSystem
- Provides systems to different game modes via getter methods

### DialogGame
- Main game loop for dialogue state
- Updates dialogue animation and renders scene
- Delegates input handling to DialogEventHandlerSystem

**Main loop:**
```python
while state == "DIALOGUE":
    # Handle input
    event_handler.process_events(events, interlocutor_id)
    
    # Update animation
    dialogue_system.update(entity_manager, dt)
    
    # Render
    rendering_system.render()
```

## Configuration Constants

**Location:** `src/helpers/constants.py`

- `DEFAULT_TEXT_SPEED_CHAR_PER_SEC`: Animation speed (default: 60)
- `TEXT_SPRITES_PATH`: Path to bitmap font sprite sheet
- `TILE_SIZE`: Used for character dimensions in dialogue positioning

## Creating Dialogues in Map Files

Add dialogue to enemies in the map JSON:

```json
{
  "enemies": [
    {
      "type": "orc",
      "position": {"x": 300, "y": 300},
      "dialogue": "Your dialogue text here. It will be automatically wrapped and paginated."
    }
  ]
}
```

## Performance Considerations

1. **Text Wrapping:** Done once during DialoguePreparation
2. **Character Lookup:** O(1) hash lookup in font.chars dict
3. **Rendering:** Only visible characters are rendered each frame
4. **Camera Culling:** Dialogue boxes outside camera viewport are skipped

## Extending the System

### Adding Dialogue Effects

To add effects like color, style, or sound:

1. Extend DialogueComponent with metadata
2. Modify text_system.py to parse special formatting
3. Update RenderingSystem._render_dialogues() to apply effects

### Multiple Dialogue Tracks

For multi-character conversations:

1. Create separate DialogueComponent for each speaker
2. Track which speaker is currently talking
3. Render appropriate dialogue box and text

### Dialogue Choices

To implement branching dialogue:

1. Extend DialogueComponent with choice_pages list
2. Modify DialogEventHandlerSystem to show choices
3. Update dialogue.pages based on player selection

## Troubleshooting

### Dialogue Not Appearing
- Check that enemy has "dialogue" component
- Verify DialogueBoxComponent was created
- Ensure BitmapFont loaded correctly
- Check that text is not empty

### Text Rendering Issues
- Verify character exists in font.chars
- Check bitmap font sprite sheet dimensions
- Ensure char_width and char_height match sprite sheet
- Verify chars_order string contains all needed characters

### Animation Not Working
- Check that DialogueSystem.update() is called with valid dt
- Verify chars_per_second is not zero
- Check that DialoguePreparation.run() was called

## Testing Dialogue

1. **Manual Testing:**
   - Launch game and approach enemy
   - Verify dialogue box appears
   - Check text animation
   - Test page advancement with K key
   - Verify battle starts after dialogue

2. **Unit Testing:**
   - Test text wrapping with various widths
   - Test pagination with various heights
   - Test visible_chars increment
   - Test page transitions

## Example Workflow

1. **Enemy Definition (forest.json):**
```json
"enemies": [
  {
    "type": "orc",
    "position": {"x": 300, "y": 300},
    "dialogue": "Grrr! You dare enter my forest? Prepare to face my wrath!"
  }
]
```

2. **Collision Detection:**
Player collides with enemy → `state_manager.start_battle(enemy_id)`

3. **Battle Begin:**
- Check if enemy has dialogue
- Create dialogue box on enemy
- Call `DialoguePreparation(font).run(entity_manager, enemy_id)`
- Call `state_manager.start_conversation(enemy_id)`
- Transition to DIALOGUE state

4. **Dialogue Display:**
- DialogGame.main_loop() runs
- DialogueSystem animates text
- RenderingSystem renders scene with dialogue
- DialogEventHandlerSystem handles input

5. **Dialogue Completion:**
- Player presses K after all pages shown
- DialogEventHandlerSystem transitions to BATTLE_STARTED
- Battle begins with HUD created
