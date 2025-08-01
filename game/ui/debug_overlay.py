# Removed unused import


def draw_debug_info(screen, font, info, config=None):
    """Draw debug information on screen."""
    if config is None:
        config = {}

    x = config.get("x", 10)
    y = config.get("y", 10)
    line_height = config.get("line_height", 20)

    for i, line in enumerate(info):
        text_surface = font.render(line, True, (255, 255, 0))
        screen.blit(text_surface, (x, y + i * line_height))
