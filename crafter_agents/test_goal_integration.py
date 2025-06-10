#!/usr/bin/env python3
"""
Test the complete goal system integration:
1. SubgoalManager generates dynamic subgoals
2. Structured prompts include goal section (section 8)
3. Display shows goal information
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.game_state import GameState
from game.action_space import initialize_action_space
from utils.memory import Recent_Results
from agents.structured_prompts import get_goal_descriptions, build_complete_prompt
from planning.sub_goal_manager import SubgoalManager

def test_goal_integration():
    """Test complete goal system integration."""
    print("🧪 Testing Complete Goal System Integration")
    print("=" * 60)
    
    # Create test game state
    print("1. Creating test game state...")
    game_state = GameState()
    game_state.health = 8
    game_state.food = 6
    game_state.drink = 7
    game_state.energy = 9
    game_state.inventory = {
        'health': 8, 'food': 6, 'drink': 7, 'energy': 9,
        'wood': 2, 'stone': 0, 'coal': 0, 'iron': 0, 'diamond': 0,
        'sapling': 0, 'wood_pickaxe': 0, 'stone_pickaxe': 0, 'iron_pickaxe': 0,
        'wood_sword': 0, 'stone_sword': 0, 'iron_sword': 0
    }
    game_state.achievements = {'collect_wood': 2}
    print("✅ Game state created")
    
    # Test SubgoalManager directly
    print("\n2. Testing SubgoalManager...")
    subgoal_manager = SubgoalManager()
    subgoal_manager.update_plan(game_state)
    subgoal = subgoal_manager.get_current_subgoal()
    print(f"✅ SubgoalManager subgoal: {subgoal}")
    
    # Test goal descriptions
    print("\n3. Testing goal descriptions...")
    goal_desc = get_goal_descriptions(game_state)
    print("✅ Goal descriptions generated")
    print(f"Preview: {goal_desc[:200]}...")
    
    # Test that goal descriptions contain required elements
    print("\n4. Testing goal description content...")
    if "### Goal Descriptions" in goal_desc:
        print("✅ Goal section header present")
    else:
        print("❌ Missing goal section header")
        return False
    
    if "Main Objective (Fixed Goal)" in goal_desc:
        print("✅ Main objective section present")
    else:
        print("❌ Missing main objective section")
        return False
    
    if "Current Subgoal (Dynamic)" in goal_desc:
        print("✅ Dynamic subgoal section present")
    else:
        print("❌ Missing dynamic subgoal section")
        return False
    
    if "find and collect a diamond" in goal_desc.lower():
        print("✅ Main goal (diamond) mentioned")
    else:
        print("❌ Main goal not mentioned")
        return False
    
    if subgoal.lower() in goal_desc.lower():
        print("✅ Current subgoal integrated into description")
    else:
        print("❌ Current subgoal not integrated")
        return False
    
    # Test different game states for subgoal progression
    print("\n5. Testing subgoal progression...")
    
    # State 2: Place table
    game_state.achievements['place_table'] = 1
    subgoal_manager.update_plan(game_state)
    subgoal2 = subgoal_manager.get_current_subgoal()
    print(f"After placing table: {subgoal2[:50]}...")
    
    # State 3: Craft wood pickaxe
    game_state.achievements['make_wood_pickaxe'] = 1
    game_state.inventory['wood_pickaxe'] = 1
    subgoal_manager.update_plan(game_state)
    subgoal3 = subgoal_manager.get_current_subgoal()
    print(f"After crafting wood pickaxe: {subgoal3[:50]}...")
    
    # Verify subgoals are different (progression working)
    if subgoal != subgoal2 != subgoal3:
        print("✅ Subgoals change with game progression")
    else:
        print("❌ Subgoals not changing properly")
        return False
    
    print("\n✅ All goal integration tests passed!")
    print("📋 Summary:")
    print("  - SubgoalManager generates dynamic subgoals ✓")
    print("  - Goal descriptions include main objective and current subgoal ✓")
    print("  - Subgoals update based on game progression ✓")
    print("  - Goal section properly formatted for prompts ✓")
    
    return True

if __name__ == "__main__":
    success = test_goal_integration()
    if success:
        print("\n🎉 Goal system integration is working perfectly!")
        sys.exit(0)
    else:
        print("\n❌ Goal system integration has issues!")
        sys.exit(1) 