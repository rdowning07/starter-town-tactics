# 🎮 Week 1 UI Integration Plan - Starter Town Tactics

## **📋 Week 1 Deliverables**

### **Core Files to Create:**
- `game/ui/ui_state.py` – Store UI state (selected unit, menu visibility)
- `game/ui/ui_renderer.py` – Draw basic UI overlay (highlight, cursor)
- `game/ui/input_handler.py` – Handle mouse clicks for unit selection
- `cli/play_demo.py` – Integrate UI system into main loop
- `tests/test_ui.py` – Basic tests for unit selection and state updates

---

## **📅 Day-by-Day Execution Plan**

### **Day 1 – Setup UI State**
**✅ Create ui_state.py**
**✅ Define UIState class**
**✅ Implement unit selection tracking**
**✅ Implement action menu toggle**

**File: `game/ui/ui_state.py`**
```python
# @api
# @refactor
from typing import Optional, Tuple

class UIState:
    """Tracks UI state for Starter Town Tactics."""
    def __init__(self):
        # Currently selected unit
        self.selected_unit_id: Optional[int] = None
        # Mouse hover position (tile x, y)
        self.hover_tile: Optional[Tuple[int, int]] = None
        # Action menu position (pixel coordinates)
        self.action_menu_pos: Optional[Tuple[int, int]] = None
        # Is action menu visible?
        self.action_menu_visible: bool = False

    def select_unit(self, unit_id: int):
        self.selected_unit_id = unit_id
        self.action_menu_visible = True
        print(f"[UIState] Selected unit: {unit_id}")

    def deselect_unit(self):
        print(f"[UIState] Deselected unit: {self.selected_unit_id}")
        self.selected_unit_id = None
        self.action_menu_visible = False

    def update_hover(self, tile_pos: Tuple[int, int]):
        self.hover_tile = tile_pos
```

**Test stub:**
- Ensure selecting a unit sets `selected_unit_id` and toggles menu
- Ensure `deselect_unit` clears everything

---

### **Day 2 – Render Basic UI**
**✅ Create ui_renderer.py**
**✅ Highlight selected unit**
**✅ Show hover cursor**
**✅ Stub action menu box**

**File: `game/ui/ui_renderer.py`**
```python
# @api
# @refactor
import pygame
from game.ui.ui_state import UIState

class UIRenderer:
    """Render UI overlays."""
    def __init__(self, screen: pygame.Surface, tile_size: int = 32):
        self.screen = screen
        self.tile_size = tile_size

    def render_ui(self, ui_state: UIState):
        # Draw hover highlight
        if ui_state.hover_tile:
            x, y = ui_state.hover_tile
            rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
            pygame.draw.rect(self.screen, (200, 200, 0), rect, 3)

        # Draw selected unit highlight
        if ui_state.selected_unit_id is not None:
            # For demo, draw a red box at unit position (stub)
            # TODO: Replace with actual unit position lookup
            rect = pygame.Rect(100, 100, self.tile_size, self.tile_size)
            pygame.draw.rect(self.screen, (255, 0, 0), rect, 3)

        # Draw action menu (stub)
        if ui_state.action_menu_visible and ui_state.action_menu_pos:
            x, y = ui_state.action_menu_pos
            menu_rect = pygame.Rect(x, y, 100, 50)
            pygame.draw.rect(self.screen, (0, 0, 255), menu_rect)
```

**Test stub:**
- Manual: move mouse over tile → see yellow highlight
- Select unit → see red box + blue action menu

---

### **Day 3 – Input Handling**
**✅ Create input_handler.py**
**✅ Map mouse clicks to tiles**
**✅ Call UIState.select_unit if unit exists**
**✅ Update hover tile on mouse movement**

**File: `game/ui/input_handler.py`**
```python
# @api
# @refactor
import pygame
from game.ui.ui_state import UIState

def screen_to_tile(pos: tuple[int, int], tile_size: int) -> tuple[int, int]:
    """Convert pixel coordinates to tile coordinates."""
    x, y = pos
    return (x // tile_size, y // tile_size)

def handle_mouse_input(event: pygame.event.Event, ui_state: UIState, tile_size: int, get_unit_at_tile):
    """Handle mouse click/hover events."""
    if event.type == pygame.MOUSEMOTION:
        ui_state.update_hover(screen_to_tile(event.pos, tile_size))

    elif event.type == pygame.MOUSEBUTTONDOWN:
        tile = screen_to_tile(event.pos, tile_size)
        unit_id = get_unit_at_tile(tile)
        if unit_id is not None:
            ui_state.select_unit(unit_id)
            ui_state.action_menu_pos = event.pos
        else:
            ui_state.deselect_unit()
```

**Stub `get_unit_at_tile` for W1:**
```python
def get_unit_at_tile(tile):
    # For demo, return 1 if top-left tile clicked
    return 1 if tile == (0, 0) else None
```

---

### **Day 4 – Integrate into play_demo.py**
**✅ Initialize UIState and UIRenderer**
**✅ Hook input handler into Pygame loop**
**✅ Call render_ui each frame**

**Snippet: `cli/play_demo.py`**
```python
import pygame
from game.ui.ui_state import UIState
from game.ui.ui_renderer import UIRenderer
from game.ui.input_handler import handle_mouse_input, get_unit_at_tile

pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
tile_size = 32

ui_state = UIState()
ui_renderer = UIRenderer(screen, tile_size)

running = True
while running:
    screen.fill((50, 50, 50))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        handle_mouse_input(event, ui_state, tile_size, get_unit_at_tile)

    ui_renderer.render_ui(ui_state)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```

**Test:**
- Move mouse → yellow hover box
- Click top-left tile → red selection + blue menu

---

### **Day 5 – Unit Test test_ui.py**
**✅ Validate UIState methods**
**✅ Validate selection/deselection logic**

**File: `tests/test_ui.py`**
```python
import unittest
from game.ui.ui_state import UIState

class TestUIState(unittest.TestCase):
    def setUp(self):
        self.ui = UIState()

    def test_select_unit(self):
        self.ui.select_unit(5)
        self.assertEqual(self.ui.selected_unit_id, 5)
        self.assertTrue(self.ui.action_menu_visible)

    def test_deselect_unit(self):
        self.ui.select_unit(5)
        self.ui.deselect_unit()
        self.assertIsNone(self.ui.selected_unit_id)
        self.assertFalse(self.ui.action_menu_visible)

    def test_update_hover(self):
        self.ui.update_hover((2,3))
        self.assertEqual(self.ui.hover_tile, (2,3))

if __name__ == "__main__":
    unittest.main()
```

**Run:**
```bash
python -m unittest tests/test_ui.py
```
**✅ All should pass**

---

## **✅ Week 1 Deliverables Recap**

| **File** | **Purpose** | **Status** |
|----------|-------------|------------|
| `game/ui/ui_state.py` | UI state management | ✅ |
| `game/ui/ui_renderer.py` | Draw hover, selected unit, action menu | ✅ |
| `game/ui/input_handler.py` | Mouse movement & click handling | ✅ |
| `cli/play_demo.py` | Integrated main loop with UI | ✅ |
| `tests/test_ui.py` | Unit tests for UI state | ✅ |

---

## **🎯 Success Criteria for Week 1**

### **Functional Requirements:**
- [ ] Mouse hover shows yellow highlight on tiles
- [ ] Clicking top-left tile selects unit (red box)
- [ ] Selected unit shows blue action menu
- [ ] Clicking elsewhere deselects unit
- [ ] All unit tests pass

### **Technical Requirements:**
- [ ] Clean separation of UI state, rendering, and input
- [ ] Type hints on all functions
- [ ] Proper error handling for edge cases
- [ ] Unit test coverage for UI state logic
- [ ] Integration works with existing game loop

### **Testing Commands:**
```bash
# Run unit tests
python -m unittest tests/test_ui.py

# Test UI integration
python cli/play_demo.py

# Validate no syntax errors
python -m py_compile game/ui/ui_state.py
python -m py_compile game/ui/ui_renderer.py
python -m py_compile game/ui/input_handler.py
```

---

## **🚀 Ready to Start**

This focused Week 1 plan provides:
- **Clear daily deliverables**
- **Specific file structures**
- **Testable outcomes**
- **Integration points**

Start with Day 1: creating `game/ui/ui_state.py` and build incrementally! 🎮
