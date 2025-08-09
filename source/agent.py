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
        self.actions = {"f": "forward", 
                        "l": "turn left", 
                        "r": "turn right", 
                        "g": "grab", 
                        "s": "shoot", 
                        "c": "climb", 
                        "e": "exit"}
        self.selected_action = "None"
        self.is_random = random

        self.known_cells = []
        self.adjacent_cells = []
        self.percepts = {}
        self.unreachable_safe = set()

        self.kb = KnowledgeBase()
        self.planner = Planner()

        self.visited_locations = {start}
        self.world_size = 8

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
    
    def _count_unknown_neighbors(self, location):
        count = 0; known_locs = {c.location for c in self.known_cells}
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = location[0] + dx, location[1] + dy
            if 0 <= nx < self.world_size and 0 <= ny < self.world_size and (nx, ny) not in known_locs:
                count += 1
        return count

    def find_nearest_unvisited_safe(self):
        candidates = [c.location for c in self.known_cells if c.isSafe() and c.location not in self.visited_locations]
        if not candidates: return None
        sortable_candidates = []
        for loc in candidates:
            dist = abs(loc[0] - self.location[0]) + abs(loc[1] - self.location[1])
            unknown_count = self._count_unknown_neighbors(loc)
            sortable_candidates.append( ((dist, -unknown_count), loc) )
        sortable_candidates.sort(key=lambda x: x[0])
        return sortable_candidates[0][1]

    def get_next_move_towards(self, target):
        grid = [[None for _ in range(self.world_size)] for _ in range(self.world_size)]
        for c in self.known_cells:
            x, y = c.location
            grid[x][y] = c
        path = self.planner.find_path(self.location, target, grid)
        if not path or len(path) < 2:
            return None 
        next_step = path[1]
        dx = next_step[0] - self.location[0]
        dy = next_step[1] - self.location[1]
        desired_direction = None
        if dx == 1: 
            desired_direction = "RIGHT"
        elif dx == -1: 
            desired_direction = "LEFT"
        elif dy == 1: 
            desired_direction = "UP"
        elif dy == -1: 
            desired_direction = "DOWN"

        if self.direction == desired_direction:
            return "f"

        idx_current = self.DIRECTIONS.index(self.direction)
        idx_desired = self.DIRECTIONS.index(desired_direction)
        if (idx_current - idx_desired) % 4 == 1:
            return "l"
        else: 
            return "r"

    def find_best_wumpus_target(self): 
        suspects = {}
        for cell in self.known_cells:
            if cell.location not in self.visited_locations and not cell.isSafe():
                wumpus_literal = f"W{cell.location[0]}{cell.location[1]}"
                for clause in self.kb.clauses:
                    if wumpus_literal in clause and len(clause) > 1:
                        if cell.location not in suspects: suspects[cell.location] = 0
                        suspects[cell.location] += 1
        
        if not suspects: return None

        high_utility_suspects = {
            loc: score for loc, score in suspects.items() 
            if self._count_unknown_neighbors(loc) > 0
        }

        if not high_utility_suspects: 
            return None
        return max(high_utility_suspects, key=high_utility_suspects.get)

    def aim_and_shoot(self, target):
        tx, ty = target
        ax, ay = self.location
        desired_dir = None
        if ax == tx:
            if ty > ay: 
                desired_dir = "UP"
            elif ty < ay: 
                desired_dir = "DOWN"
        elif ay == ty:
            if tx > ax: 
                desired_dir = "RIGHT"
            elif tx < ax: 
                desired_dir = "LEFT"
        if desired_dir is None:
            return None  

        if self.direction == desired_dir:
            return "s"  
    
        idx_cur = self.DIRECTIONS.index(self.direction)
        idx_des = self.DIRECTIONS.index(desired_dir)
        if (idx_cur - idx_des) % 4 == 1:
            return "l"
        else: 
            return "r"
            
    
    def select_action(self):
        if self.is_random:
            return random.choice(['f', 'l', 'r', 'g', 's', 'c', 'e'])
        
        # Priority 1: If Glitter is present, grab it.
        if self.percepts.get("glitter", False):
            print("[DEBUG] Priority 1: Glitter found. Grabbing gold.")
            self.selected_action = "grab"
            return "g"

        # Priority 2: If we have the gold, plan a path to (0,0) and climb.
        if self.has_gold:
            print("[DEBUG] Priority 2: Has gold. Planning path to (0,0).")
            if self.location == (0,0):
                self.selected_action = "climb"
                return "c"
            move = self.get_next_move_towards((0, 0))
            if move:
                self.selected_action = f"Move towards (0,0): {self.actions[move]}"
                return move
            else: 
                print("[DEBUG] Path to (0,0) blocked. Climbing from current location.")
                self.selected_action = "climb"
                return "c"


        # Priority 3: Find the best guaranteed safe, unvisited cell and move there.
        target = self.find_nearest_unvisited_safe()
        if target:
            print(f"[DEBUG] Priority 3: Found best safe cell {target}. Planning path.")
            move = self.get_next_move_towards(target)
            if move:
                self.selected_action = f"Explore to {target}: {self.actions[move]}"
                return move
            else:
                self.unreachable_safe.add(target)


        # Priority 4: If no safe moves, consider a calculated risk: shoot a suspected Wumpus.
        if self.has_arrow:
            wumpus_target = self.find_best_wumpus_target()
            if wumpus_target:
                print(f"[DEBUG] Priority 4: No safe options. Risking shot at suspected Wumpus {wumpus_target}.")
                move = self.aim_and_shoot(wumpus_target)
                if move:
                    self.selected_action = f"Shoot at {wumpus_target}: {self.actions[move]}"
                    return move

        # Priority 5: If completely stuck, retreat to (0,0) and climb out.
        print("[DEBUG] Priority 5: No other options. Retreating to (0,0) to climb.")
        if self.location == (0, 0):
            self.selected_action = "climb"
            return "c"
        
        move = self.get_next_move_towards((0, 0))
        if move:
            self.selected_action = f"Retreat to (0,0): {self.actions[move]}"
            return move

        print("[DEBUG] Cannot find path to (0,0). Climbing from current location.")
        self.selected_action = "climb"
        return "c"