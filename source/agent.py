import random

from knowledge_base import KnowledgeBase
from planning import Planner


class Agent:
    def __init__(self, start=(0, 0), random=False) -> None:
        self.location = start
        self.direction = "RIGHT"  # mặc định quay phải
        self.has_arrow = True
        self.has_gold = False
        self.score = 0
        self.alive = True
        self.out = False  # đã ra khỏi hang chưa
        self.is_exit = False # chưa exit game
        self.DIRECTIONS = ["UP", "RIGHT", "DOWN", "LEFT"]  # theo thứ tự quay phải
        self.actions = ["forward", "left", "right", "grab", "shoot", "climb", "exit"]
        self.selected_action = "None"
        self.is_random = random

        self.known_cells = []
        self.adjacent_cells = []
        self.percepts = {}

        self.kb = KnowledgeBase()
        # self.planner = Planner()

    def turn_left(self) -> None:
        idx = self.DIRECTIONS.index(self.direction)
        self.direction = self.DIRECTIONS[(idx - 1) % 4]
        self.score -= 1

    def turn_right(self) -> None:
        idx = self.DIRECTIONS.index(self.direction)
        self.direction = self.DIRECTIONS[(idx + 1) % 4]
        self.score -= 1

    def move_forward(self) -> None: # bump xử lí ở main
        x, y = self.location
        if self.direction == "UP":
            self.location = (x, y + 1)
        elif self.direction == "DOWN":
            self.location = (x, y - 1)
        elif self.direction == "LEFT":
            self.location = (x - 1, y)
        elif self.direction == "RIGHT":
            self.location = (x + 1, y)
        self.score -= 1

    def grab(self) -> None:
        self.has_gold = True
        self.score += 10  

    def shoot(self) -> bool:
        if self.has_arrow:
            self.has_arrow = False
            self.score -= 10 
            return True
        return False

    def climb_out(self) -> None:
        if self.location == (0, 0):
            self.out = True
            self.score += 1000 * self.has_gold
    
    def exit(self):
        self.is_exit = True
    
    def die(self) -> None:
        self.alive = False
        self.score -= 1000

    def tell(self) -> None:
        self.kb.tell(self.percepts, self.location, self.adjacent_cells)
    
    def update_kb(self) -> None:
        x, y = self.location
        self.kb.add_clause({f"~P{x}{y}"})
        self.kb.add_clause({f"~W{x}{y}"})
    
    def infer_surrounding_cells(self) -> None:
        self.kb.full_resolution_closure()
        self.kb.infer_safe_and_dangerous_cells(self.known_cells)

    def show_knowledge(self):
        print("💡 Knowledge Base:")
        print(self.kb.clauses)
    
    def select_action(self) -> str:
        if self.is_random:
            action = random.sample(['f', 'l', 'r', 'g', 's', 'c', 'e'], k=1)[0]
        else:
            action = input("Hành động (forward / left / right / grab / shoot / climb / exit): ").strip().lower()
            if action not in ['f', 'l', 'r', 'g', 's', 'c', 'e']:
                action = None
                self.selected_action = "None"
        if action == "f":
            self.selected_action = "forward"
        elif action == "l":
            self.selected_action = "turn left"
        elif action == "r":
            self.selected_action = "turn right"
        elif action == "g":
            self.selected_action = "grab gold"
        elif action == "s":
            self.selected_action = "shoot"
        elif action == "c":
            self.selected_action = "climb out"
        elif action == "e":
            self.selected_action = "exit"
        return action
        
        
