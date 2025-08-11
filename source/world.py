from cell import Cell
from agent import Agent
from random import randrange, random, sample, choice

class WumpusWorld:
    def __init__(self, agent: Agent, size=8, num_wumpus=2, pit_prob=0.2, moving_wumpus = False) -> None:
        self.size = size
        self.numWumpus = num_wumpus
        self.wumpus_positions = []
        self.p = pit_prob
        self.counter = 0
        self.moving_wumpus = moving_wumpus
        self.scream_flag = False
        self.bump_flag = False

        self.listCells = [[Cell(x, y) for x in range(size)] for y in range(size)]
        self.agent = agent
        self.agent.world_size = size
        self.agent.known_cells.append(self.listCells[0][0])
        self.listCells[0][0].setPlayer()
        #self.doorPos = (0, 0)

        # (0,0) luôn an toàn
        self.listCells[0][0].markSafe()
        self.listCells[0][0].setVisited()

        # Đặt hố ngẫu nhiên
        for x in range(size):
            for y in range(size):
                if (x, y) != (0, 0) and random() < self.p:
                    self.listCells[x][y].setPit()

        # Đặt Wumpus ngẫu nhiên (không trùng, không nằm trong hố)
        available_positions = [(x, y) for x in range(size) for y in range(size)
                               if (x, y) != (0, 0) and not self.listCells[x][y].getPit()]
        wumpus_positions = sample(available_positions, self.numWumpus)
        self.wumpus_positions = wumpus_positions
        for (x, y) in wumpus_positions:
            self.listCells[x][y].setWumpus()

        # Đặt vàng ngẫu nhiên (không nằm cùng hố hoặc wumpus)
        gold_candidates = [(x, y) for x in range(size) for y in range(size)
                           if (x, y) != (0, 0)
                           and not self.listCells[x][y].getPit()
                           and not self.listCells[x][y].getWumpus()]
        gold_x, gold_y = sample(gold_candidates, 1)[0]
        self.listCells[gold_x][gold_y].setGold()

        # Sinh breeze và stench cho các ô lân cận
        self._generate_percepts()

    def _generate_percepts(self) -> None:
        # xoá các stench cũ
        for x in range(self.size):
            for y in range(self.size):
                self.listCells[x][y].removeStench()

        for x in range(self.size):
            for y in range(self.size):
                if self.listCells[x][y].getPit():
                    for nx, ny in self.get_Adjacents(x, y):
                        self.listCells[nx][ny].setBreeze()
                if self.listCells[x][y].getWumpus():
                    for nx, ny in self.get_Adjacents(x, y):
                        self.listCells[nx][ny].setStench()

    def generate_bump(self):
        self.bump_flag = True
    
    def generate_scream(self):
        self.scream_flag = True
    
    def reset_scream_bump(self):
        self.bump_flag = False
        self.scream_flag = False

    def tell_agent_adjacent_cells(self) -> None:
        x, y = self.agent.location
        adjacent_cells = self.get_Adjacents(x, y)
        self.agent.adjacent_cells = adjacent_cells
    
    def update_agent_known_cells(self) -> None:
        x, y = self.agent.location
        self.adjacent_cells = self.get_Adjacents(x, y)
        for (i, j) in self.adjacent_cells:
            if self.listCells[i][j] not in self.agent.known_cells:
                self.agent.known_cells.append(self.listCells[i][j])

    def get_Adjacents(self, i: int, j: int) -> list[tuple[int, int]]:
        adj = []
        if i - 1 >= 0:
            adj.append((i - 1, j))
        if i + 1 < self.size:
            adj.append((i + 1, j))
        if j - 1 >= 0:
            adj.append((i, j - 1))
        if j + 1 < self.size:
            adj.append((i, j + 1))
        return adj

    def grabGold(self, x: int, y: int) -> bool:
        """Agent grabs gold if it's in current cell"""
        if self.listCells[x][y].getGold():
            self.listCells[x][y].removeGold()
            return True  # successfully grabbed
        return False  # no gold

    def killWumpus(self, x: int, y: int) -> bool:
        """Kill the Wumpus at position (if present)"""
        if self.listCells[x][y].getWumpus():
            self.listCells[x][y].removeWumpus()
            # Remove stench from adjacent cells
            for nx, ny in self.get_Adjacents(x, y):
                self.listCells[nx][ny].removeStench()
            return True  # Wumpus killed
        return False  # no Wumpus

    def movePlayer(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> None:
        """Move the player from one cell to another"""
        fx, fy = from_pos
        tx, ty = to_pos

        # Remove from old position
        self.listCells[fx][fy].removePlayer()

        # Add to new position
        self.listCells[tx][ty].setPlayer()
        self.listCells[tx][ty].setVisited()  # mark as visited

    def move_all_wumpus(self):
        new_positions = []  
        planned_moves = {} 

        # Plan ô tiếp theo mõi wumpus di chuyển tới
        for (i, j) in self.wumpus_positions:
            old_pos = (i, j)
            wumpus_adj_cells = self.get_Adjacents(i, j)

            new_pos = choice(wumpus_adj_cells)
            new_x, new_y = new_pos

            if self.listCells[new_x][new_y].getWumpus() or self.listCells[new_x][new_y].getPit():
                new_pos = old_pos

            planned_moves[old_pos] = new_pos

        # Cập nhật wumpus ở ô mới
        for old_pos, new_pos in planned_moves.items():
            i, j = old_pos
            new_x, new_y = new_pos

            self.listCells[i][j].removeWumpus()

        for old_pos, new_pos in planned_moves.items():
            new_x, new_y = new_pos

            if new_pos == self.agent.location:
                self.agent.die()

            self.listCells[new_x][new_y].setWumpus()
            new_positions.append(new_pos)

        self.wumpus_positions = new_positions
        self._generate_percepts()

    def update_world(self, action: str) -> None:
        if action is None:
            print("Not a valid action!")
            return
        
        elif action == "f":
            old_pos = self.agent.location
            self.agent.move_forward()
            new_x, new_y = new_pos = self.agent.location

            # bump nếu ra ngoài
            if not (0 <= new_x < self.size and 0 <= new_y < self.size):
                self.agent.location = old_pos
                self.generate_bump()
                return

            # nếu rơi vào hố hoặc gặp wumpus thì chết
            cell = self.listCells[new_x][new_y]
            if cell.getPit() or cell.getWumpus():
                print("💀 Agent is dead!")
                self.agent.die()
                
            # an toàn → cập nhật ~Wxy và ~Pxy vào KB
            self.agent.update_kb()

            self.movePlayer(old_pos, new_pos)

        elif action == "l":
            self.agent.turn_left()

        elif action == "r":
            self.agent.turn_right()

        elif action == "g":
            x, y = self.agent.location
            if self.grabGold(x, y):
                self.agent.grab()

        elif action == "s":
            if self.agent.shoot():
                dx, dy = 0, 0
                if self.agent.direction == "UP":
                    dx, dy = 0, 1
                elif self.agent.direction == "DOWN":
                    dx, dy = 0, -1
                elif self.agent.direction == "LEFT":
                    dx, dy = -1, 0
                elif self.agent.direction == "RIGHT":
                    dx, dy = 1, 0

                x, y = self.agent.location
                while 0 <= x + dx < self.size and 0 <= y + dy < self.size:
                    x += dx
                    y += dy
                    if self.killWumpus(x, y):
                        self.generate_scream()
                        break

        elif action == "c":
            self.agent.climb_out()
            print("🧗 Agent has climbed out of the map")

        if self.moving_wumpus:
            self.counter += 1
            if self.counter % 5 == 0:
                self.move_all_wumpus()
    
    # debug 
    def printWorld(self)-> None:
        print("\n👽👽👽👽👽 WUMPUS WORLD 👽👽👽👽👽")
        for y in reversed(range(self.size)):  # y từ cao xuống thấp (hàng trên xuống hàng dưới)
            row = ""
            for x in range(self.size):        # x từ trái sang phải
                cell = self.listCells[x][y]
                content = cell.printTile()
                "Only display cells that has content and in agent's knowledge"
                if content == "" or cell not in self.agent.known_cells:
                    content = "?"
                row += f"[{content:^12}]"  # căn giữa trong ô rộng 12 ký tự
            print(row)
        print("==================================\n")
