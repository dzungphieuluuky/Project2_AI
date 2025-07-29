class Agent:
    def __init__(self, start=(0, 0)) -> None:
        self.location = start
        self.direction = "RIGHT"  # mặc định quay phải
        self.has_arrow = True
        self.has_gold = False
        self.score = 0
        self.alive = True
        self.out = False  # đã ra khỏi hang chưa
        self.DIRECTIONS = ["UP", "RIGHT", "DOWN", "LEFT"]  # theo thứ tự quay phải

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
