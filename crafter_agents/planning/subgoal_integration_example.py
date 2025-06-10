"""
Example of how to integrate SubgoalManager with GameState class.
This file demonstrates proper usage and provides a wrapper class for easy integration.
"""

from typing import Optional
import sys
import os

# Add the parent directory to the path so we can import from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game_state import GameState
from planning.sub_goal_manager import SubgoalManager

class GameStateSubgoalIntegrator:
    """
    A wrapper class that integrates SubgoalManager with GameState.
    Provides additional validation and helper methods.
    """
    
    def __init__(self):
        self.subgoal_manager = SubgoalManager()
        self.last_subgoal = None
        
    def validate_game_state(self, game_state: GameState) -> bool:
        """
        Validate that the GameState has all required attributes.
        Returns True if valid, False otherwise.
        """
        required_attributes = [
            'health', 'food', 'drink', 'energy', 
            'inventory', 'achievements'
        ]
        
        for attr in required_attributes:
            if not hasattr(game_state, attr):
                print(f"WARNING: GameState missing required attribute: {attr}")
                return False
                
        # Check if inventory is a dictionary
        if not isinstance(game_state.inventory, dict):
            print(f"WARNING: GameState.inventory should be a dict, got {type(game_state.inventory)}")
            return False
            
        # Check if achievements is a dictionary
        if not isinstance(game_state.achievements, dict):
            print(f"WARNING: GameState.achievements should be a dict, got {type(game_state.achievements)}")
            return False
            
        return True
    
    def get_subgoal(self, game_state: GameState) -> str:
        """
        Get the current subgoal based on the game state.
        Returns the subgoal string or an error message if validation fails.
        """
        try:
            # Validate the game state first
            if not self.validate_game_state(game_state):
                return "Error: Invalid GameState - check console for details"
            
            # Update the subgoal plan
            self.subgoal_manager.update_plan(game_state)
            
            # Get the current subgoal
            current_subgoal = self.subgoal_manager.get_current_subgoal()
            
            # Check if subgoal changed
            if self.last_subgoal != current_subgoal:
                print(f"🎯 Subgoal changed: {current_subgoal}")
                self.last_subgoal = current_subgoal
            
            return current_subgoal
            
        except Exception as e:
            error_msg = f"Error in subgoal planning: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def get_subgoal_status(self, game_state: GameState) -> dict:
        """
        Get detailed status information about the current subgoal planning.
        Returns a dictionary with status information.
        """
        try:
            self.subgoal_manager.update_plan(game_state)
            
            return {
                'current_subgoal': self.subgoal_manager.get_current_subgoal(),
                'main_objective': self.subgoal_manager.main_objective,
                'has_wood_pickaxe': self.subgoal_manager.has_wood_pickaxe,
                'has_stone_pickaxe': self.subgoal_manager.has_stone_pickaxe,
                'has_iron_pickaxe': self.subgoal_manager.has_iron_pickaxe,
                'has_wood_sword': self.subgoal_manager.has_wood_sword,
                'has_stone_sword': self.subgoal_manager.has_stone_sword,
                'has_iron_sword': self.subgoal_manager.has_iron_sword,
                'table_placed': self.subgoal_manager.table_placed,
                'furnace_placed': self.subgoal_manager.furnace_placed,
                'health': game_state.health,
                'food': game_state.food,
                'drink': game_state.drink,
                'energy': game_state.energy,
                'wood': game_state.inventory.get('wood', 0),
                'stone': game_state.inventory.get('stone', 0),
                'coal': game_state.inventory.get('coal', 0),
                'iron': game_state.inventory.get('iron', 0),
                'diamond': game_state.inventory.get('diamond', 0)
            }
        except Exception as e:
            return {'error': str(e)}

def example_usage():
    """
    Example of how to use the SubgoalManager with GameState.
    """
    print("=== SubgoalManager Integration Example ===\n")
    
    # Create a sample GameState
    game_state = GameState()
    
    # Set some example values
    game_state.health = 8
    game_state.food = 6
    game_state.drink = 7
    game_state.energy = 9
    game_state.inventory = {
        'health': 8, 'food': 6, 'drink': 7, 'energy': 9,
        'wood': 2, 'stone': 0, 'coal': 0, 'iron': 0, 'diamond': 0,
        'wood_pickaxe': 0, 'stone_pickaxe': 0, 'iron_pickaxe': 0,
        'wood_sword': 0, 'stone_sword': 0, 'iron_sword': 0
    }
    game_state.achievements = {
        'collect_wood': 2, 'place_table': 0, 'make_wood_pickaxe': 0
    }
    
    # Create the integrator
    integrator = GameStateSubgoalIntegrator()
    
    # Get the current subgoal
    subgoal = integrator.get_subgoal(game_state)
    print(f"Current subgoal: {subgoal}\n")
    
    # Get detailed status
    status = integrator.get_subgoal_status(game_state)
    print("=== Detailed Status ===")
    for key, value in status.items():
        if key != 'error':
            print(f"{key}: {value}")
    
    print("\n=== Simulating Game Progress ===")
    
    # Simulate placing a table
    game_state.achievements['place_table'] = 1
    subgoal = integrator.get_subgoal(game_state)
    print(f"After placing table: {subgoal}")
    
    # Simulate crafting wood pickaxe
    game_state.achievements['make_wood_pickaxe'] = 1
    game_state.inventory['wood_pickaxe'] = 1
    game_state.inventory['wood'] = 1  # Still have some wood left
    subgoal = integrator.get_subgoal(game_state)
    print(f"After crafting wood pickaxe: {subgoal}")
    
    # Simulate getting some stone
    game_state.inventory['stone'] = 3
    subgoal = integrator.get_subgoal(game_state)
    print(f"After collecting stone: {subgoal}")

if __name__ == "__main__":
    example_usage() 