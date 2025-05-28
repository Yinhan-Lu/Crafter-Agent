from typing import Dict, List, Tuple, Optional, Callable
from enum import Enum, auto
from PIL import Image
import base64
import io
import crafter
import openai
import numpy as np
import matplotlib.pyplot as plt
import random
import json
import time
import agents as agents
from basic_actions import *
from game.game_state import *

class Direction(Enum):
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()



class ActionSpace:
    def __init__(self):
        self.actions: Dict[str, Tuple[str, str, Callable[[GameState], bool]]] = {}

    def update_actions_from_dict(self, action_dict: Dict[str, Tuple[str, str, Callable[[GameState], bool]]]):
        """Update actions from a dictionary."""
        self.actions.update(action_dict)

    def add_action(self, name: str, description: str, condition_desc: str, condition_func: Callable[[GameState], bool]):
        """Add a single action to the action space."""
        self.actions[name] = (description, condition_desc, condition_func)

    def get_valid_actions(self, game_state: GameState) -> List[str]:
        """Get a list of currently valid actions based on the game state."""
        return [name for name, (_, _, condition) in self.actions.items() if condition(game_state)]
    
    def get_invalid_actions(self, game_state: GameState) -> List[str]:
        """Get a list of currently invalid actions based on the game state."""
        return [name for name, (_, _, condition) in self.actions.items() if (not condition(game_state))]

    def is_action_valid(self, action_name: str, game_state: GameState) -> bool:
        """Check if a specific action is currently valid."""
        if action_name not in self.actions:
            return False
        return self.actions[action_name][2](game_state)  # Index 2 is the condition function

    def get_valid_action_prompt(self, game_state: GameState) -> str:
        """Generate a prompt string listing all valid actions with their descriptions."""
        valid_actions = self.get_valid_actions(game_state)
        prompt = "You can perform the following actions:\n"
        for action in valid_actions:
            description, condition_desc, _ = self.actions[action]
            prompt += f"- {action}: {description} ({condition_desc})\n"
        return prompt
    
    def get_invalid_action_prompt(self, game_state: GameState) -> str:
        """Generate a prompt string listing all invalid actions with their descriptions."""
        invalid_actions = self.get_invalid_actions(game_state)
        prompt = "You can't perform the following actions:\n"
        for action in invalid_actions:
            description, condition_desc, _ = self.actions[action]
            prompt += f"- {action}: {description} ({condition_desc})\n"
        return prompt

    def get_action_info(self, action_name: str) -> Tuple[str, str]:
        """Get the description and condition description for a specific action."""
        if action_name not in self.actions:
            raise ValueError(f"Invalid action: {action_name}")
        description, condition_desc, _ = self.actions[action_name]
        return description, condition_desc

def initialize_action_space() -> ActionSpace:
    action_space = ActionSpace()
    action_space.update_actions_from_dict(action_conditions)
    return action_space
