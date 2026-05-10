# Bitmap Font and Text Rendering Guide

## Overview

The text rendering system uses bitmap fonts (sprite sheets) to display dialogue. Each character is pre-extracted from a sprite sheet and cached for efficient rendering.

## Bitmap Font System

### Loading a Bitmap Font

**BitmapFont Class** (`src/helpers/bitmap_font_loader.py`)

```python
from helpers.bitmap_font_loader import BitmapFont

font = BitmapFont(
    image_path="assets/text/8x8text_darkGrayShadow.png",
    char_width=8,
    char_height=8,
    chars_order=r"~1234567890-+!@#$%^&*()_={}[]|\\:;\"'<,>.?/ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
)
```

### Parameters

- **image_path** (str): Path to sprite sheet image file
  - Relative to project root
  - Supports PNG, JPG, and other pygame-supported formats
  
- **char_width** (int): Width of each character tile in pixels
  - Must match actual sprite dimensions
  - Default: 8 pixels
  
- **char_height** (int): Height of each character tile in pixels
  - Must match actual sprite dimensions
  - Default: 8 pixels
  
- **chars_order** (str): String defining character order in sprite sheet
  - Characters read left-to-right, top-to-bottom
  - First character is at (0, 0)
  - Second character is at (char_width, 0)
  - When sprite sheet width is exceeded, wraps to next row

### Character Extraction Algorithm

The BitmapFont extracts character glyphs from the sprite sheet:

```python
sheet_width = image.get_width()

for index, char in enumerate(chars_order):
    # Calculate position in sprite sheet
    x = (index * char_width) % sheet_width
    y = (index * char_width) // sheet_width * char_height
    
    # Extract character surface
    rect = pygame.Rect(x, y, char_width, char_height)
    chars[char] = image.subsurface(rect)
```

### Example Sprite Sheet Layout

For a sprite sheet of width 288 pixels with 8x8 characters:

```
Row 0: ~ 1 2 3 4 5 6 7 8 9 0 - + ! @ # $ % ^ & * ( ) _ = { } [ ] | \ : ; " ' < , > . ? /
Row 1: A B C D E F G H I J K L M N O P Q R S T U V W X Y Z a b c d e f g h i j k l m n o
Row 2: p q r s t u v w x y z ...
```

In this case:
- Characters 0-35 (row 0): Special characters and digits
- Characters 36-61 (row 1): Uppercase letters
- Characters 62-87 (row 2): Lowercase letters

### Font Properties

After loading, the font object contains:

```python
font.image          # pygame.Surface - the sprite sheet
font.char_width     # int - width of each glyph
font.char_height    # int - height of each glyph
font.chars          # dict[str, pygame.Surface] - character glyphs
```

## Text Rendering in Dialogue

### RenderingSystem Dialogue Rendering

**Method:** `RenderingSystem._render_dialogues()`

The rendering system handles displaying dialogue text on screen:

```python
def _render_dialogues(self):
    """Render dialogue text for all entities with dialogue components"""
    dialogue_entities = entity_manager.get_entities_with_components(
        ["dialogue", "dialogue_box"]
    )
    
    for entity_id, components in dialogue_entities:
        dialogue = components["dialogue"]
        dialogue_box = components["dialogue_box"]
        
        # Each line of current page
        for line_idx, line in enumerate(current_page):
            y_offset = line_idx * font.char_height
            
            # Each character in line
            for char_idx in range(visible_in_line):
                char = line[char_idx]
                if char not in font.chars:
                    continue
                
                x_offset = char_idx * font.char_width
                screen_x = dialogue_box.rect.x + x_offset - camera.x
                screen_y = dialogue_box.rect.y + y_offset - camera.y
                
                # Blit character surface to screen
                screen.blit(font.chars[char], (screen_x, screen_y))
```

### Text Wrapping Algorithm

**DialoguePreparation._wrap_text()**

Text is wrapped to fit within the dialogue box width:

```python
def _wrap_text(self, text, rect) -> list[str]:
    words = text.split(" ")
    lines = []
    current_line = ""
    
    # Maximum characters per line
    max_chars = rect.width // self.font.char_width
    
    for word in words:
        test = current_line + (" " if current_line else "") + word
        
        if len(test) <= max_chars:
            current_line = test
        else:
            # Word too long or line complete
            lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines
```

**Example:**
- Dialogue box width: 100 pixels
- Character width: 8 pixels
- Max characters per line: 100 / 8 = 12 characters
- Text: "You dare enter my forest?"
- Result:
  ```
  "You dare"
  "enter my"
  "forest?"
  ```

### Text Pagination Algorithm

**DialoguePreparation._paginate()**

Wrapped lines are paginated to fit within the dialogue box height:

```python
def _paginate(self, lines, rect) -> list[list[str]]:
    max_lines = rect.height // self.font.char_height
    
    pages = []
    for i in range(0, len(lines), max_lines):
        pages.append(lines[i:i + max_lines])
    
    return pages
```

**Example:**
- Dialogue box height: 48 pixels
- Character height: 8 pixels
- Max lines per page: 48 / 8 = 6 lines
- Wrapped text (6 lines)
- Result: [page1 with all 6 lines]

- If 12 lines wrapped:
- Result: [page1 with 6 lines, page2 with 6 lines]

### Typewriter Animation

**DialogueSystem.update()**

The typewriter effect is created by gradually revealing characters:

```python
def update(self, entity_manager, dt):
    dialogue_entities = entity_manager.get_entities_with_components(
        ["dialogue", "dialogue_box"]
    )
    
    for entity_id, components in dialogue_entities:
        d = components["dialogue"]
        
        if d.finished_page:
            continue
        
        # Accumulate time
        d.timer += dt
        char_delay = 1.0 / d.chars_per_second
        
        # Show more characters when delay is exceeded
        while d.timer >= char_delay:
            d.timer -= char_delay
            d.visible_chars += 1
            
            if d.visible_chars >= self.page_length(d):
                d.visible_chars = self.page_length(d)
                d.finished_page = True
                break
```

**Timeline Example** (chars_per_second = 10):
- t=0.00s: visible_chars=0
- t=0.10s: visible_chars=1
- t=0.20s: visible_chars=2
- t=0.30s: visible_chars=3
- ...
- t=1.50s: visible_chars=15

## Coordinate System

### Dialogue Box World Coordinates

The dialogue box starts at world coordinates:

```python
# In HUDFactory.create_dialogue_box()
dialogue_x = enemy_x + 16 - (box_width // 2)  # Center horizontally
dialogue_y = enemy_y - 96                      # Above enemy's head
```

### Screen Space Conversion

Coordinates are converted to screen space for rendering:

```python
screen_x = dialogue_box.rect.x + char_x_offset - camera.x
screen_y = dialogue_box.rect.y + char_y_offset - camera.y
```

Where:
- `dialogue_box.rect.x/y`: Top-left of dialogue box in world space
- `char_x_offset`: Character column × char_width
- `char_y_offset`: Character row × char_height
- `camera.x/y`: Camera position in world space

## Font Configuration

### Default Font Settings

In game initialization (`src/run.py`):

```python
font = BitmapFont(
    image_path=TEXT_SPRITES_PATH,  # "assets/text/8x8text_darkGrayShadow.png"
    char_width=8,
    char_height=8,
    chars_order=r"~1234567890-+!@#$%^&*()_={}[]|\\:;\"'<,>.?/ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
)
```

### Available Characters

The default font includes:

- **Special characters:** ~ ! @ # $ % ^ & * ( ) - + = { } [ ] | \ : ; " ' < > , . ? /
- **Digits:** 0-9
- **Uppercase:** A-Z
- **Lowercase:** a-z

### Character Limitations

- Only characters in `chars_order` can be rendered
- Unknown characters are skipped silently during rendering
- Common unsupported: Accented characters, Asian characters, emoji

## Creating Custom Fonts

### 1. Prepare Sprite Sheet

Create a PNG with characters arranged in a grid:
- One character per cell
- Cells are char_width × char_height pixels
- Characters read left-to-right, top-to-bottom
- No gaps between cells

### 2. Define Character Order

Create a string with characters in sprite sheet order:

```python
my_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!?. -"
```

### 3. Load Font

```python
custom_font = BitmapFont(
    image_path="assets/fonts/my_custom_font.png",
    char_width=16,  # Adjust to sprite size
    char_height=16,
    chars_order=my_chars
)
```

## Performance Tips

1. **Font Caching:** Font is created once and reused - no per-frame overhead
2. **Character Lookup:** Using dict for O(1) glyph lookup
3. **Rendering Optimization:**
   - Only visible characters are rendered
   - Only visible lines are processed
   - Screen boundary checking prevents off-screen rendering
4. **Memory:** Each font glyph stored as subsurface (references sprite sheet, not copies)

## Debugging Text Rendering

### Character Not Rendering

1. Check if character exists in chars_order:
```python
if char not in font.chars:
    print(f"Character '{char}' not in font")
```

2. Verify sprite sheet dimensions match char_width/height

3. Check that dialogue box is within screen bounds:
```python
if screen_x < 0 or screen_x > screen.get_width():
    print(f"Outside screen: x={screen_x}")
```

### Wrapping Issues

1. Verify dialogue box width allows at least one character:
```python
max_chars = box_width // char_width
if max_chars < 1:
    print(f"Box too narrow for {char_width}px characters")
```

2. Check that words can fit:
```python
for word in text.split():
    if len(word) * char_width > box_width:
        print(f"Word '{word}' exceeds box width")
```

### Animation Too Fast/Slow

Adjust chars_per_second:
```python
dialogue.chars_per_second = 30  # Slower
dialogue.chars_per_second = 120 # Faster
```

## Integration Checklist

- [ ] Bitmap font file exists at specified path
- [ ] char_width matches sprite sheet cell width
- [ ] char_height matches sprite sheet cell height
- [ ] chars_order includes all required characters
- [ ] Dialogue boxes have sufficient width (at least 1 character)
- [ ] Dialogue boxes have sufficient height (at least 1 line)
- [ ] Camera coordinate conversion is correct
- [ ] Font passed to RenderingSystem during initialization

## Technical Details

### Sprite Subsurface Behavior

PyGame's `subsurface()` returns references to regions of the original surface:
- Non-copying (efficient memory usage)
- Updates to original affect subsurfaces
- Cannot create subsurfaces of subsurfaces (copy if needed)

### Coordinate Precision

Coordinates are kept as floats during calculation. PyGame's blit expects integers:
```python
screen.blit(surface, (int(x), int(y)))  # Recommended
```

Floating point errors are usually negligible with proper camera interpolation.
