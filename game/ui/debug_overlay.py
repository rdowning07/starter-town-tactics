# Removed unused import


def draw_debug_info(screen, font, info, x=10, y=10, line_height=20):
    for i, line in enumerate(info):
        text_surface = font.render(line, True, (255, 255, 0))
        screen.blit(text_surface, (x, y + i * line_height))
