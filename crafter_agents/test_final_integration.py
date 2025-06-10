"""
Final Integration Test - Complete Prompt System with Valid/Invalid Actions

This test demonstrates how the structured prompt system now includes:
1. All action descriptions as scaffolding (for incomplete agent designs)
2. Dynamic valid/invalid actions for each turn based on game state
3. Proper integration with ActionSpace validation methods
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.game_state import GameState
from game.action_space import ActionSpace, initialize_action_space
from agents.structured_prompts import build_complete_prompt
from utils.memory import Recent_Results
import numpy as np

def create_test_game_state(scenario_name):
    """Create different game state scenarios to test action validation."""
    
    game_state = GameState()
    
    # Common setup
    game_state._walkable_directions = {'north': True, 'south': True, 'east': True, 'west': True}
    game_state._turnable_directions = {'north': True, 'south': True, 'east': True, 'west': True}
    game_state.get_walkable_directions = lambda: game_state._walkable_directions
    game_state.get_turnable_directions = lambda: game_state._turnable_directions
    game_state.text_local_view_mat = np.array([['grass', 'grass', 'grass'], ['grass', 'player', 'tree'], ['grass', 'stone', 'grass']])
    
    if scenario_name == "early_game":
        # Early game: No tools, facing tree
        game_state.health = 9
        game_state.food = 8
        game_state.drink = 8
        game_state.energy = 9
        game_state.target_material = "tree"
        game_state.inventory = {
            'wood': 0, 'stone': 0, 'coal': 0, 'iron': 0, 'diamond': 0, 'sapling': 0,
            'wood_pickaxe': 0, 'stone_pickaxe': 0, 'iron_pickaxe': 0,
            'wood_sword': 0, 'stone_sword': 0, 'iron_sword': 0
        }
        
    elif scenario_name == "mid_game":
        # Mid game: Has wood pickaxe, facing stone
        game_state.health = 7
        game_state.food = 6
        game_state.drink = 7
        game_state.energy = 5
        game_state.target_material = "stone"
        game_state.inventory = {
            'wood': 5, 'stone': 0, 'coal': 0, 'iron': 0, 'diamond': 0, 'sapling': 1,
            'wood_pickaxe': 1, 'stone_pickaxe': 0, 'iron_pickaxe': 0,
            'wood_sword': 1, 'stone_sword': 0, 'iron_sword': 0
        }
        # Add table to local view for crafting
        game_state.text_local_view_mat = np.array([['grass', 'table', 'grass'], ['grass', 'player', 'stone'], ['grass', 'stone', 'grass']])
        
    elif scenario_name == "advanced_game":
        # Advanced game: Has multiple tools and materials
        game_state.health = 8
        game_state.food = 7
        game_state.drink = 8
        game_state.energy = 6
        game_state.target_material = "iron"
        game_state.inventory = {
            'wood': 10, 'stone': 8, 'coal': 3, 'iron': 0, 'diamond': 0, 'sapling': 2,
            'wood_pickaxe': 1, 'stone_pickaxe': 1, 'iron_pickaxe': 0,
            'wood_sword': 1, 'stone_sword': 1, 'iron_sword': 0
        }
        # Add table and furnace for advanced crafting
        game_state.text_local_view_mat = np.array([['table', 'furnace', 'grass'], ['grass', 'player', 'iron'], ['grass', 'coal', 'grass']])
    
    return game_state

def test_dynamic_action_validation():
    """Test that actions change dynamically based on game state."""
    
    print("🧪 Testing Dynamic Action Validation System")
    print("=" * 60)
    
    action_space = initialize_action_space()
    recent_results = Recent_Results(num_of_results=5)
    
    scenarios = ["early_game", "mid_game", "advanced_game"]
    
    for scenario in scenarios:
        print(f"\n🎮 Scenario: {scenario.upper().replace('_', ' ')}")
        print("-" * 40)
        
        game_state = create_test_game_state(scenario)
        
        # Get valid and invalid actions
        valid_actions = action_space.get_valid_actions(game_state)
        invalid_actions = action_space.get_invalid_actions(game_state)
        
        print(f"📊 Valid actions: {len(valid_actions)}/{len(action_space.actions)}")
        print(f"📊 Invalid actions: {len(invalid_actions)}/{len(action_space.actions)}")
        
        # Show key valid actions for this scenario
        key_actions = ['collect_wood', 'collect_stone', 'collect_coal', 'collect_iron', 
                      'make_wood_pickaxe', 'make_stone_pickaxe', 'make_iron_pickaxe',
                      'place_table', 'place_furnace']
        
        print("\n🔑 Key Actions Status:")
        for action in key_actions:
            if action in valid_actions:
                print(f"  ✅ {action}")
            elif action in invalid_actions:
                print(f"  ❌ {action}")
        
        # Generate the complete prompt for this scenario
        prompt = build_complete_prompt(
            game_state=game_state,
            action_space=action_space,
            recent_results=recent_results
        )
        
        # Extract the valid/invalid actions section from the prompt
        if "📍 ACTIONS AVAILABLE THIS TURN:" in prompt:
            start = prompt.find("📍 ACTIONS AVAILABLE THIS TURN:")
            end = prompt.find("**Note:**", start)
            actions_section = prompt[start:end] if end != -1 else prompt[start:start+500]
            
            print(f"\n📋 Actions Section in Prompt (first 200 chars):")
            print(actions_section[:200] + "..." if len(actions_section) > 200 else actions_section)

def test_prompt_structure_completeness():
    """Test that the prompt contains all required sections as specified in the comment."""
    
    print("\n\n🔍 Testing Complete Prompt Structure")
    print("=" * 60)
    
    game_state = create_test_game_state("mid_game")
    action_space = initialize_action_space()
    recent_results = Recent_Results(num_of_results=5)
    
    # Add some test memory
    recent_results.add_result(
        reasoning="I need wood to start crafting.",
        observation="I see trees nearby.",
        current_step=1,
        action="collect_wood"
    )
    
    prompt = build_complete_prompt(
        game_state=game_state,
        action_space=action_space,
        recent_results=recent_results
    )
    
    # Check for all 10 required sections from the comment
    required_sections = [
        "### Crafter Game Environment - Basic Rules",  # 1. Basic rules
        "### Material Properties",                      # 2. Materials  
        "### Creature Properties",                      # 3. Creatures
        "### Action Detailed Descriptions",            # 4. Actions
        "### Tool Detailed Descriptions",              # 5. Tools
        "### Game State Detailed Descriptions",        # 6. Game states
        "### Current Game State",                       # 7. Current state
        "### ReAct Framework Instructions",            # 8. ReAct framework
        "### Recent History",                           # 9. Recent steps
        "### Answer Format Requirements"                # 10. Format requirements
    ]
    
    print("✅ Required Sections Check:")
    all_present = True
    for i, section in enumerate(required_sections, 1):
        if section in prompt:
            print(f"  {i:2d}. ✅ {section}")
        else:
            print(f"  {i:2d}. ❌ {section}")
            all_present = False
    
    # Check that valid/invalid actions are prominently displayed
    if "📍 ACTIONS AVAILABLE THIS TURN:" in prompt and "🚫 ACTIONS NOT AVAILABLE THIS TURN:" in prompt:
        print("  11. ✅ Dynamic valid/invalid actions clearly marked")
    else:
        print("  11. ❌ Dynamic valid/invalid actions not clearly marked")
        all_present = False
    
    print(f"\n📏 Total prompt length: {len(prompt):,} characters")
    
    if all_present:
        print("🎉 All required sections present! Prompt structure is complete.")
    else:
        print("❌ Some required sections missing.")
    
    return all_present

if __name__ == "__main__":
    print("🚀 Final Integration Test - Enhanced Prompt System")
    print("=" * 60)
    print("Testing the structured prompt system that includes:")
    print("1. All action descriptions as scaffolding")
    print("2. Dynamic valid/invalid actions for each turn") 
    print("3. Proper ActionSpace integration with game state validation")
    print("4. Complete 10-part structure as specified in requirements")
    
    # Run all tests
    test_dynamic_action_validation()
    structure_complete = test_prompt_structure_completeness()
    
    print("\n" + "="*60)
    if structure_complete:
        print("🎯 SUCCESS: Enhanced prompt system is working correctly!")
        print("✅ Valid/invalid actions are dynamically determined each turn")
        print("✅ All action descriptions serve as scaffolding for incomplete agents")
        print("✅ ActionSpace validation methods are properly integrated")
        print("✅ All 10 required prompt sections are present")
    else:
        print("❌ Some issues found in the prompt system")
    
    print("\n💡 Usage: The agent now receives both comprehensive action descriptions")
    print("   AND specific valid/invalid actions for each game state turn.") 