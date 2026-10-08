import pygame
import time

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()

BLACK = (0, 0, 0)
AMBER = (255, 176, 50)

screen.fill(BLACK)

font = pygame.font.SysFont("monospace", 42)
small_font = pygame.font.SysFont("monospace", 28)

title = font.render("TELEPHONE NETWORK", True, AMBER)
hello = small_font.render("Hello.", True, AMBER)

screen.blit(title, (70, 100))
screen.blit(hello, (70, 180))

pygame.display.flip()

print(f"LCD test running at {width}x{height}")
print("Press Ctrl+C to exit.")

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    pygame.quit()