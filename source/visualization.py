import pygame
import sys
from agent import Agent
from world import WumpusWorld

# Color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
DARK_BLUE = (0, 80, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

# Theme colors
AMARANTH_PURPLE = (170, 17, 85)
ATOMIC_TANGERINE = (247, 157, 101)
FRENCH_BLUE = (0, 114, 187)
CREAM = (239, 242, 192)
ZOMP = (81, 158, 138)

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH = 1200
HEIGHT = 800
FPS = 60
GRID_SIZE = 60
GRID_ORIGIN = (400, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wumpus World AI Game")
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 32)
font_small = pygame.font.Font(None, 24)

class Button:
    def __init__(self, text, x, y, width, height, color, action=None, text_color=BLACK):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.action = action
        self.text_color = text_color
        self.hovered = False
        
    def draw(self, surface):
        color = self.color if not self.hovered else tuple(min(255, c + 30) for c in self.color)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        text_surf = font_medium.render(str(self.text), True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()

class InputBox:
    def __init__(self, x, y, width, height, default_text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = WHITE
        self.text = default_text
        self.active = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
    
    def draw(self, surface):
        color = LIGHT_GRAY if self.active else WHITE
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        text_surf = font_small.render(self.text, True, BLACK)
        surface.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))

class WumpusWorldGUI:
    def __init__(self):
        self.world = None
        self.agent = None
        self.game_running = False
        self.paused = True
        self.step_delay = 1000
        self.last_step_time = 0
        
        # Game settings
        self.world_size = 8
        self.num_wumpus = 2
        self.pit_prob = 0.2
        self.random_agent = False
        self.moving_wumpus = False
        
    def draw_cell(self, x, y, cell):
        cell_x = GRID_ORIGIN[0] + x * GRID_SIZE
        cell_y = GRID_ORIGIN[1] + y * GRID_SIZE
        cell_rect = pygame.Rect(cell_x, cell_y, GRID_SIZE, GRID_SIZE)
        
        # Base color
        color = WHITE
        if cell.isSafe:
            color = GREEN
        elif cell.isDangerous:
            color = RED
        elif cell.isVisited:
            color = LIGHT_GRAY
            
        pygame.draw.rect(screen, color, cell_rect)
        pygame.draw.rect(screen, BLACK, cell_rect, 1)
        
        # Draw symbols
        center_x = cell_x + GRID_SIZE // 2
        center_y = cell_y + GRID_SIZE // 2
        
        if cell.getPit:
            pygame.draw.circle(screen, BROWN, (center_x, center_y), 15)
        if cell.getWumpus:
            pygame.draw.polygon(screen, PURPLE, [(center_x-10, center_y+10), 
                                                (center_x, center_y-15), 
                                                (center_x+10, center_y+10)])
        if cell.getGold:
            pygame.draw.circle(screen, YELLOW, (center_x, center_y), 10)
        if cell.getBreeze:
            text = font_small.render("~", True, BLUE)
            screen.blit(text, (cell_x + 5, cell_y + 5))
        if cell.getStench:
            text = font_small.render("S", True, PURPLE)
            screen.blit(text, (cell_x + GRID_SIZE - 15, cell_y + 5))
            
        # Draw agent
        if self.agent and self.agent.location == (x, y):
            pygame.draw.circle(screen, BLACK, (center_x, center_y), 8)
    
    def draw_world(self):
        if not self.world:
            return
            
        for y in range(self.world.size):
            for x in range(self.world.size):
                cell = self.world.listCells[y][x]
                self.draw_cell(x, y, cell)
    
    def setup_game_screen(self):
        running = True
        
        # Input boxes
        size_input = InputBox(150, 100, 100, 30, str(self.world_size))
        wumpus_input = InputBox(150, 150, 100, 30, str(self.num_wumpus))
        pit_input = InputBox(150, 200, 100, 30, str(self.pit_prob))
        
        # Buttons
        random_button = Button("Random Agent: No", 50, 250, 200, 40, ATOMIC_TANGERINE)
        moving_button = Button("Moving Wumpus: No", 50, 300, 200, 40, ZOMP)
        start_button = Button("Start Game", 50, 400, 150, 50, GREEN, self.start_game)
        back_button = Button("Back", 50, 500, 100, 40, RED, self.show_menu)
        
        inputs = [size_input, wumpus_input, pit_input]
        buttons = [random_button, moving_button, start_button, back_button]
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                for inp in inputs:
                    inp.handle_event(event)
                
                for button in buttons:
                    button.handle_event(event)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if random_button.rect.collidepoint(event.pos):
                        self.random_agent = not self.random_agent
                        random_button.text = f"Random Agent: {'Yes' if self.random_agent else 'No'}"
                    elif moving_button.rect.collidepoint(event.pos):
                        self.moving_wumpus = not self.moving_wumpus
                        moving_button.text = f"Moving Wumpus: {'Yes' if self.moving_wumpus else 'No'}"
            
            # Update values from inputs
            try:
                self.world_size = int(size_input.text) if size_input.text else 8
                self.num_wumpus = int(wumpus_input.text) if wumpus_input.text else 2
                self.pit_prob = float(pit_input.text) if pit_input.text else 0.2
            except ValueError:
                pass
            
            screen.fill(CREAM)
            
            # Labels
            screen.blit(font_medium.render("Game Setup", True, BLACK), (50, 50))
            screen.blit(font_small.render("World Size:", True, BLACK), (50, 105))
            screen.blit(font_small.render("Number of Wumpus:", True, BLACK), (50, 155))
            screen.blit(font_small.render("Pit Probability:", True, BLACK), (50, 205))
            
            for inp in inputs:
                inp.draw(screen)
            
            for button in buttons:
                button.draw(screen)
            
            pygame.display.flip()
            clock.tick(FPS)
            
            if self.game_running:
                running = False
    
    def start_game(self):
        self.agent = Agent(random=self.random_agent)
        self.world = WumpusWorld(size=self.world_size, num_wumpus=self.num_wumpus, 
                                pit_prob=self.pit_prob, agent=self.agent, 
                                moving_wumpus=self.moving_wumpus)
        self.game_running = True
        self.game_loop()
    
    def game_loop(self):
        running = True
        
        # Control buttons
        play_button = Button("Play", 50, 50, 80, 40, GREEN, self.toggle_pause)
        reset_button = Button("Reset", 50, 100, 80, 40, ATOMIC_TANGERINE, self.reset_game)
        menu_button = Button("Menu", 50, 150, 80, 40, RED, self.show_menu)
        
        buttons = [play_button, reset_button, menu_button]
        
        while running and self.game_running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                for button in buttons:
                    button.handle_event(event)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.toggle_pause()
                    elif event.key == pygame.K_r:
                        self.reset_game()
            
            # Update pause button text
            play_button.text = "Pause" if not self.paused else "Play"
            
            # Game step
            if not self.paused and current_time - self.last_step_time > self.step_delay:
                if self.agent.alive and not self.agent.out:
                    self.game_step()
                    self.last_step_time = current_time
                else:
                    self.paused = True
            
            # Draw everything
            screen.fill(CREAM)
            
            for button in buttons:
                button.draw(screen)
            
            self.draw_world()
            self.draw_info()
            
            pygame.display.flip()
            clock.tick(FPS)
    
    def game_step(self):
        # Get percepts and update KB
        self.agent.percepts = self.world.tell_agent_percept()
        self.world.reset_scream_bump()
        
        self.agent.tell()
        self.agent.infer_surrounding_cells()
        self.world.update_agent_known_cells()
        
        # Agent selects action
        action = self.agent.select_action()
        
        # Update world state
        self.world.update_world(action=action)
        self.agent.update_visited_location()
    
    def draw_info(self):
        info_x = 50
        info_y = 250
        line_height = 25
        
        info_texts = [
            f"Location: {self.agent.location}",
            f"Direction: {self.agent.direction}",
            f"Score: {self.agent.score}",
            f"Has Gold: {self.agent.has_gold}",
            f"Has Arrow: {self.agent.has_arrow}",
            f"Alive: {self.agent.alive}",
            f"Percepts: {self.agent.percepts}"
        ]
        
        for i, text in enumerate(info_texts):
            surf = font_small.render(text, True, BLACK)
            screen.blit(surf, (info_x, info_y + i * line_height))
    
    def toggle_pause(self):
        self.paused = not self.paused
    
    def reset_game(self):
        self.game_running = False
        self.setup_game_screen()
    
    def show_menu(self):
        self.game_running = False
        self.menu_loop()
    
    def menu_loop(self):
        running = True
        
        title = font_large.render("Wumpus World AI", True, AMARANTH_PURPLE)
        
        buttons = [
            Button("Start Game", WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50, ATOMIC_TANGERINE, self.setup_game_screen),
            Button("Quit", WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, AMARANTH_PURPLE, lambda: pygame.quit() or sys.exit())
        ]
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                for button in buttons:
                    button.handle_event(event)
            
            screen.fill(CREAM)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
            
            for button in buttons:
                button.draw(screen)
            
            pygame.display.flip()
            clock.tick(FPS)
            
            if self.game_running:
                running = False

def main():
    gui = WumpusWorldGUI()
    gui.menu_loop()

if __name__ == "__main__":
    main()