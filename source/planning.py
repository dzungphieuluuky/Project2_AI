import heapq

class Planner:
    def __init__(self):
        pass

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, cell, known_world_state, size):
        x, y = cell
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size:
                neighbor_cell = known_world_state[nx][ny]
                if neighbor_cell is not None and neighbor_cell.isSafe():
                    neighbors.append((nx, ny))
        return neighbors

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def find_path(self, start, goal, known_world_state):
        size = len(known_world_state)

        gx, gy = goal
        if known_world_state[gx][gy] is None or not known_world_state[gx][gy].isSafe():
            return None

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                return self.reconstruct_path(came_from, current)

            for neighbor in self.get_neighbors(current, known_world_state, size):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None     
    
    def _count_unknown_neighbors(self, location, known_cells, world_size):
        count = 0; known_locs = {c.location for c in known_cells}
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = location[0] + dx, location[1] + dy
            if 0 <= nx < world_size and 0 <= ny < world_size and (nx, ny) not in known_locs:
                count += 1
        return count

    def find_nearest_unvisited_safe(self, known_cells, visited_locations, location, world_size):
        candidates = [c.location for c in known_cells if c.isSafe() and c.location not in visited_locations]
        if not candidates: return None
        sortable_candidates = []
        for loc in candidates:
            dist = abs(loc[0] - location[0]) + abs(loc[1] - location[1])
            unknown_count = self._count_unknown_neighbors(loc, known_cells, world_size)
            sortable_candidates.append( ((dist, -unknown_count), loc) )
        sortable_candidates.sort(key=lambda x: x[0])
        return sortable_candidates[0][1]

    def get_next_move_towards(self, target, world_size, known_cells, direction, directions, location):
        grid = [[None for _ in range(world_size)] for _ in range(world_size)]
        for c in known_cells:
            x, y = c.location
            grid[x][y] = c
        path = self.find_path(location, target, grid)
        if not path or len(path) < 2:
            return None 
        next_step = path[1]
        dx = next_step[0] - location[0]
        dy = next_step[1] - location[1]
        desired_direction = None
        if dx == 1: 
            desired_direction = "RIGHT"
        elif dx == -1: 
            desired_direction = "LEFT"
        elif dy == 1: 
            desired_direction = "UP"
        elif dy == -1: 
            desired_direction = "DOWN"

        if direction == desired_direction:
            return "f"

        idx_current = directions.index(direction)
        idx_desired = directions.index(desired_direction)
        if (idx_current - idx_desired) % 4 == 1:
            return "l"
        else: 
            return "r"

    def find_best_wumpus_target(self, known_cells, visited_locations, clauses, world_size): 
        suspects = {}
        for cell in known_cells:
            if cell.location not in visited_locations and not cell.isSafe():
                wumpus_literal = f"W{cell.location[0]}-{cell.location[1]}"
                for clause in clauses:
                    if wumpus_literal in clause and len(clause) > 1:
                        if cell.location not in suspects: suspects[cell.location] = 0
                        suspects[cell.location] += 1
        
        if not suspects: return None

        high_utility_suspects = {
            loc: score for loc, score in suspects.items() 
            if self._count_unknown_neighbors(loc, known_cells, world_size) > 0
        }

        if not high_utility_suspects: 
            return None
        return max(high_utility_suspects, key=high_utility_suspects.get)

    def aim_and_shoot(self, target, location, direction, directions):
        tx, ty = target
        ax, ay = location
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

        if direction == desired_dir:
            return "s"
    
        idx_cur = directions.index(direction)
        idx_des = directions.index(desired_dir)
        if (idx_cur - idx_des) % 4 == 1:
            return "l"
        else: 
            return "r"