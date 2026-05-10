# Quick Start Guide: Adding Dialogue to Your Game

## 1. Define Dialogue in Map File

Edit `src/assets/maps/forest.json`:

```json
{
  "enemies": [
    {
      "type": "orc",
      "position": {"x": 300, "y": 300},
      "dialogue": "Grrr! You dare enter my forest? Prepare to face my wrath!"
    }
  ]
}
```

The dialogue can be a single line or multiple sentences. It will automatically wrap and paginate.

## 2. Run the Game

```bash
cd src
python3 run.py
```

## 3. Test the Dialogue

1. **Approach Enemy:** Walk towards the orc until collision is detected
2. **Dialogue Begins:** Battle begins with dialogue display
3. **Typewriter Effect:** Watch text appear character-by-character
4. **Advance Pages:** Press **K key** to show all text on page
5. **Next Page:** Press **K** again to advance to next page
6. **Battle Starts:** After final page, press **K** to begin battle

## How It Works Behind the Scenes

### Game Flow
```
Player moves → Collides with enemy
     ↓
Battle begins (BATTLE_BEGIN state)
     ↓
If enemy has dialogue:
  - Create dialogue box
  - Prepare text (wrap + paginate)
  - Go to DIALOGUE state
     ↓
DIALOGUE Loop (run.py, DialogGame):
  - Update animation (typewriter)
  - Handle input (K key)
  - Render everything
     ↓
When dialogue ends:
  - Go to BATTLE_STARTED
     ↓
Battle begins
```

### Key Systems

1. **DialoguePreparation** - Wraps text and paginates to fit box
2. **DialogueSystem** - Animates characters appearing
3. **DialogEventHandlerSystem** - Handles K key input
4. **RenderingSystem** - Draws text on screen using bitmap font

## Customization Examples

### Change Text Speed

**Fast:**
```python
enemy["dialogue"].chars_per_second = 120
```

**Slow:**
```python
enemy["dialogue"].chars_per_second = 20
```

**Default:** 60 characters per second

### Larger Dialogue Box

```python
# In HUDFactory.create_dialogue_box() call
HUDFactory.create_dialogue_box(entity_manager, enemy_id, box_width=200, box_height=96)
```

### Multiple Paragraphs

Just write longer text in the map file:

```json
"dialogue": "First paragraph here. Second paragraph here. Third paragraph continues the story. And so on..."
```

The system automatically handles wrapping and pagination.

## Troubleshooting

### Dialogue Not Appearing

Check:
- [ ] Enemy JSON has "dialogue" field (not "dialogues")
- [ ] Dialogue text is not empty
- [ ] Game started correctly
- [ ] No runtime errors in console

### Text Not Visible

Check:
- [ ] Font image exists: `src/assets/text/8x8text_darkGrayShadow.png`
- [ ] Characters are in font's character set
- [ ] Dialogue box has positive width/height

### Input Not Working

Check:
- [ ] Game in DIALOGUE state (check state_manager output)
- [ ] K key is pressed (not other keys)
- [ ] 0.5 second cooldown between presses

### Text Wraps Incorrectly

Check:
- [ ] Dialogue box width is set correctly
- [ ] Font character width is 8 pixels
- [ ] Words aren't too long for box width

## Advanced: Adding Non-Quest NPCs

NPCs without dialogue (won't trigger dialogue state):

```json
{
  "enemies": [
    {
      "type": "orc",
      "position": {"x": 300, "y": 300}
    }
  ]
}
```

Without a "dialogue" field, collision goes directly to battle.

## API Quick Reference

### Show Dialogue

```python
# Automatically done when collision detected, but for reference:
state_manager.start_battle("enemy_1")  # Triggers BATTLE_BEGIN
# Then BATTLE_BEGIN handler does:
HUDFactory.create_dialogue_box(entity_manager, "enemy_1")
DialoguePreparation(font).run(entity_manager, "enemy_1")
state_manager.start_conversation("enemy_1")  # Goes to DIALOGUE
```

### Modify Text Speed

```python
entity["dialogue"].chars_per_second = 30
```

### Skip Typewriter Animation

```python
entity["dialogue"].visible_chars = entity["dialogue"].pages_length(entity["dialogue"])
entity["dialogue"].finished_page = True
```

### Jump to Next Page

```python
if entity["dialogue"].current_page < len(entity["dialogue"].pages) - 1:
    entity["dialogue"].current_page += 1
    entity["dialogue"].visible_chars = 0
    entity["dialogue"].finished_page = False
    entity["dialogue"].timer = 0
```

## File Organization

### Dialogue System Files
```
src/
├── ecs/
│   ├── components/
│   │   └── dialogue.py              (DialogueComponent, DialogueBoxComponent)
│   └── systems/
│       ├── text_system.py           (DialoguePreparation, DialogueSystem)
│       ├── render_system.py         (Renders dialogue text)
│       └── event_handler_system.py (DialogEventHandlerSystem)
├── world/
│   └── hud_factory.py              (HUDFactory.create_dialogue_box())
├── helpers/
│   ├── bitmap_font_loader.py       (BitmapFont class)
│   └── system_manager.py           (Manages all systems)
└── run.py                          (Game loop with dialogue state)

docs/
├── DIALOGUE_SYSTEM.md              (Architecture & concepts)
├── TEXT_RENDERING.md               (Bitmap font & rendering)
├── DIALOGUE_API.md                 (API reference)
└── IMPLEMENTATION_SUMMARY.md       (What was implemented)
```

## Common Patterns

### Dialogue Before Battle

```json
{
  "enemies": [{
    "type": "boss",
    "position": {"x": 400, "y": 400},
    "dialogue": "You have challenged the wrong enemy! Prepare yourself!"
  }]
}
```

### Taunt During Dialogue

```json
"dialogue": "Ha! Is that all you've got? Bring it on!"
```

### Story Building

```json
"dialogue": "I have been waiting for you. Long ago, I was cursed... and now you must face the consequences!"
```

## Performance Notes

- Dialogue system is optimized for smooth 60 FPS
- Text wrapping done once, not every frame
- Character lookup is O(1) hash table
- Only visible characters are rendered
- Dialogue boxes off-screen are culled

## Next Steps

1. **Play the game** and test dialogue with different enemies
2. **Customize text speed** to match your game's feel
3. **Add story dialogue** to all enemies
4. **Expand to NPCs** for quest systems
5. **Add sound effects** (create custom event system)
6. **Implement dialogue trees** (extend DialogueComponent)

## Support Files

For more information, see:
- `docs/DIALOGUE_SYSTEM.md` - Complete system architecture
- `docs/TEXT_RENDERING.md` - How text rendering works
- `docs/DIALOGUE_API.md` - Full API reference
- `docs/IMPLEMENTATION_SUMMARY.md` - Implementation details

Enjoy your new dialogue system!
