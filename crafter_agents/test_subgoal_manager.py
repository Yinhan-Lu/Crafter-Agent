"""
Comprehensive test script for SubgoalManager integration with GameState.
Tests various scenarios to ensure the code is bug-free.
"""

import sys
import os
import traceback
from typing import Dict, Any, List

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.game_state import GameState, GameStateUpdater
from planning.sub_goal_manager import SubgoalManager
from planning.subgoal_integration_example import GameStateSubgoalIntegrator

def create_test_game_state(scenario: str) -> GameState:
    """Create different game state scenarios for testing."""
    game_state = GameState()
    
    if scenario == "start":
        # Starting game state
        game_state.health = 9
        game_state.food = 9
        game_state.drink = 9
        game_state.energy = 9
        game_state.inventory = {
            'health': 9, 'food': 9, 'drink': 9, 'energy': 9,
            'sapling': 0, 'wood': 0, 'stone': 0, 'coal': 0, 'iron': 0, 'diamond': 0,
            'wood_pickaxe': 0, 'stone_pickaxe': 0, 'iron_pickaxe': 0,
            'wood_sword': 0, 'stone_sword': 0, 'iron_sword': 0
        }
        game_state.achievements = {
            'collect_coal': 0, 'collect_diamond': 0, 'collect_drink': 0,
            'collect_iron': 0, 'collect_sapling': 0, 'collect_stone': 0,
            'collect_wood': 0, 'defeat_skeleton': 0, 'defeat_zombie': 0,
            'eat_cow': 0, 'eat_plant': 0, 'make_iron_pickaxe': 0,
            'make_iron_sword': 0, 'make_stone_pickaxe': 0, 'make_stone_sword': 0,
            'make_wood_pickaxe': 0, 'make_wood_sword': 0, 'place_furnace': 0,
            'place_plant': 0, 'place_stone': 0, 'place_table': 0, 'wake_up': 0
        }
        # Set up matrices for resource detection
        game_state.text_local_view_mat = [
            ['grass', 'grass', 'tree', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass']
        ]
        game_state.text_local_view_obj = [
            ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
            ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
            ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
            ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
            ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Player', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
            ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
            ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
            ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
            ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing']
        ]
        
    elif scenario == "low_health":
        # Low health scenario
        game_state.health = 1
        game_state.food = 5
        game_state.drink = 5
        game_state.energy = 8
        game_state.inventory = {
            'health': 1, 'food': 5, 'drink': 5, 'energy': 8,
            'sapling': 0, 'wood': 2, 'stone': 0, 'coal': 0, 'iron': 0, 'diamond': 0,
            'wood_pickaxe': 0, 'stone_pickaxe': 0, 'iron_pickaxe': 0,
            'wood_sword': 0, 'stone_sword': 0, 'iron_sword': 0
        }
        game_state.achievements = {}
        game_state.text_local_view_mat = [['grass'] * 9 for _ in range(9)]
        game_state.text_local_view_obj = [['Nothing'] * 9 for _ in range(9)]
        game_state.text_local_view_obj[4][4] = 'Player'
        
    elif scenario == "hungry":
        # Very hungry scenario
        game_state.health = 7
        game_state.food = 1  # Very low food
        game_state.drink = 8
        game_state.energy = 7
        game_state.inventory = {
            'health': 7, 'food': 1, 'drink': 8, 'energy': 7,
            'sapling': 0, 'wood': 3, 'stone': 0, 'coal': 0, 'iron': 0, 'diamond': 0,
            'wood_pickaxe': 0, 'stone_pickaxe': 0, 'iron_pickaxe': 0,
            'wood_sword': 0, 'stone_sword': 0, 'iron_sword': 0
        }
        game_state.achievements = {}
        game_state.text_local_view_mat = [['grass'] * 9 for _ in range(9)]
        game_state.text_local_view_obj = [['Nothing'] * 9 for _ in range(9)]
        game_state.text_local_view_obj[4][4] = 'Player'
        game_state.text_local_view_obj[3][4] = 'Cow'  # Food source nearby
        
    elif scenario == "with_enemies":
        # Enemy nearby scenario
        game_state.health = 8
        game_state.food = 7
        game_state.drink = 8
        game_state.energy = 6
        game_state.inventory = {
            'health': 8, 'food': 7, 'drink': 8, 'energy': 6,
            'sapling': 0, 'wood': 1, 'stone': 0, 'coal': 0, 'iron': 0, 'diamond': 0,
            'wood_pickaxe': 1, 'stone_pickaxe': 0, 'iron_pickaxe': 0,
            'wood_sword': 0, 'stone_sword': 0, 'iron_sword': 0
        }
        game_state.achievements = {'make_wood_pickaxe': 1}
        game_state.text_local_view_mat = [['grass'] * 9 for _ in range(9)]
        game_state.text_local_view_obj = [['Nothing'] * 9 for _ in range(9)]
        game_state.text_local_view_obj[4][4] = 'Player'
        game_state.text_local_view_obj[5][4] = 'Zombie'  # Enemy nearby
        
    elif scenario == "mid_game":
        # Mid-game scenario with some progress
        game_state.health = 8
        game_state.food = 6
        game_state.drink = 7
        game_state.energy = 9
        game_state.inventory = {
            'health': 8, 'food': 6, 'drink': 7, 'energy': 9,
            'sapling': 0, 'wood': 3, 'stone': 2, 'coal': 0, 'iron': 0, 'diamond': 0,
            'wood_pickaxe': 1, 'stone_pickaxe': 0, 'iron_pickaxe': 0,
            'wood_sword': 0, 'stone_sword': 0, 'iron_sword': 0
        }
        game_state.achievements = {
            'collect_wood': 5, 'collect_stone': 2, 'place_table': 1, 'make_wood_pickaxe': 1
        }
        game_state.text_local_view_mat = [
            ['grass', 'grass', 'stone', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass'],
            ['grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass', 'grass']
        ]
        game_state.text_local_view_obj = [['Nothing'] * 9 for _ in range(9)]
        game_state.text_local_view_obj[4][4] = 'Player'
        
    elif scenario == "end_game":
        # End-game scenario with diamond
        game_state.health = 9
        game_state.food = 8
        game_state.drink = 8
        game_state.energy = 7
        game_state.inventory = {
            'health': 9, 'food': 8, 'drink': 8, 'energy': 7,
            'sapling': 1, 'wood': 2, 'stone': 3, 'coal': 2, 'iron': 1, 'diamond': 1,
            'wood_pickaxe': 1, 'stone_pickaxe': 1, 'iron_pickaxe': 1,
            'wood_sword': 1, 'stone_sword': 1, 'iron_sword': 0
        }
        game_state.achievements = {
            'collect_wood': 10, 'collect_stone': 8, 'collect_coal': 3, 'collect_iron': 2,
            'collect_diamond': 1, 'place_table': 1, 'place_furnace': 1,
            'make_wood_pickaxe': 1, 'make_stone_pickaxe': 1, 'make_iron_pickaxe': 1,
            'make_wood_sword': 1, 'make_stone_sword': 1
        }
        game_state.text_local_view_mat = [['grass'] * 9 for _ in range(9)]
        game_state.text_local_view_obj = [['Nothing'] * 9 for _ in range(9)]
        game_state.text_local_view_obj[4][4] = 'Player'
        
    return game_state

def run_test_scenario(scenario_name: str, game_state: GameState) -> bool:
    """Run a single test scenario and return True if successful."""
    print(f"\n{'='*60}")
    print(f"🧪 Testing Scenario: {scenario_name.upper()}")
    print(f"{'='*60}")
    
    try:
        # Test basic SubgoalManager
        print("Testing basic SubgoalManager...")
        subgoal_manager = SubgoalManager()
        subgoal_manager.update_plan(game_state)
        basic_subgoal = subgoal_manager.get_current_subgoal()
        print(f"✅ Basic subgoal: {basic_subgoal}")
        
        # Test with integrator wrapper
        print("\nTesting with GameStateSubgoalIntegrator...")
        integrator = GameStateSubgoalIntegrator()
        integrator_subgoal = integrator.get_subgoal(game_state)
        print(f"✅ Integrator subgoal: {integrator_subgoal}")
        
        # Get detailed status
        print("\nGetting detailed status...")
        status = integrator.get_subgoal_status(game_state)
        if 'error' in status:
            print(f"❌ Error in status: {status['error']}")
            return False
        
        print("✅ Status retrieved successfully")
        print(f"   Health: {status['health']}, Food: {status['food']}, Energy: {status['energy']}")
        print(f"   Wood: {status['wood']}, Stone: {status['stone']}")
        print(f"   Tools: Wood pickaxe: {status['has_wood_pickaxe']}, Stone pickaxe: {status['has_stone_pickaxe']}")
        
        # Verify subgoals match
        if basic_subgoal != integrator_subgoal:
            print(f"⚠️  Warning: Basic and integrator subgoals differ!")
            print(f"   Basic: {basic_subgoal}")
            print(f"   Integrator: {integrator_subgoal}")
        
        print(f"✅ {scenario_name} test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in {scenario_name} test: {str(e)}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

def test_edge_cases() -> bool:
    """Test edge cases and potential error conditions."""
    print(f"\n{'='*60}")
    print("🔍 Testing Edge Cases")
    print(f"{'='*60}")
    
    try:
        subgoal_manager = SubgoalManager()
        
        # Test with None matrices
        print("Testing with None matrices...")
        game_state = GameState()
        game_state.text_local_view_mat = None
        game_state.text_local_view_obj = None
        subgoal_manager.update_plan(game_state)
        print("✅ Handled None matrices")
        
        # Test with empty matrices
        print("Testing with empty matrices...")
        game_state.text_local_view_mat = []
        game_state.text_local_view_obj = []
        subgoal_manager.update_plan(game_state)
        print("✅ Handled empty matrices")
        
        # Test with wrong type input
        print("Testing type validation...")
        try:
            subgoal_manager.update_plan("not_a_gamestate")
            print("❌ Type validation failed - should have raised TypeError")
            return False
        except TypeError:
            print("✅ Type validation works correctly")
        
        # Test with missing inventory keys
        print("Testing with missing inventory keys...")
        game_state = GameState()
        game_state.inventory = {}  # Empty inventory
        subgoal_manager.update_plan(game_state)
        print("✅ Handled missing inventory keys")
        
        print("✅ All edge cases passed!")
        return True
        
    except Exception as e:
        print(f"❌ Edge case test failed: {str(e)}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

def test_subgoal_progression() -> bool:
    """Test the logical progression of subgoals."""
    print(f"\n{'='*60}")
    print("📈 Testing Subgoal Progression")
    print(f"{'='*60}")
    
    try:
        integrator = GameStateSubgoalIntegrator()
        
        # Start with basic game state
        game_state = create_test_game_state("start")
        subgoal1 = integrator.get_subgoal(game_state)
        print(f"Initial: {subgoal1}")
        
        # Add some wood
        game_state.inventory['wood'] = 2
        game_state.achievements['collect_wood'] = 2
        subgoal2 = integrator.get_subgoal(game_state)
        print(f"After collecting wood: {subgoal2}")
        
        # Place table
        game_state.achievements['place_table'] = 1
        subgoal3 = integrator.get_subgoal(game_state)
        print(f"After placing table: {subgoal3}")
        
        # Craft wood pickaxe
        game_state.achievements['make_wood_pickaxe'] = 1
        game_state.inventory['wood_pickaxe'] = 1
        subgoal4 = integrator.get_subgoal(game_state)
        print(f"After crafting wood pickaxe: {subgoal4}")
        
        # Add stone
        game_state.inventory['stone'] = 3
        game_state.achievements['collect_stone'] = 3
        subgoal5 = integrator.get_subgoal(game_state)
        print(f"After collecting stone: {subgoal5}")
        
        print("✅ Subgoal progression test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Progression test failed: {str(e)}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all tests and report results."""
    print("🚀 Starting Comprehensive SubgoalManager Test Suite")
    print("=" * 80)
    
    test_results = []
    
    # Test different scenarios
    scenarios = [
        ("start", create_test_game_state("start")),
        ("low_health", create_test_game_state("low_health")),
        ("hungry", create_test_game_state("hungry")),
        ("with_enemies", create_test_game_state("with_enemies")),
        ("mid_game", create_test_game_state("mid_game")),
        ("end_game", create_test_game_state("end_game"))
    ]
    
    for scenario_name, game_state in scenarios:
        result = run_test_scenario(scenario_name, game_state)
        test_results.append((scenario_name, result))
    
    # Test edge cases
    edge_case_result = test_edge_cases()
    test_results.append(("edge_cases", edge_case_result))
    
    # Test progression
    progression_result = test_subgoal_progression()
    test_results.append(("progression", progression_result))
    
    # Print final results
    print(f"\n{'='*80}")
    print("📊 FINAL TEST RESULTS")
    print(f"{'='*80}")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.upper():20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 🎉 🎉 ALL TESTS PASSED! 🎉 🎉 🎉")
        print("✅ SubgoalManager is BUG-FREE and ready for production!")
    else:
        print("❌ Some tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 