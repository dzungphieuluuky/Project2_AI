import random
from knowledge_base import KnowledgeBase
from planning import Planner

class Agent:
    def __init__(self, start=(0, 0), random=False) -> None:
        self.location = start
        self.DIRECTIONS = ["UP", "RIGHT", "DOWN", "LEFT"]  # theo thứ tự quay phải
        self.direction = "RIGHT"  # mặc định quay phải

        self.has_arrow = True
        self.has_gold = False
        self.score = 0
        self.alive = True
        self.out = False  # đã ra khỏi hang chưa
        self.has_just_shoot = False

        self.name_actions = {"f": "Move Forward", 
                        "l": "Turn Left", 
                        "r": "Turn Right", 
                        "g": "Grab", 
                        "s": "Shoot", 
                        "c": "Climb Out"}
        self.selected_action = "None"
        self.is_random = random

        self.total_percepts = {}
        self.adjacent_cells = []
        self.known_cells = []
        self.percepts = {}
        self.unreachable_safe = set()

        self.kb = KnowledgeBase()
        self.planner = Planner()

        self.visited_locations = {start}
        self.world_size = 8

    def get_Adjacents(self, i: int, j: int) -> list[tuple[int, int]]:
        adj = []
        if i - 1 >= 0:
            adj.append((i - 1, j))
        if i + 1 < self.world_size:
            adj.append((i + 1, j))
        if j - 1 >= 0:
            adj.append((i, j - 1))
        if j + 1 < self.world_size:
            adj.append((i, j + 1))
        return adj
    
    def get_adjacent_cells(self) -> list[tuple[int, int]]:
        i, j = self.location
        return self.get_Adjacents(i, j)
    
    def update_visited_location(self):
        self.visited_locations.add(self.location)
    
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
            self.has_just_shoot = True
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

    def get_percepts_from(self, world):
        """Lấy percept tại vị trí agent hiện tại"""
        x, y = self.location
        tile = world.listCells[x][y]
        new_percept = {
            "breeze": tile.getBreeze(),
            "stench": tile.getStench(),
            "glitter": tile.getGold(),
            "bump": world.bump_flag,  # chưa xử lý tường
            "scream": world.scream_flag  # được xử lý khi bắn trúng Wumpus
        }
        self.total_percepts[self.location] = new_percept
        self.percepts = new_percept
    
    def tell(self) -> None:
        self.adjacent_cells = self.get_adjacent_cells()
        self.kb.tell(self.percepts, self.location, self.adjacent_cells)

        if self.has_just_shoot:
            self.kb.percepts_after_shoot(self.location, self.direction, self.percepts, 
                                         self.known_cells, self.world_size)
            self.has_just_shoot = False
    
    def update_kb(self) -> None:
        if not self.alive:
            return
        x, y = self.location
        self.kb.add_clause({f"~P{x}-{y}"})
        self.kb.add_clause({f"~W{x}-{y}"})
    
    def infer_surrounding_cells(self) -> None:
        self.kb.full_resolution_closure()
        self.kb.infer_safe_and_dangerous_cells(self.known_cells)

    def show_knowledge(self):
        print("💡 Knowledge Base:")
        print(self.kb.clauses)
            
    def select_action(self):
        # if agent is random
        if self.is_random:
            action = random.choice([key for key in self.name_actions.keys()])
            self.selected_action = self.name_actions[action]
            return action
        
        # Priority 1: If Glitter is present, grab it.
        if self.percepts.get("glitter", False):
            print("Priority 1: Glitter found. Grabbing gold.")
            action = "g"
            self.selected_action = self.name_actions[action]
            return action

        # Priority 2: If we have the gold, plan a path to (0,0) and climb.
        if self.has_gold:
            print("Priority 2: Has gold. Planning path to (0,0).")
            if self.location == (0,0):
                action = "c"
                self.selected_action = self.name_actions[action]
                return action
            move = self.planner.get_next_move_towards((0, 0), self.world_size, self.known_cells,
                                                      self.direction, self.DIRECTIONS, self.location)
            if move:
                self.selected_action = f"Planning to move towards (0,0). Current action: {self.name_actions[move]}"
                return move


        # Priority 3: Find the best guaranteed safe, unvisited cell and move there.
        target = self.planner.find_nearest_unvisited_safe(self.known_cells, self.visited_locations, 
                                                          self.location, self.world_size)
        if target:
            print(f"Priority 3: Found best safe cell {target}. Planning path.")
            move = self.planner.get_next_move_towards(target, self.world_size, self.known_cells,
                                                      self.direction, self.DIRECTIONS, self.location)
            if move:
                self.selected_action = f"Planning to explore {target}. Current action: {self.name_actions[move]}"
                return move
            else:
                self.unreachable_safe.add(target)


        # Priority 4: If no safe moves, consider a calculated risk: shoot a suspected Wumpus.
        if self.has_arrow:
            wumpus_target = self.planner.find_best_wumpus_target(self.known_cells, self.visited_locations, 
                                                                 self.kb.clauses, self.world_size)
            if wumpus_target:
                print(f"Priority 4: No safe options. Risking shot at suspected Wumpus {wumpus_target}.")
                move = self.planner.aim_and_shoot(wumpus_target, self.location, self.direction, self.DIRECTIONS)
                if move:
                    self.selected_action = f"Planning to shoot at {wumpus_target}. Current action: {self.name_actions[move]}"
                    return move

        # Priority 5: If completely stuck, retreat to (0,0) and climb out.
        print("Priority 5: No other options. Retreating to (0,0) to climb.")
        if self.location == (0, 0):
            action = "c"
            self.selected_action = self.name_actions[action]
            return action
        
        move = self.planner.get_next_move_towards((0, 0), self.world_size, self.known_cells,
                                        self.direction, self.DIRECTIONS, self.location)
        if move:
            self.selected_action = f"Retreat to (0,0): {self.name_actions[move]}"
            return move

        # fallback solution
        return 'l'