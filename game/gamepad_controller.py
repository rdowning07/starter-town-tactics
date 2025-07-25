import pygame


class GamepadController:
    def __init__(self, input_state, init_joystick=True):
        self.input_state = input_state
        self.joystick = None
        self.move_cooldown = 200  # ms between moves
        self.last_move_time = 0

        if init_joystick:
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()

    def handle_event(self, event):
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                self.input_state.confirm_selection()
            elif event.button == 1:
                self.input_state.cancel_selection()
        elif event.type == pygame.JOYHATMOTION:
            dx, dy = event.value
            self.input_state.move_cursor(dx, -dy)

    def update(self):
        if not self.joystick:
            return

        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.move_cooldown:
            return

        axis_x = self.joystick.get_axis(0)
        axis_y = self.joystick.get_axis(1)

        dx, dy = 0, 0
        threshold = 0.5

        if axis_x < -threshold:
            dx = -1
        elif axis_x > threshold:
            dx = 1

        if axis_y < -threshold:
            dy = -1
        elif axis_y > threshold:
            dy = 1

        if dx or dy:
            self.input_state.move_cursor(dx, dy)
            self.last_move_time = now
