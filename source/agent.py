from enum import Enum
import random

from inference import InferenceEngine
from environment import Environment
class Orientation(Enum):
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class Agent:
    def __init__(self) -> None:
        self.location = (0, 0)
        self.orientations = [Orientation.UP, Orientation.RIGHT, Orientation.DOWN, Orientation.LEFT]
        self.orientation_index = 1 
        self.orientation = self.orientations[self.orientation_index]
        self.has_arrow = True
        self.score = 0
        self.has_escaped = False
        self.has_gold = False
        self.actions = [self.move_forward, self.turn_left, self.turn_right,
                        self.grab, self.shoot, self.climb_out]
        
        # kb = Knowledge Base
        self.kb = InferenceEngine()
    
    def move_forward(self) -> None:
        if self.orientation == Orientation.LEFT or self.orientation == Orientation.RIGHT:
            self.location += self.orientation
        else:
            self.location -= self.orientation
        self.score -= 1
    
    def turn_left(self) -> None:
        self.orientation_index = (self.orientation_index - 1) % 4
        self.orientation = self.orientations[self.orientation_index]
        self.score -= 1
    
    def turn_right(self) -> None:
        self.orientation_index = (self.orientation_index + 1) % 4
        self.orientation = self.orientations[self.orientation_index]
        self.score -= 1

    def grab(self) -> None:
        self.has_gold = True
        self.score += 10

    def shoot(self) -> None:
        self.has_arrow = False
        self.score -= 10

    def climb_out(self) -> None:
        if self.location == (0, 0):
            self.has_escaped = True
            if self.has_gold:
                self.score += 1000
    
    def die(self) -> None:
        self.score -= 1000
    
    'Select action after inference and planning'
    def select_action(self) -> None:
        pass

class RandomAgent(Agent):
    def __init__(self):
        super().__init__()

    def select_action(self) -> None:
        action_selected_index = random.randint(0, len(self.actions) - 1)
        self.actions[action_selected_index]()
