from button import *
from sound import *
from font import *


import pygame
import sys

# Color macro
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
DARK_BLUE = (0, 80, 200)
BLACK = (0, 0, 0)

AMARANTH_PURPLE = (170, 17, 85)
ATOMIC_TANGERINE = (247, 157, 101)
FRENCH_BLUE = (0, 114, 187)
CREAM = (239, 242, 192)
ZOMP = (81, 158, 138)

DELAY_TIME = 1000

# DO NOT TOUCH! 
pygame.init()

WIDTH = 800
HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wumpus World Agent")
icon_image = pygame.image.load('./assets/bot.png').convert_alpha()
pygame.display.set_icon(icon_image)
clock = pygame.time.Clock()

def menu_loop() -> None:
    running = True
    screen.fill(WHITE)
    image = pygame.image.load('./assets/background.png').convert_alpha()
    image_rect = image.get_rect()

    button_width = 200
    button_height = 60
    button_x_coordinate = WIDTH // 2 - button_width // 2
    last_button_y_coordinate = HEIGHT - 20 - button_height

    buttons = [Button("Start Game", button_x_coordinate, last_button_y_coordinate - 2 * (button_height + 10), 
                      button_width, button_height, ATOMIC_TANGERINE, start_game),
               Button("Introduction", button_x_coordinate, last_button_y_coordinate - (button_height + 10), 
                      button_width, button_height, ZOMP, introduction_screen),
               Button("Quit Game", button_x_coordinate, last_button_y_coordinate, 
                      button_width, button_height, AMARANTH_PURPLE, quit_game)]
    
    hovered_button = 0
    title = font.render("Wumpus World Agent", True, AMARANTH_PURPLE)

    while running:
        screen.blit(image, image_rect)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        
        for button in buttons:
            button.draw_button(screen)

        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    buttons[hovered_button].is_hovered = False
                    hovered_button = (hovered_button - 1) % len(buttons)
                    buttons[hovered_button].is_hovered = True
                
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    buttons[hovered_button].is_hovered = False
                    hovered_button = (hovered_button + 1) % len(buttons)
                    buttons[hovered_button].is_hovered = True
                
                elif event.key == pygame.K_ESCAPE:
                    running = False

            for button in buttons:
                button.handle_event(event=event)
        
        
        pygame.display.flip()
        clock.tick(FPS)

def start_game():
    # placeholder
    quit_game()

def introduction_screen() -> None:
    introductions = [
        "This is The Wumpus World Game visualizer.",
        "Here are some instructions to help you through the application!",
        "1. Use arrow (up/down/left/right) or WASD keys to navigate the buttons.",
        "2. You can view all the agent's knowledge and actions on the screen.",
        "3. You can change the size of the map by clicking on the button.",
        "4. Click the Start Game below to see what the agent will do!"
    ]
    # list to hold all buttons
    buttons = []

    title = title_font.render("Introduction", True, BLACK)

    back_button_title = button_font.render("Back to Menu", True, BLACK)
    back_button_width = back_button_title.get_width() + 35
    back_button_height = back_button_title.get_height() + 35
    back_button = Button("Back to Menu", WIDTH - 20 - back_button_width, 20, 
                            back_button_width, back_button_height, ATOMIC_TANGERINE, menu_loop)
    buttons.append(back_button)

    start_button_title = button_font.render("Start Game", True, BLACK)
    start_button_width = start_button_title.get_width() + 35
    start_button_height = start_button_title.get_height() + 35
    start_button = Button("Start Game", WIDTH // 2 - start_button_width // 2,HEIGHT - 20 - start_button_height, 
                            start_button_width, start_button_height, AMARANTH_PURPLE, start_game)
    buttons.append(start_button)

    running = True
    while running:
        screen.fill(CREAM)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # rendering intro text
        for i, line in enumerate(introductions):
            text = intro_font.render(line, True, BLACK)
            screen.blit(text, (20, 150 + 40 * i))
        
        for button in buttons:
            button.draw_button(screen)

        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            
            for button in buttons:
                button.handle_event(event=event)
    
        pygame.display.flip()
        clock.tick(FPS)

def quit_game():
    pygame.quit()
    sys.exit()

def main():
    menu_loop()

if __name__ == "__main__":
    main()
