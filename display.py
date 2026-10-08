import os
import math
import random
import time
import textwrap

TYPE_SPEED = 0.00000015
MESSAGE_SPEED = 0.0000002

# LCD appearance
BACKGROUND_COLOR = (24, 10, 2)
AMBER = (255, 176, 0)
DIM_AMBER = (155, 98, 15)

SIDE_MARGIN = 70
TOP_MARGIN = 80
LINE_SPACING = 14

# Pygame/LCD state
pygame = None
screen = None
font = None
small_font = None
lcd_available = False
lcd_initialization_attempted = False
scanline_overlay = None
vignette_overlay = None

# Persistent screen state used by update() for cursor blinking and CRT motion.
current_text = ""
current_font = None
current_color = AMBER
current_x = SIDE_MARGIN
current_y = TOP_MARGIN
cursor_enabled = False
cursor_blinking = True
last_render_time = 0.0
next_glitch_time = 0.0
glitch_until = 0.0
glitch_offset = (0, 0)

CURSOR_BLINK_SECONDS = 0.52
MAX_REFRESH_RATE = 30
GLOW_OFFSETS = ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1))


def build_crt_overlays(width, height):
    """Pre-render scanlines and a soft vignette once for Pi-friendly effects."""
    global scanline_overlay
    global vignette_overlay

    scanline_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    for scan_y in range(0, height, 3):
        pygame.draw.line(scanline_overlay, (0, 0, 0, 34), (0, scan_y), (width, scan_y))

    # Calculate the vignette at low resolution, then scale it smoothly.
    small_width = 64
    small_height = max(1, round(small_width * height / width))
    small_vignette = pygame.Surface((small_width, small_height), pygame.SRCALPHA)
    center_x = (small_width - 1) / 2
    center_y = (small_height - 1) / 2

    for pixel_y in range(small_height):
        for pixel_x in range(small_width):
            normalized_x = (pixel_x - center_x) / max(1, center_x)
            normalized_y = (pixel_y - center_y) / max(1, center_y)
            distance = min(1.0, math.sqrt(normalized_x ** 2 + normalized_y ** 2))
            # Keep the center nearly untouched and let only the outer edge
            # fall off. This reads as glass curvature, not a dark spotlight.
            alpha = int(46 * max(0.0, (distance - 0.62) / 0.38) ** 2.2)
            small_vignette.set_at((pixel_x, pixel_y), (0, 0, 0, alpha))

    vignette_overlay = pygame.transform.smoothscale(small_vignette, (width, height))


def initialize_lcd():
    """
    Initialize Pygame once.

    When launched over SSH, these defaults connect Pygame to Anna's existing
    Wayland desktop session. Existing environment values are preserved.
    """
    global pygame
    global screen
    global font
    global small_font
    global lcd_available
    global lcd_initialization_attempted
    global current_font
    global next_glitch_time

    if lcd_initialization_attempted:
        return lcd_available

    lcd_initialization_attempted = True

    try:
        # These must be set before importing Pygame.
        os.environ.setdefault("XDG_RUNTIME_DIR", "/run/user/1000")
        os.environ.setdefault("WAYLAND_DISPLAY", "wayland-0")
        os.environ.setdefault("SDL_VIDEODRIVER", "wayland")

        import pygame as pygame_module

        pygame = pygame_module
        pygame.init()

        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Telephone Network")
        pygame.mouse.set_visible(False)

        width, height = screen.get_size()

        # Scale reasonably for the current 1024 × 768 framebuffer while still
        # adapting if the display resolution changes later.
        main_font_size = max(34, min(54, height // 14))
        small_font_size = max(26, min(40, height // 19))

        font = pygame.font.SysFont("DejaVu Sans Mono", main_font_size)
        small_font = pygame.font.SysFont("DejaVu Sans Mono", small_font_size)

        current_font = font
        build_crt_overlays(width, height)
        next_glitch_time = time.monotonic() + random.uniform(20.0, 40.0)

        lcd_available = True

        print(
            f"[DISPLAY] LCD initialized at {width}x{height}",
            flush=True,
        )

    except Exception as error:
        lcd_available = False
        print(
            f"[DISPLAY] LCD unavailable; using terminal only: {error}",
            flush=True,
        )

    return lcd_available


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def clear_lcd():
    if not initialize_lcd():
        return

    set_screen_text("", show_cursor=False)


def clear():
    """Clear both the SSH terminal and the LCD."""
    clear_terminal()
    clear_lcd()


def update():
    """
    Refresh the LCD and process window events.

    Kept for compatibility with any existing calls from main.py.
    """
    if not initialize_lcd():
        return

    global last_render_time

    now = time.monotonic()
    if now - last_render_time < 1 / MAX_REFRESH_RATE:
        pygame.event.pump()
        return

    render_current_screen(now)


def wrap_text(text, selected_font, max_width):
    """
    Wrap text using the actual rendered pixel width instead of assuming a
    fixed number of characters per line.
    """
    wrapped_lines = []

    for paragraph in text.split("\n"):
        if paragraph == "":
            wrapped_lines.append("")
            continue

        words = paragraph.split()
        current_line = ""

        for word in words:
            proposed_line = (
                f"{current_line} {word}" if current_line else word
            )

            if selected_font.size(proposed_line)[0] <= max_width:
                current_line = proposed_line
            else:
                if current_line:
                    wrapped_lines.append(current_line)

                # Protect against one unusually long unbroken word.
                if selected_font.size(word)[0] > max_width:
                    average_character_width = max(
                        1,
                        selected_font.size("M")[0],
                    )
                    character_limit = max_width // average_character_width
                    pieces = textwrap.wrap(
                        word,
                        width=max(1, character_limit),
                    )
                    wrapped_lines.extend(pieces[:-1])
                    current_line = pieces[-1]
                else:
                    current_line = word

        if current_line:
            wrapped_lines.append(current_line)

    return wrapped_lines


def render_glowing_text(surface, text, selected_font, color, position):
    """Render a restrained phosphor halo followed by a crisp text core."""
    if not text:
        return

    x, y = position
    glow_color = (color[0], max(0, color[1] - 55), 0)
    glow = selected_font.render(text, True, glow_color)
    glow.set_alpha(72)

    for offset_x, offset_y in GLOW_OFFSETS:
        surface.blit(glow, (x + offset_x, y + offset_y))

    soft_glow = pygame.transform.smoothscale(
        glow,
        (glow.get_width() + 8, glow.get_height() + 6),
    )
    soft_glow.set_alpha(34)
    surface.blit(soft_glow, (x - 4, y - 3))

    wide_glow = pygame.transform.smoothscale(
        glow,
        (glow.get_width() + 18, glow.get_height() + 12),
    )
    wide_glow.set_alpha(14)
    surface.blit(wide_glow, (x - 9, y - 6))

    core = selected_font.render(text, True, color)
    surface.blit(core, (x, y))


def render_current_screen(now=None):
    """Compose text, glow, cursor, scanlines, vignette, and subtle CRT motion."""
    global last_render_time
    global next_glitch_time
    global glitch_until
    global glitch_offset

    if not initialize_lcd():
        return

    if now is None:
        now = time.monotonic()

    # Preserve a tiny, rare sync disturbance without making the interface
    # look like a deliberate glitch animation.
    if now >= next_glitch_time and now >= glitch_until:
        glitch_until = now + random.uniform(0.025, 0.045)
        glitch_offset = (random.choice((-2, -1, 1, 2)), 0)
        next_glitch_time = now + random.uniform(20.0, 40.0)

    if now < glitch_until:
        horizontal_offset, vertical_offset = glitch_offset
    else:
        horizontal_offset = 0
        vertical_offset = 0
    content = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    selected_font = current_font or font
    max_width = screen.get_width() - current_x - SIDE_MARGIN
    lines = wrap_text(current_text, selected_font, max_width)
    line_height = selected_font.get_linesize() + LINE_SPACING
    line_y = current_y

    if not lines:
        lines = [""]

    for line in lines:
        render_glowing_text(
            content,
            line,
            selected_font,
            current_color,
            (current_x, line_y),
        )
        line_y += line_height

    cursor_is_visible = (
        cursor_enabled
        and (
            not cursor_blinking
            or int(now / CURSOR_BLINK_SECONDS) % 2 == 0
        )
    )

    if cursor_is_visible:
        final_line = lines[-1]
        cursor_x = current_x + selected_font.size(final_line)[0]
        cursor_y = current_y + (len(lines) - 1) * line_height
        render_glowing_text(
            content,
            "█",
            selected_font,
            current_color,
            (cursor_x, cursor_y),
        )

    screen.fill(BACKGROUND_COLOR)

    # A 1–2% irregular brightness drift keeps the phosphor alive while being
    # too small to read as an obvious opacity animation.
    flutter = (
        0.65 * math.sin(now * 5.7)
        + 0.35 * math.sin(now * 11.3 + 1.4)
    )
    content.set_alpha(max(250, min(255, round(253 + flutter * 2))))
    screen.blit(content, (horizontal_offset, vertical_offset))

    screen.blit(scanline_overlay, (0, 0))
    screen.blit(vignette_overlay, (0, 0))

    pygame.event.pump()
    pygame.display.flip()
    last_render_time = now


def set_screen_text(
    text,
    selected_font=None,
    color=AMBER,
    x=SIDE_MARGIN,
    y=TOP_MARGIN,
    show_cursor=False,
    blink_cursor=True,
):
    """Store the current LCD state and render it immediately."""
    global current_text
    global current_font
    global current_color
    global current_x
    global current_y
    global cursor_enabled
    global cursor_blinking

    if not initialize_lcd():
        return

    current_text = text
    current_font = selected_font or font
    current_color = color
    current_x = x
    current_y = y
    cursor_enabled = show_cursor
    cursor_blinking = blink_cursor
    render_current_screen()


def draw_text(
    text,
    selected_font=None,
    color=AMBER,
    x=SIDE_MARGIN,
    y=TOP_MARGIN,
    show_cursor=False,
    blink_cursor=True,
):
    """Compatibility wrapper used by the existing display functions."""
    set_screen_text(
        text,
        selected_font,
        color,
        x,
        y,
        show_cursor,
        blink_cursor,
    )


def terminal_print(text, speed=TYPE_SPEED):
    """
    Type text progressively in SSH and on the LCD at the same time.

    While typing, a steady block marks the position of the next character.
    Once typing finishes, the block changes to its normal blinking state.
    """
    clear_terminal()

    visible_text = ""
    draw_text(visible_text, show_cursor=True, blink_cursor=False)

    for character in text:
        visible_text += character

        print(character, end="", flush=True)
        draw_text(visible_text, show_cursor=True, blink_cursor=False)

        time.sleep(speed)

    print(flush=True)
    draw_text(visible_text, show_cursor=True)


def show(state):
    match state.name:
        case "IDLE":
            show_idle()

        case "WAITING_FOR_DIAL":
            show_waiting()

        case "RECORDING":
            show_recording()

        case "PROCESSING":
            show_processing()

        case "DISPLAYING_MESSAGE":
            pass


def show_idle():
    terminal_print(
        "Leave a message\n\n"
        "Hear another"
    )


def show_waiting():
    terminal_print(
        "Turn dial\n"
        "to begin recording.\n\n"
        "Turn again\n"
        "to finish."
    )


def show_recording():
    clear_terminal()
    print("Recording", flush=True)

    draw_text("Recording", show_cursor=False)


def show_processing():
    terminal_print("Message received.")


def show_recording_progress(remaining):
    progress_text = (
        "Recording\n\n"
        f"{'█' * remaining}"
    )

    clear_terminal()
    print(progress_text, flush=True)

    draw_text(progress_text, show_cursor=False)


def searching(duration=2):
    frames = [
        "Searching archive",
        "Searching archive.",
        "Searching archive..",
        "Searching archive...",
    ]

    start = time.time()
    index = 0

    while time.time() - start < duration:
        display_text = (
            "Message received.\n\n"
            f"{frames[index]}"
        )

        clear_terminal()
        print(display_text, flush=True)

        draw_text(display_text, show_cursor=False)

        index = (index + 1) % len(frames)
        time.sleep(0.35)


def show_location(message):
    location = message.get("location", {})

    city = location.get("city", "Unknown")
    country = location.get("country", "")
    timestamp = message.get("timestamp", "")

    try:
        date = time.strftime(
            "%B %d, %Y",
            time.strptime(timestamp[:10], "%Y-%m-%d"),
        )

        # Remove a leading zero from dates such as "July 05".
        date = date.replace(" 0", " ")

    except (ValueError, TypeError):
        date = "Unknown date"

    if country:
        location_text = f"{city}, {country}"
    else:
        location_text = city

    terminal_print(f"{location_text}\n\n{date}")


def type_message(text):
    terminal_print(text, speed=MESSAGE_SPEED)


def shutdown():
    """Cleanly close Pygame when the main program exits."""
    global lcd_available

    if pygame is not None:
        pygame.quit()

    lcd_available = False