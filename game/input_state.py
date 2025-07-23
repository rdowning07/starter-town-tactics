import pygame


class InputState:
    def __init__(self, game):
        self.game = game
        self.cursor_x = 0
        self.cursor_y = 0
        self.state = "idle"
        self.selected_unit = None
        self.log = []
        self.blink_timer = 0
        self.blink_interval = 30
        self.cursor_visible = True

    def move_cursor(self, dx, dy):
        new_x = self.cursor_x + dx
        new_y = self.cursor_y + dy
        if 0 <= new_x < self.game.width and 0 <= new_y < self.game.height:
            self.cursor_x = new_x
            self.cursor_y = new_y
            self.log.append(f"Moved to ({new_x}, {new_y})")

    def confirm_selection(self):
        if self.state == "unit_selected" and self.selected_unit:
            self.selected_unit.move_to(self.cursor_x, self.cursor_y)
            self.log.append(
                f"{self.selected_unit.name} moved to ({self.cursor_x}, {self.cursor_y})"
            )
            self.reset()
        else:
            for unit in self.game.units:
                if unit.x == self.cursor_x and unit.y == self.cursor_y:
                    self.selected_unit = unit
                    self.state = "unit_selected"
                    self.log.append(f"Selected {unit.name}")
                    break

    def cancel_selection(self):
        if self.state == "unit_selected":
            self.log.append(f"Cancelled selection of {self.selected_unit.name}")
            self.reset()

    def reset(self):
        self.state = "idle"
        self.selected_unit = None

    def handle_keypress(self, key):
        if key == pygame.K_LEFT:
            self.move_cursor(-1, 0)
        elif key == pygame.K_RIGHT:
            self.move_cursor(1, 0)
        elif key == pygame.K_UP:
            self.move_cursor(0, -1)
        elif key == pygame.K_DOWN:
            self.move_cursor(0, 1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.confirm_selection()
        elif key == pygame.K_ESCAPE:
            self.cancel_selection()

    def draw_cursor(self, surface, tile_size, cam_x, cam_y, sprites):
        self.blink_timer += 1
        if self.blink_timer >= self.blink_interval:
            self.cursor_visible = not self.cursor_visible
            self.blink_timer = 0

        if self.cursor_visible:
            draw_x = self.cursor_x - cam_x
            draw_y = self.cursor_y - cam_y
            if (
                0 <= draw_x * tile_size < surface.get_width()
                and 0 <= draw_y * tile_size < surface.get_height()
            ):
                sprite = sprites.get_sprite("ui", "cursor")
                surface.blit(sprite, (draw_x * tile_size, draw_y * tile_size))

    def get_log(self, limit=3):
        return self.log[-limit:]
