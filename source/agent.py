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
        self.DIRECTIONS = ["UP", "RIGHT", "DOWN", "LEFT"]  # theo thứ tự quay phải
        self.actions = [self.turn_left, self.turn_right, self.move_forward,
                        self.grab, self.shoot, self.climb_out]
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

