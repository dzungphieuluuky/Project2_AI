import pygame
import sys

from agent import Agent
from world import WumpusWorld
from button import *
from config import *

# DO NOT TOUCH! 
pygame.init()

GRID_SIZE = 80
GRID_ORIGIN = (300, 90)
ASSETS_PATH = "./assets"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wumpus World Agent")
icon_image = pygame.image.load('./assets/bot.png').convert_alpha()
pygame.display.set_icon(icon_image)
clock = pygame.time.Clock()

# Hình ảnh
original_assets = {
        'agent_up': pygame.image.load("./assets/agent_up.png").convert_alpha(),
        'agent_right': pygame.image.load("./assets/agent_right.png").convert_alpha(),
        'agent_down': pygame.image.load("./assets/agent_down.png").convert_alpha(),
        'agent_left': pygame.image.load("./assets/agent_left.png").convert_alpha(),
        'breeze': pygame.image.load("./assets/breeze.png").convert_alpha(),
        'gold': pygame.image.load("./assets/gold.png").convert_alpha(),
        'pit': pygame.image.load("./assets/pit.png").convert_alpha(),
        'stench': pygame.image.load("./assets/stench.png").convert_alpha(),
        'wumpus': pygame.image.load("./assets/wumpus.png").convert_alpha(),
        'bump': pygame.image.load("./assets/bump.png").convert_alpha(),
        'glitter': pygame.image.load("./assets/glitter.png").convert_alpha(),
        'scream': pygame.image.load("./assets/scream.png").convert_alpha(),
    }
PERCEPTS_ICON_SIZE = (32, 32)

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
    welcome_text = [
        "Welcome to the Wumpus World AI Visualizer!",
        "An intelligent agent is trapped in a perilous cave, filled with deadly pits",
        "and a fearsome monster called Wumpus. Using only its senses (smell,",
        "breeze, glitter), the agent must deduce the location of the gold, grab it,",
        "and return to the starting point to climb out of the cave.",
        "Use the setup screen to configure the challenge, then watch as the agent",
        "uses propositional logic to navigate the dangers and achieve its goal!"
    ]

    notation_icon_size = (40, 40)
    notations = []
    
    # Define which assets to show and their descriptions
    symbols_to_explain = {
        'agent_up': "The Agent",
        'wumpus': "The deadly Wumpus",
        'pit': "A bottomless Pit",
        'gold': "The precious Gold",
        'stench': "Stench (Wumpus is nearby)",
        'breeze': "Breeze (A Pit is nearby)",
        'glitter': "Glitter (Gold is in this cell)",
        'scream': "Scream (A Wumpus was hit)",
    }

    for key, description in symbols_to_explain.items():
        if key in original_assets:
            icon = pygame.transform.scale(original_assets[key], notation_icon_size)
            notations.append((icon, description))


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

        for i, line in enumerate(welcome_text):
            text_surf = intro_font.render(line, True, BLACK)
            screen.blit(text_surf, (50, 120 + 35 * i))

        # Render "Game Notations" title
        notation_title_surf = FONT_MEDIUM.render("Game Symbols", True, BLACK)
        screen.blit(notation_title_surf, (40, 360))
        
        # Render the list of icons and their descriptions on the right
        notation_start_y = 420
        for i, (icon_surf, description) in enumerate(notations):
            y_pos = notation_start_y + (i % 4) * (notation_icon_size[1] + 15)
            
            # Draw the icon
            icon_rect = icon_surf.get_rect(centery=y_pos, left=40 + 400 * (i > 3))
            screen.blit(icon_surf, icon_rect)
            
            # Draw the description text next to it
            desc_surf = FONT_MEDIUM.render(f"- {description}", True, BLACK)
            desc_rect = desc_surf.get_rect(centery=y_pos, left=icon_rect.right + 20)
            screen.blit(desc_surf, desc_rect)

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

        for button in buttons:
            button.draw_button(screen)

        pygame.display.flip()
        clock.tick(FPS)

def start_game() -> None:
    app_state = 'setup'  # 'setup' or 'game'
    agent = None
    world = None
    
    GRID_SIZE = 0
    GRID_ORIGIN = (0, 0)
    scaled_assets = {}

    settings = {
        'world_size': 8, 
        'num_wumpus': 1, 
        'pit_prob': 0.2,
        'random_agent': False, 
        'moving_wumpus': False
    }

    pause = True
    game_over = False
    last_step_time = 0
    
    game_buttons = {}
    setup_buttons = {}
    input_boxes = {}
    cell_icon_map = {}

    def create_scaled_assets(icon_size_px, agent_icon_px):
        "Scale image according to size map"
        scaled = {}
        icon_tuple = (icon_size_px, icon_size_px)
        agent_icon_tuple = (agent_icon_px, agent_icon_px)
        for name, surf in original_assets.items():
            if "agent" in name:
                scaled[name] = pygame.transform.scale(surf, agent_icon_tuple)
            else:
                scaled[name] = pygame.transform.scale(surf, icon_tuple)
        return scaled

    def update_visual_knowledge():
        nonlocal cell_icon_map
        cell_icon_map.clear()
        if not agent or not world: return

        known_pits = set()
        known_wumpus = set()
        for clause in agent.kb.clauses:
            if len(clause) == 1:
                literal = next(iter(clause))
                if not literal.startswith('~'):
                    try:
                        entity_type = literal[0]
                        coords = tuple(map(int, literal[1:].split('-')))
                        if entity_type == 'P': known_pits.add(coords)
                        elif entity_type == 'W': known_wumpus.add(coords)
                    except (ValueError, IndexError): continue

        for x in range(world.size):
            for y in range(world.size):
                loc = (x, y)
                icons = []
                if loc in agent.total_percepts:
                    percepts = agent.total_percepts[loc]
                    if percepts.get('breeze'): 
                        icons.append(scaled_assets['breeze'])
                    if percepts.get('stench'): 
                        icons.append(scaled_assets['stench'])
                
                if loc in known_pits: 
                    icons.append(scaled_assets['pit'])
                if loc in known_wumpus: 
                    icons.append(scaled_assets['wumpus'])
                if (x, y) == agent.location and world.listCells[x][y].getGold(): 
                    icons.append(scaled_assets['gold'])

                cell_icon_map[loc] = icons
    
    def draw_cell(cell, is_visible, agent):
        x, y = cell.location
        inverted_y = (world.size - 1) - y
        cell_rect = pygame.Rect(GRID_ORIGIN[0] + x * GRID_SIZE, GRID_ORIGIN[1] + inverted_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)

        if not is_visible:
            pygame.draw.rect(screen, DARK_GRAY, cell_rect)
        else:
            bg_color = LIGHT_GRAY if cell.isVisited() else WHITE
            if cell.isDangerous(): bg_color = RED
            elif cell.isSafe(): bg_color = GREEN
            pygame.draw.rect(screen, bg_color, cell_rect)

        icons_to_draw = cell_icon_map.get((x, y), [])
        
        corner_positions = {0: 'topleft', 1: 'topright', 2: 'bottomleft', 3: 'bottomright'}
        for i, icon_surface in enumerate(icons_to_draw):
            if i >= 4: break
            icon_rect = icon_surface.get_rect(**{corner_positions[i]: getattr(cell_rect, corner_positions[i])})
            screen.blit(icon_surface, icon_rect)

        if agent and agent.location == (x, y):
            direction = agent.direction.lower()
            agent_icon = scaled_assets.get(f'agent_{direction}', scaled_assets['agent_up'])
            agent_rect = agent_icon.get_rect(center=cell_rect.center)
            screen.blit(agent_icon, agent_rect)

        pygame.draw.rect(screen, BLACK, cell_rect, 1)
    
    def run_one_game_turn():
        nonlocal game_over, pause
        agent.get_percepts_from(world)
        world.reset_scream_bump()
        agent.tell()
        world.update_agent_known_cells()
        agent.infer_surrounding_cells()
        action_code = agent.select_action()
        world.update_world(action=action_code)
        agent.update_visited_location()
        
        update_visual_knowledge()

        game_buttons['score_panel'].set_text(f'Score: {agent.score}')
        game_buttons['action_panel'].set_text(f'Action: {agent.name_actions.get(action_code, "Unknown")}')
        
        percept_icons = [percepts_scaled_assets[p] for p, active in agent.percepts.items() if active]
        game_buttons['percepts_panel'].set_icons(percept_icons)

        if not agent.alive or agent.out:
            game_over, pause = True, True
            game_buttons['pause_play'].set_text('Game Over')



    percepts_scaled_assets = {}
    for name in ['stench', 'breeze', 'glitter', 'bump', 'scream']:
        percepts_scaled_assets[name] = pygame.transform.scale(original_assets[name], PERCEPTS_ICON_SIZE)
    
    def start_main_loop():
        nonlocal agent, world, app_state, pause, game_over, last_step_time
        nonlocal GRID_SIZE, GRID_ORIGIN, scaled_assets

        try:
            settings['world_size'] = int(input_boxes['size'].text)
            settings['num_wumpus'] = int(input_boxes['wumpus'].text)
            settings['pit_prob'] = float(input_boxes['pit_prob'].text)
        except (ValueError, TypeError):
            settings['world_size'], settings['num_wumpus'], settings['pit_prob'] = 8, 1, 0.2
        
        grid_area_width = WIDTH - 400
        grid_area_height = HEIGHT - 80
        GRID_SIZE = min(grid_area_width // settings['world_size'], grid_area_height // settings['world_size'])
        ICON_SIZE = GRID_SIZE // 3
        AGENT_ICON_SIZE = GRID_SIZE // 2

        total_grid_width = GRID_SIZE * settings['world_size']
        total_grid_height = GRID_SIZE * settings['world_size']
        GRID_ORIGIN = (
            400 + (grid_area_width - total_grid_width) // 2,
            40 + (grid_area_height - total_grid_height) // 2
        )

        scaled_assets = create_scaled_assets(ICON_SIZE, AGENT_ICON_SIZE)

        agent = Agent(random=settings['random_agent'])
        world = WumpusWorld(
            agent=agent, size=settings['world_size'], 
            num_wumpus=settings['num_wumpus'], pit_prob=settings['pit_prob'],
            moving_wumpus=settings['moving_wumpus']
        )
        
        pause, game_over, last_step_time = True, False, 0
        game_buttons['pause_play'].set_text('Play (P)')
        game_buttons['score_panel'].set_text(f'Score: {agent.score}')
        game_buttons['action_panel'].set_text('Action: None')
        game_buttons['percepts_panel'].set_icons([])
        
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
                                 WIDTH//2 - 150, 380, 300, 50, ATOMIC_TANGERINE, None)
    random_agent_button.callback = lambda: toggle_setting('random_agent', random_agent_button, "Random Agent: {}")
    setup_buttons['random_agent'] = random_agent_button

    moving_wumpus_button = Button(f"Moving Wumpus: {'Yes' if settings['moving_wumpus'] else 'No'}",
                                  WIDTH//2 - 150, 440, 300, 50, AMARANTH_PURPLE, None)
    moving_wumpus_button.callback = lambda: toggle_setting('moving_wumpus', moving_wumpus_button, "Moving Wumpus: {}")
    setup_buttons['moving_wumpus'] = moving_wumpus_button
    
    back_button_title = button_font.render("Back to Menu", True, BLACK)
    back_button_width = back_button_title.get_width() + 35
    back_button_height = back_button_title.get_height() + 35

    setup_buttons['start'] = Button('Start Game', WIDTH//2 - 100, 520, 200, 60, GREEN, start_main_loop)
    setup_buttons['back_to_menu'] = Button("Back to Menu", WIDTH - 20 - back_button_width, 20, 
                                back_button_width, back_button_height, ATOMIC_TANGERINE, menu_loop)
    game_buttons['pause_play'] = Button('Play (P)', 20, 20, 180, 50, GREEN, change_play_pause)
    game_buttons['reset'] = Button('New Game', 20, 80, 180, 50, BLUE, reset_to_setup)

    game_buttons['back_to_menu'] = Button("Back to Menu", 20, 140, 
                                          back_button_width, back_button_height, ATOMIC_TANGERINE, menu_loop)

    
    game_buttons['score_panel'] = Button('Score: 0', 20, 240, 264, 60, ZOMP, None, expandable=False)
    game_buttons['action_panel'] = Button('Action: None', 20, 320, 264, 60, FRENCH_BLUE, None, expandable=False)
    percept_label_surf = button_font.render("Percepts:", True, WHITE)
    game_buttons['percepts_label'] = Button('Percepts:', 20, 400, percept_label_surf.get_width() + 150, 60, ATOMIC_TANGERINE, None, expandable=False)
    game_buttons['percepts_panel'] = Button('', 20, 480, 264, 60, CREAM, None, expandable=False)

    game_buttons['die_panel'] = Button('Agent is dead!', 20, 480, 264, 60, AMARANTH_PURPLE, None, expandable=False)
    game_buttons['climb_panel'] = Button('Agent has climbed out!', 20, 560, 264, 60, GREEN, None, expandable=False)

    # main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            
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

            for btn in setup_buttons.values(): 
                btn.draw_button(screen)
            for box in input_boxes.values(): 
                box.draw_box(screen)

        elif app_state == 'game':
            if not pause and not game_over and pygame.time.get_ticks() - last_step_time >= DELAY_TIME:
                run_one_game_turn()
                last_step_time = pygame.time.get_ticks()

            known_locs = {cell.location for cell in agent.known_cells} if agent else set()
            if world:
                for x in range(world.size):
                    for y in range(world.size):
                        draw_cell(world.listCells[x][y], (x, y) in known_locs, agent)

            for name, button in game_buttons.items():
                if name not in ['die_panel', 'climb_panel']:
                    button.draw_button(screen)
            
            if game_over:
                if not agent.alive:
                    game_buttons['die_panel'].draw_button(screen)
                elif agent.out:
                    game_buttons['climb_panel'].draw_button(screen)
        
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


