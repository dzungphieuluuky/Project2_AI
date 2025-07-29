from cell import Cell
from random import randrange, random, sample

class WumpusWorld:
    def __init__(self, size=8, num_wumpus=2, pit_prob=0.2) -> None:
        self.size = size
        self.numWumpus = num_wumpus
        self.p = pit_prob
        self.listTiles = [[Cell() for _ in range(size)] for _ in range(size)]
        #self.doorPos = (0, 0)

        # (0,0) luôn an toàn
        self.listTiles[0][0].markSafe()
        self.listTiles[0][0].setVisited()

        # Đặt hố ngẫu nhiên
        for x in range(size):
            for y in range(size):
                if (x, y) != (0, 0) and random() < self.p:
                    self.listTiles[x][y].setPit()

        # Đặt Wumpus ngẫu nhiên (không trùng, không nằm trong hố)
        available_positions = [(x, y) for x in range(size) for y in range(size)
                               if (x, y) != (0, 0) and not self.listTiles[x][y].getPit()]
        wumpus_positions = sample(available_positions, self.numWumpus)
        for (x, y) in wumpus_positions:
            self.listTiles[x][y].setWumpus()

        # Đặt vàng ngẫu nhiên (không nằm cùng hố hoặc wumpus)
        gold_candidates = [(x, y) for x in range(size) for y in range(size)
                           if (x, y) != (0, 0)
                           and not self.listTiles[x][y].getPit()
                           and not self.listTiles[x][y].getWumpus()]
        gold_x, gold_y = sample(gold_candidates, 1)[0]
        self.listTiles[gold_x][gold_y].setGold()

        # Sinh breeze và stench cho các ô lân cận
        self._generate_percepts()

    def _generate_percepts(self) -> None:
        for x in range(self.size):
            for y in range(self.size):
                if self.listTiles[x][y].getPit():
                    for nx, ny in self.get_Adjacents(x, y):
                        self.listTiles[nx][ny].setBreeze()
                if self.listTiles[x][y].getWumpus():
                    for nx, ny in self.get_Adjacents(x, y):
                        self.listTiles[nx][ny].setStench()

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
        if self.listTiles[x][y].getGold():
            self.listTiles[x][y].removeGold()
            return True  # successfully grabbed
        return False  # no gold

    def killWumpus(self, x: int, y: int) -> bool:
        """Kill the Wumpus at position (if present)"""
        if self.listTiles[x][y].getWumpus():
            self.listTiles[x][y].removeWumpus()
            # Remove stench from adjacent tiles
            for nx, ny in self.get_Adjacents(x, y):
                self.listTiles[nx][ny].removeStench()
            return True  # Wumpus killed
        return False  # no Wumpus

    def movePlayer(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> None:
        """Move the player from one cell to another"""
        fx, fy = from_pos
        tx, ty = to_pos

        # Remove from old position
        self.listTiles[fx][fy].removePlayer()

        # Add to new position
        self.listTiles[tx][ty].setPlayer()
        self.listTiles[tx][ty].setVisited()  # mark as visited

    # debug 
    def printWorld(self)-> None:
        print("\n========== WUMPUS WORLD ==========")
        for y in reversed(range(self.size)):  # y từ cao xuống thấp (hàng trên xuống hàng dưới)
            row = ""
            for x in range(self.size):        # x từ trái sang phải
                cell = self.listTiles[x][y]
                content = cell.printTile()
                if content == "":
                    content = "Empty"
                row += f"[{content:^12}]"  # căn giữa trong ô rộng 12 ký tự
            print(row)
        print("==================================\n")
