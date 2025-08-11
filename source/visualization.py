import pygame
import sys
from typing import Union
from agent import Agent
from world import WumpusWorld

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

# DO NOT TOUCH! 
pygame.init()

WIDTH = 1200
HEIGHT = 720
FPS = 60

GRID_SIZE = 80
GRID_ORIGIN = (300, 90)
ASSETS_PATH = "./assets"

# Font chữ
font = pygame.font.SysFont("Roboto", 128, bold=True)
button_font = pygame.font.SysFont("Cascadia Mono", 32)
title_font = pygame.font.SysFont("Consolas", 60, bold=True)
body_font = pygame.font.SysFont("Consolas", 28)
intro_font = pygame.font.SysFont("Consolas", 20)
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_SMALL = pygame.font.Font(None, 24)

# Âm thanh
hover_sound = pygame.mixer.Sound('./assets/click.mp3')
click_sound = pygame.mixer.Sound('./assets/mouse-click.mp3')

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wumpus World Agent")
icon_image = pygame.image.load('./assets/bot.png').convert_alpha()
pygame.display.set_icon(icon_image)
clock = pygame.time.Clock()

# Hình ảnh
ICON_SIZE = (GRID_SIZE // 2, GRID_SIZE // 2) 
agent_up_surf = pygame.image.load("./assets/agent_up.png")
agent_right_surf = pygame.image.load("./assets/agent_right.png")
agent_down_surf = pygame.image.load("./assets/agent_down.png")
agent_left_surf = pygame.image.load("./assets/agent_left.png")
breeze_surf = pygame.image.load("./assets/breeze.png")
gold_surf = pygame.image.load("./assets/gold.png")
pit_surf = pygame.image.load("./assets/pit.png")
stench_surf = pygame.image.load("./assets/stench.png")
wumpus_surf = pygame.image.load("./assets/wumpus.png")

# scale thành icon
agent_up_surf_icon = pygame.transform.scale(agent_up_surf, ICON_SIZE)
agent_right_surf_icon = pygame.transform.scale(agent_right_surf, ICON_SIZE)
agent_down_surf_icon = pygame.transform.scale(agent_down_surf, ICON_SIZE)
agent_left_surf_icon = pygame.transform.scale(agent_left_surf, ICON_SIZE)
breeze_surf_icon = pygame.transform.scale(breeze_surf, ICON_SIZE)
gold_surf_icon = pygame.transform.scale(gold_surf, ICON_SIZE)
pit_surf_icon = pygame.transform.scale(pit_surf, ICON_SIZE)
stench_surf_icon = pygame.transform.scale(stench_surf, ICON_SIZE)
wumpus_surf_icon = pygame.transform.scale(wumpus_surf, ICON_SIZE)

class Button:
    # initialize button class with callback function
    def __init__(self, present : Union[str, pygame.Surface], x: float, y: float, width: float, height: float, color: tuple[int, int, int], callback: callable, expandable = True) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.present = present
        self.color = color
        # callback function to call the function of the button
        self.callback = callback
        self.expandable = expandable
        self.last_hovered = False
        self.is_hovered = False

    def draw_button(self, surface: pygame.surface) -> None:
        present_surf = self.present
        if isinstance(self.present, str):
            present_surf = button_font.render(self.present, True, WHITE)
        if self.is_hovered and self.expandable:
            present_surf = pygame.transform.scale_by(present_surf, 1.1)
            if isinstance(self.present, str):
                pygame.draw.rect(surface, self.color, self.rect.scale_by(1.1, 1.1), border_radius=15)
                if self.last_hovered == False:
                    hover_sound.play()
        else:
            if isinstance(self.present, str):
                pygame.draw.rect(surface, self.color, self.rect, border_radius=15)

        self.last_hovered = self.is_hovered
        present_rect = present_surf.get_rect(center=self.rect.center)
        surface.blit(present_surf, present_rect)

    def handle_event(self, event: pygame.event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif self.is_hovered and (event.type == pygame.MOUSEBUTTONDOWN or
                                  event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_SPACE]):
            if self.expandable:
                click_sound.play()
            self.callback()
    
    def set_text(self, text: str) -> None:
        if isinstance(self.present, str):
            self.present = text

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.text = text
        self.active = False
        self.just_got_clicked = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                self.just_got_clicked = True
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if self.just_got_clicked:
                    self.text = ""
                    self.just_got_clicked = False
                self.text += event.unicode

    def draw_box(self, surface):
        color = LIGHT_GRAY if self.active else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        text_surface = FONT_MEDIUM.render(self.text, True, BLACK)
        surface.blit(text_surface, (self.rect.x + 8, self.rect.y + 8))


def draw_cell(cell, is_visible, agent):
    x, y = cell.location
    cell_rect = pygame.Rect(GRID_ORIGIN[0] + x * GRID_SIZE, GRID_ORIGIN[1] + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)

    # hide unknown cells
    if not is_visible:
        pygame.draw.rect(screen, DARK_GRAY, cell_rect)
        pygame.draw.rect(screen, BLACK, cell_rect, 1)
        return

    bg_color = WHITE
    if cell.isDangerous(): 
        bg_color = RED
    elif cell.isSafe(): 
        bg_color = GREEN
    if cell.isVisited(): 
        bg_color = LIGHT_GRAY
    pygame.draw.rect(screen, bg_color, cell_rect)

    if cell.isVisited():
        if cell.getBreeze():
            screen.blit(breeze_surf_icon, cell_rect.topleft)
        if cell.getStench():
            stench_rect = stench_surf_icon.get_rect(topright=cell_rect.topright)
            screen.blit(stench_surf_icon, stench_rect)

    occupant_surf_icon = None
    if cell.getPit():
        occupant_surf_icon = pit_surf_icon
    elif cell.getWumpus():
        occupant_surf_icon = wumpus_surf_icon
    elif cell.getGold():
        occupant_surf_icon = gold_surf_icon
        
    if occupant_surf_icon:
        occupant_rect = occupant_surf_icon.get_rect(center=cell_rect.center)
        screen.blit(occupant_surf_icon, occupant_rect)
        
    if agent.location == (x, y):
        agent_surf_icon = None
        if agent.direction == "UP": 
            agent_surf_icon = agent_up_surf_icon
        elif agent.direction == "RIGHT": 
            agent_surf_icon = agent_right_surf_icon
        elif agent.direction == "DOWN": 
            agent_surf_icon = agent_down_surf_icon
        elif agent.direction == "LEFT": 
            agent_surf_icon = agent_left_surf_icon
        
        if agent_surf_icon:
            agent_rect = agent_surf_icon.get_rect(center=cell_rect.center)
            screen.blit(agent_surf_icon, agent_rect)
            
    # 6. Draw Grid Border over everything
    pygame.draw.rect(screen, BLACK, cell_rect, 1)

def menu_loop() -> None:
    running = True
    screen.fill(CREAM)
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
                      button_width, button_height, AMARANTH_PURPLE, pygame.quit)]
    
    hovered_button = 0
    title = font.render("Wumpus World Agent", True, AMARANTH_PURPLE)

    while running:
        screen.blit(image, image_rect)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 250))
        
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

def introduction_screen() -> None:
    introductions = [
        "Welcome to our Wumpus World Agent visualizer!",
        "In this application, we will see how our agent",
        "manage to grab the precious gold and get back",
        "in a completely safe-and-sound state!",
        "To see how our agent will explore this dangerous place",
        "just click the button below and the truth shall be revealed!"]
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

def start_game() -> None:
    app_state = 'setup'  # 'setup' or 'game'
    agent = None
    world = None
    
    settings = {
        'world_size': 8, 
        'num_wumpus': 1, 
        'pit_prob': 0.2,
        'random_agent': False, 
        'moving_wumpus': False
    }

    pause = True
    game_over = False
    fog_of_war = True
    last_step_time = 0
    
    game_buttons = {}
    setup_buttons = {}
    input_boxes = {}

    def start_the_game():
        nonlocal agent, world, app_state, pause, game_over, last_step_time
        # Validate and apply settings from input boxes
        try:
            settings['world_size'] = int(input_boxes['size'].text)
            settings['num_wumpus'] = int(input_boxes['wumpus'].text)
            settings['pit_prob'] = float(input_boxes['pit_prob'].text)
        except (ValueError, TypeError):
            print("Invalid input! Using default values.")
            # Revert to defaults if input is bad
            settings['world_size'], settings['num_wumpus'], settings['pit_prob'] = 8, 1, 0.2
        
        agent = Agent(random=settings['random_agent'])
        world = WumpusWorld(
            agent=agent, size=settings['world_size'], 
            num_wumpus=settings['num_wumpus'], pit_prob=settings['pit_prob'],
            moving_wumpus=settings['moving_wumpus']
        )
        
        pause = True
        game_over = False
        last_step_time = 0
        game_buttons['pause_play'].set_text('Play (P)')
        game_buttons['score_panel'].set_text(f'Score: {agent.score}')
        game_buttons['action_panel'].set_text('Action: None')
        game_buttons['percepts_panel'].set_text('Percepts: {}')
        
        app_state = 'game'

    def change_play_pause():
        nonlocal pause
        if not game_over:
            pause = not pause
            game_buttons['pause_play'].set_text('Play (P)' if pause else 'Pause (P)')

    def reset_to_setup():
        nonlocal app_state
        app_state = 'setup'

    def toggle_setting(key, button, text_template):
        settings[key] = not settings[key]
        button.set_text(text_template.format('Yes' if settings[key] else 'No'))
    
    input_boxes['size'] = InputBox(WIDTH//2, 180, 150, 40, str(settings['world_size']))
    input_boxes['wumpus'] = InputBox(WIDTH//2, 240, 150, 40, str(settings['num_wumpus']))
    input_boxes['pit_prob'] = InputBox(WIDTH//2, 300, 150, 40, str(settings['pit_prob']))
    
    random_agent_button = Button(f"Random Agent: {'Yes' if settings['random_agent'] else 'No'}",
                                 WIDTH//2 - 150, 380, 300, 50, GRAY, None)
    random_agent_button.callback = lambda: toggle_setting('random_agent', random_agent_button, "Random Agent: {}")
    setup_buttons['random_agent'] = random_agent_button

    moving_wumpus_button = Button(f"Moving Wumpus: {'Yes' if settings['moving_wumpus'] else 'No'}",
                                  WIDTH//2 - 150, 440, 300, 50, GRAY, None)
    moving_wumpus_button.callback = lambda: toggle_setting('moving_wumpus', moving_wumpus_button, "Moving Wumpus: {}")
    setup_buttons['moving_wumpus'] = moving_wumpus_button

    setup_buttons['start'] = Button('Start Game', WIDTH//2 - 100, 520, 200, 60, GREEN, start_the_game)

    game_buttons['pause_play'] = Button('Play (P)', 20, 20, 180, 50, GREEN, change_play_pause)
    game_buttons['reset'] = Button('New Game', 20, 80, 180, 50, BLUE, reset_to_setup)
    game_buttons['fog'] = Button('Fog: ON', 20, 140, 180, 50, PURPLE, lambda: toggle_fog())
    game_buttons['score_panel'] = Button('Score: 0', 20, 240, 220, 50, GRAY, None, expandable=False)
    game_buttons['action_panel'] = Button('Action: None', 20, 300, 220, 50, GRAY, None, expandable=False)
    game_buttons['percepts_panel'] = Button('Percepts: {}', 20, 360, 220, 50, GRAY, None, expandable=False)
    
    def toggle_fog():
        nonlocal fog_of_war
        fog_of_war = not fog_of_war
        game_buttons['fog'].set_text('Fog: ON' if fog_of_war else 'Fog: OFF')

    # main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
            if app_state == 'setup':
                for btn in setup_buttons.values(): btn.handle_event(event)
                for box in input_boxes.values(): box.handle_event(event)
            elif app_state == 'game':
                for btn in game_buttons.values(): btn.handle_event(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p: change_play_pause()
                    if event.key == pygame.K_r: reset_to_setup()
        
        screen.fill(CREAM)

        if app_state == 'setup':
            title = title_font.render("Wumpus World Setup", True, BLACK)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
            
            labels = {"World Size:": 185, "Num Wumpus:": 245, "Pit Probability:": 305}
            for text, y_pos in labels.items():
                label_surf = FONT_MEDIUM.render(text, True, BLACK)
                screen.blit(label_surf, (WIDTH//2 - 250, y_pos))

            for btn in setup_buttons.values(): btn.draw_button(screen)
            for box in input_boxes.values(): box.draw_box(screen)

        elif app_state == 'game':
            if not pause and not game_over and pygame.time.get_ticks() - last_step_time >= DELAY_TIME:

                agent.get_percepts_from(world)
                world.reset_scream_bump()
                agent.tell()
                world.update_agent_known_cells()
                agent.infer_surrounding_cells()
                action_code = agent.select_action()
                world.update_world(action=action_code)
                agent.update_visited_location()
                
                game_buttons['score_panel'].set_text(f'Score: {agent.score}')
                game_buttons['action_panel'].set_text(f'Action: {agent.name_actions.get(action_code, "Unknown")}')
                game_buttons['percepts_panel'].set_text(f'Percepts: {agent.percepts}')
                
                if not agent.alive or agent.out:
                    game_over = True; pause = True
                    game_buttons['pause_play'].set_text('Game Over')
                
                last_step_time = pygame.time.get_ticks()

            known_locs = {cell.location for cell in agent.known_cells} if agent else set()
            if world:
                for x in range(world.size):
                    for y in range(world.size):
                        draw_cell(world.listCells[x][y], (x,y) in known_locs or not fog_of_war, agent)

            for button in game_buttons.values(): 
                button.draw_button(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

def quit_game():
    pygame.quit()
    sys.exit()

def main():
    menu_loop()

if __name__ == "__main__":
    main()


