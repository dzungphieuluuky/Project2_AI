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
        return {
            "breeze": tile.getBreeze(),
            "stench": tile.getStench(),
            "glitter": tile.getGold(),
            "bump": world.bump_flag,  # chưa xử lý tường
            "scream": world.scream_flag  # được xử lý khi bắn trúng Wumpus
        }
    
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
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
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
            move = self.get_next_move_towards((0, 0))
            if move:
                self.selected_action = f"Planning to move towards (0,0). Current action: {self.name_actions[move]}"
                return move


        # Priority 3: Find the best guaranteed safe, unvisited cell and move there.
        target = self.find_nearest_unvisited_safe()
        if target:
            print(f"Priority 3: Found best safe cell {target}. Planning path.")
            move = self.get_next_move_towards(target)
            if move:
                self.selected_action = f"Planning to explore {target}. Current action: {self.name_actions[move]}"
                return move
            else:
                self.unreachable_safe.add(target)


        # Priority 4: If no safe moves, consider a calculated risk: shoot a suspected Wumpus.
        if self.has_arrow:
            wumpus_target = self.find_best_wumpus_target()
            if wumpus_target:
                print(f"Priority 4: No safe options. Risking shot at suspected Wumpus {wumpus_target}.")
                move = self.aim_and_shoot(wumpus_target)
                if move:
                    self.selected_action = f"Planning to shoot at {wumpus_target}. Current action: {self.name_actions[move]}"
                    return move

        # Priority 5: If completely stuck, retreat to (0,0) and climb out.
        print("Priority 5: No other options. Retreating to (0,0) to climb.")
        if self.location == (0, 0):
            action = "c"
            self.selected_action = self.name_actions[action]
            return action
        
        move = self.get_next_move_towards((0, 0))
        if move:
            self.selected_action = f"Retreat to (0,0): {self.name_actions[move]}"
            return move