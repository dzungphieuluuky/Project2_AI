import pygame

pygame.init()
# Màu mè 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
RED = (255, 80, 80)
GREEN = (80, 200, 80)
YELLOW = (255, 220, 50)
BROWN = (139, 69, 19)
PURPLE = (150, 110, 200)
GRAY = (128, 128, 128)
LIGHT_GRAY = (211, 211, 211)
DARK_GRAY = (40, 40, 40)

AMARANTH_PURPLE = (170, 17, 85)
ATOMIC_TANGERINE = (247, 157, 101)
FRENCH_BLUE = (0, 114, 187)
CREAM = (239, 242, 192)
ZOMP = (81, 158, 138)

DELAY_TIME = 1000

WIDTH = 1200
HEIGHT = 720
FPS = 60

# Font chữ
font = pygame.font.SysFont("Roboto", 128, bold=True)
button_font = pygame.font.SysFont("Cascadia Mono", 32)
title_font = pygame.font.SysFont("Consolas", 60, bold=True)
body_font = pygame.font.SysFont("Consolas", 28)
intro_font = pygame.font.SysFont("Consolas", 20)
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_SMALL = pygame.font.Font(None, 24)

hover_sound = pygame.mixer.Sound('./assets/click.mp3')
click_sound = pygame.mixer.Sound('./assets/mouse-click.mp3')