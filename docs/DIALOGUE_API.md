# Dialogue System API Reference

## Components

### DialogueComponent
**File:** `src/ecs/components/dialogue.py`

```python
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
```

**Usage:**
```python
dialogue = DialogueComponent("Hello, adventurer!")
entity["dialogue"] = dialogue
```

**Modifying Display Speed:**
```python
enemy["dialogue"].chars_per_second = 30  # Slower animation
```

### DialogueBoxComponent
**File:** `src/ecs/components/dialogue.py`

```python
class DialogueBoxComponent:
    """Component to hold text rendering rectangle from dialogues"""
    
    def __init__(self, rect: Rect):
        self.rect = rect
```

**Usage:**
```python
import pygame
dialogue_box = DialogueBoxComponent(pygame.Rect(x=100, y=100, width=200, height=64))
entity["dialogue_box"] = dialogue_box
```

## Systems

### DialoguePreparation
**File:** `src/ecs/systems/text_system.py`

**Initialization:**
```python
from helpers.bitmap_font_loader import BitmapFont
from ecs.systems.text_system import DialoguePreparation

font = BitmapFont(...)
dialogue_prep = DialoguePreparation(font)
```

**Methods:**

#### run(entity_manager, entity_id)
Prepares an entity's dialogue for display.

```python
dialogue_prep.run(entity_manager, "enemy_1")
```

**What it does:**
1. Gets entity's dialogue and dialogue_box components
2. Wraps dialogue text to fit box width
3. Paginates wrapped text to fit box height
4. Stores pages in `dialogue.pages`

**Required:**
- Entity must have both "dialogue" and "dialogue_box" components
- dialogue.text must be a non-empty string
- dialogue_box.rect must have positive width and height

**Raises:**
- ValueError if entity not found
- ValueError if components missing

### DialogueSystem
**File:** `src/ecs/systems/text_system.py`

```python
from ecs.systems.text_system import DialogueSystem

dialogue_system = DialogueSystem()
```

**Methods:**

#### update(entity_manager, dt)
Updates all active dialogues with typewriter animation.

```python
dialogue_system.update(entity_manager, delta_time)
```

**Parameters:**
- `entity_manager`: EntityManager instance with dialogue entities
- `dt`: Delta time in seconds (float)

**Effect:**
- Advances `visible_chars` based on `chars_per_second`
- Sets `finished_page = True` when page complete
- Respects entity's `chars_per_second` setting

**Optimization:**
- Skips entities with `finished_page = True`
- Skips entities without pages

### DialogEventHandlerSystem
**File:** `src/ecs/systems/event_handler_system.py`

```python
from ecs.systems.event_handler_system import DialogEventHandlerSystem

handler = DialogEventHandlerSystem(entity_manager, state_manager)
```

**Methods:**

#### process_events(events, interlocutor_id)
Processes player input during dialogue.

```python
events = pygame.event.get()
handler.process_events(events, "enemy_1")
```

**Parameters:**
- `events`: List of pygame events
- `interlocutor_id`: Entity ID of dialogue participant

**Input Handling:**
- **K_k (Confirmation Button):**
  - If page not complete: Shows all remaining text
  - If page complete: Advance to next page
  - On last page: Transition to BATTLE_STARTED
- **K_q (Quit):** Exits game
- **QUIT event:** Exits game

**Cooldown:** 0.5 seconds between button presses

## Factories

### HUDFactory
**File:** `src/world/hud_factory.py`

```python
from world.hud_factory import HUDFactory
```

**Methods:**

#### create_dialogue_box(entity_manager, enemy_id, box_width=100, box_height=48)
Creates a dialogue box for an enemy entity.

```python
HUDFactory.create_dialogue_box(entity_manager, "enemy_1")
```

**Parameters:**
- `entity_manager`: EntityManager instance
- `enemy_id`: ID of enemy entity
- `box_width`: Dialogue box width in pixels (default: 100)
- `box_height`: Dialogue box height in pixels (default: 48)

**Effect:**
- Positions box above enemy's head
- Centers box horizontally on enemy
- Creates `dialogue_box` component on enemy entity

**Position Calculation:**
```python
# Horizontal: centered on enemy (enemy center - box half-width)
dialogue_x = enemy_x + 16 - (box_width // 2)

# Vertical: 3 character lines above enemy head
dialogue_y = enemy_y - 96
```

**Requires:**
- Enemy must have "position" component
- Enemy must have "dialogue" component

#### create_battle_hud(entity_manager, enemy_id)
Creates HP bars for battle HUD.

```python
HUDFactory.create_battle_hud(entity_manager, "enemy_1")
```

**Creates:**
- Enemy HP bar at offset position
- Enemy HP bar background
- Player HP bar at offset position
- Player HP bar background

## Game State Manager

### GameStateManager
**File:** `src/helpers/game_state_manager.py`

```python
from helpers.game_state_manager import GameStateManager

state_manager = GameStateManager()
```

**Game States:**
- `"PLAYING"`: World exploration
- `"BATTLE_BEGIN"`: Battle setup phase
- `"DIALOGUE"`: Dialogue display phase
- `"BATTLE_STARTED"`: Active combat

**Methods:**

#### start_battle(enemy_id) → str
Transition to battle and set current enemy.

```python
state_manager.start_battle("enemy_1")  # Returns enemy_id
```

#### start_conversation(interlocutor_id)
Transition to dialogue state.

```python
state_manager.start_conversation("enemy_1")
```

#### get_current_enemy() → str | None
Get ID of current battle enemy.

```python
enemy_id = state_manager.get_current_enemy()
```

#### get_current_interlocutor() → str | None
Get ID of current dialogue participant.

```python
interlocutor_id = state_manager.get_current_interlocutor()
```

## Rendering System

### RenderingSystem
**File:** `src/ecs/systems/render_system.py`

```python
from ecs.systems.render_system import RenderingSystem

renderer = RenderingSystem(screen, entity_manager, camera, font)
```

**Constructor:**
```python
def __init__(self, 
             screen: pygame.Surface,
             entity_manager: EntityManager,
             camera_component: CameraComponent,
             font=None):
```

**Methods:**

#### render()
Renders entire scene including dialogues.

```python
renderer.render()
```

**Rendering Order:**
1. Non-collision tiles (background)
2. Collision tiles and characters (depth-sorted by Y)
3. HUD elements (HP bars)
4. Dialogue text (if font available)

### Adding Font to RenderingSystem

```python
from helpers.bitmap_font_loader import BitmapFont
from ecs.systems.render_system import RenderingSystem

font = BitmapFont(...)
renderer = RenderingSystem(screen, entity_manager, camera, font)
```

## Complete Workflow Example

### 1. Initialize Systems

```python
from helpers.bitmap_font_loader import BitmapFont
from ecs.systems.text_system import DialoguePreparation, DialogueSystem
from ecs.systems.event_handler_system import DialogEventHandlerSystem
from ecs.systems.render_system import RenderingSystem
from world.hud_factory import HUDFactory

font = BitmapFont(
    image_path="assets/text/8x8text_darkGrayShadow.png",
    char_width=8,
    char_height=8,
    chars_order="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
)

dialogue_prep = DialoguePreparation(font)
dialogue_system = DialogueSystem()
event_handler = DialogEventHandlerSystem(entity_manager, state_manager)
renderer = RenderingSystem(screen, entity_manager, camera, font)
```

### 2. Create Enemy with Dialogue

```python
from ecs.components.dialogue import DialogueComponent

# In EnemiesFactory or elsewhere
enemy_entity = {
    "position": PositionComponent(x=300, y=300),
    "dialogue": DialogueComponent("Grrr! Prepare to fight!"),
    # ... other components
}
entity_manager.add_entity("enemy_1", enemy_entity)
```

### 3. Trigger Dialogue

```python
# When player collides with enemy
state_manager.start_battle("enemy_1")

# In BATTLE_BEGIN state
enemy = entity_manager.get_entity_by_id("enemy_1")
if "dialogue" in enemy and enemy["dialogue"].text:
    # Setup dialogue
    HUDFactory.create_dialogue_box(entity_manager, "enemy_1")
    dialogue_prep.run(entity_manager, "enemy_1")
    state_manager.start_conversation("enemy_1")
```

### 4. Dialogue Loop

```python
# In DialogGame.main_loop()
while state_manager.get_state() == "DIALOGUE":
    dt = clock.tick(FPS) / 1000.0
    
    # Handle input
    event_handler.process_events(pygame.event.get(), "enemy_1")
    
    # Update animation
    dialogue_system.update(entity_manager, dt)
    
    # Render
    renderer.render()
    pygame.display.update()
```

### 5. Handle Dialogue End

When player advances through all pages:
- DialogEventHandlerSystem automatically transitions to BATTLE_STARTED
- Battle loop begins

## Customization Points

### Changing Text Speed

**Global:**
```python
# In constants.py
DEFAULT_TEXT_SPEED_CHAR_PER_SEC = 30
```

**Per-Dialogue:**
```python
enemy["dialogue"].chars_per_second = 20
```

### Custom Dialogue Box Size

```python
HUDFactory.create_dialogue_box(
    entity_manager, 
    "enemy_1",
    box_width=150,
    box_height=96
)
```

### Custom Font

```python
custom_font = BitmapFont(
    image_path="assets/fonts/my_font.png",
    char_width=16,
    char_height=16,
    chars_order="custom_char_order"
)
renderer = RenderingSystem(screen, entity_manager, camera, custom_font)
```

### Multiple Dialogue Pages

Just use longer text - it will automatically paginate:

```python
long_text = "First page text. " * 20  # Many words
dialogue = DialogueComponent(long_text)
```

The text will be automatically wrapped and paginated based on box dimensions.

## Troubleshooting API

### Entity Not Found

```python
try:
    entity = entity_manager.get_entity_by_id("enemy_1")
    if not entity:
        print("Entity not found")
except Exception as e:
    print(f"Error: {e}")
```

### Missing Components

```python
def check_dialogue_setup(entity_manager, entity_id):
    entity = entity_manager.get_entity_by_id(entity_id)
    
    if "dialogue" not in entity:
        print("Missing dialogue component")
    if "dialogue_box" not in entity:
        print("Missing dialogue_box component")
    if "dialogue" in entity and not entity["dialogue"].pages:
        print("Dialogue not prepared (no pages)")
```

### Dialogue Not Rendering

```python
def check_rendering_setup(renderer):
    if renderer.font is None:
        print("Error: Font not passed to RenderingSystem")
```

### Input Not Working

```python
def check_event_handler(state_manager, entity_manager, entity_id):
    state = state_manager.get_state()
    if state != "DIALOGUE":
        print(f"Not in dialogue state: {state}")
    
    entity = entity_manager.get_entity_by_id(entity_id)
    if "dialogue" not in entity:
        print("Entity has no dialogue component")
