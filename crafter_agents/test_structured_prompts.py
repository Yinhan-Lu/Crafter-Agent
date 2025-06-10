"""
Test script to verify the new structured prompt system works correctly.
"""

import sys
import os

# Add the current directory to the path
# 语法解释：os.path.dirname(os.path.abspath(__file__)) 获取当前文件的目录，os.path.abspath(__file__) 获取当前文件的绝对路径，os.path.append(os.path.dirname(os.path.abspath(__file__))) 将当前文件的目录添加到系统路径中，这样就可以导入当前文件中的模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.game_state import GameState
from game.action_space import ActionSpace, initialize_action_space
from agents.structured_prompts import build_complete_prompt
from utils.memory import Recent_Results
import numpy as np

def test_structured_prompts():
    """Test the structured prompt system with a sample game state."""
    
    print("🧪 Testing Structured Prompt System")
    print("=" * 50)
    
    # Create a test game state with proper initialization
    game_state = GameState()
    game_state.health = 8
    game_state.food = 6
    game_state.drink = 7
    game_state.energy = 5
    
    # Initialize basic inventory
    game_state.inventory = {
        'wood': 3,
        'stone': 1,
        'coal': 0,
        'iron': 0,
        'diamond': 0,
        'sapling': 0,
        'wood_pickaxe': 1,
        'stone_pickaxe': 0,
        'iron_pickaxe': 0,
        'wood_sword': 0,
        'stone_sword': 0,
        'iron_sword': 0
    }
    
    # Set up walkable directions (simulate that all directions are walkable)
    game_state._walkable_directions = {
        'north': True,
        'south': True,
        'east': True,
        'west': True
    }
    
    # Set up turnable directions
    game_state._turnable_directions = {
        'north': True,
        'south': True,
        'east': True,
        'west': True
    }
    
    # Set target material (what the player is facing)
    game_state.target_material = "tree"
    
    # Set up local view with some materials
    game_state.text_local_view_mat = np.array([
        ['grass', 'grass', 'grass'],
        ['grass', 'player', 'tree'],
        ['grass', 'stone', 'grass']
    ])
    
    # Override the get_walkable_directions method to return our test data
    def mock_get_walkable_directions():
        return game_state._walkable_directions
    
    def mock_get_turnable_directions():
        return game_state._turnable_directions
    
    game_state.get_walkable_directions = mock_get_walkable_directions
    game_state.get_turnable_directions = mock_get_turnable_directions
    
    # Initialize action space
    action_space = initialize_action_space()
    
    # Create empty memory for testing
    recent_results = Recent_Results(num_of_results=5)
    
    try:
        print("Building structured prompt...")
        
        # Test the complete prompt generation
        prompt = build_complete_prompt(
            game_state=game_state,
            action_space=action_space,
            recent_results=recent_results
        )
        
        print("✅ Structured prompt generated successfully!")
        print("\n📝 Generated Prompt Preview (first 500 chars):")
        print("-" * 50)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("-" * 50)
        
        # Test valid/invalid actions specifically
        print("\n🎯 Testing Valid/Invalid Action Detection:")
        print("-" * 50)
        
        valid_actions = action_space.get_valid_actions(game_state)
        invalid_actions = action_space.get_invalid_actions(game_state)
        
        print(f"Valid actions ({len(valid_actions)}):")
        for action in valid_actions[:5]:  # Show first 5
            print(f"  ✅ {action}")
        if len(valid_actions) > 5:
            print(f"  ... and {len(valid_actions) - 5} more")
            
        print(f"\nInvalid actions ({len(invalid_actions)}):")
        for action in invalid_actions[:5]:  # Show first 5
            print(f"  ❌ {action}")
        if len(invalid_actions) > 5:
            print(f"  ... and {len(invalid_actions) - 5} more")
        
        print(f"\n📊 Total actions: {len(action_space.actions)}")
        print(f"📊 Valid: {len(valid_actions)}, Invalid: {len(invalid_actions)}")
        
        # Test the action prompts specifically
        print("\n📋 Testing Action Prompt Generation:")
        print("-" * 50)
        
        valid_prompt = action_space.get_valid_action_prompt(game_state)
        invalid_prompt = action_space.get_invalid_action_prompt(game_state)
        
        print("Valid Action Prompt (first 300 chars):")
        print(valid_prompt[:300] + "..." if len(valid_prompt) > 300 else valid_prompt)
        
        print("\nInvalid Action Prompt (first 300 chars):")
        print(invalid_prompt[:300] + "..." if len(invalid_prompt) > 300 else invalid_prompt)
        
    except Exception as e:
        print(f"❌ Error testing structured prompts: {e}")
        print("Traceback:", end=" ")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_structured_prompts() 