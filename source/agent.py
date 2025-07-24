from enum import Enum
from inference import InferenceEngine
from environment import Environment
class Direction(Enum):
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
class Agent:
    def __init__(self):
        self.location = (0, 0)
        self.directions = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        self.orientation_index = 1 
        self.orientation = self.directions[self.orientation_index]
        self.has_arrow = True
        self.score = 0
        self.has_escaped = False
        self.has_gold = False
        self.actions = [self.move_forward, self.turn_left, self.turn_right,
                        self.grab, self.shoot, self.climb_out]
        
        # kb = Knowledge Base
        self.kb = InferenceEngine()
    
    def move_forward(self):
        if self.orientation == Direction.LEFT or self.orientation == Direction.RIGHT:
            self.location += self.orientation
        else:
            self.location -= self.orientation
        self.score -= 1
    
    def turn_left(self):
        self.orientation_index = (self.orientation_index - 1) % 4
        self.orientation = self.directions[self.orientation_index]
        self.score -= 1
    
    def turn_right(self):
        self.orientation_index = (self.orientation_index + 1) % 4
        self.orientation = self.directions[self.orientation_index]
        self.score -= 1

    def grab(self):
        self.has_gold = True
        self.score += 10

    def shoot(self):
        self.has_arrow = False
        self.score -= 10

    def climb_out(self):
        if self.location == (0, 0):
            self.has_escaped = True
            if self.has_gold:
                self.score += 1000
    
    def die(self):
        self.score -= 1000
    
