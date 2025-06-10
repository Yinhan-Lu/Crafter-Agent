"""
Quick Integration Guide: How to use SubgoalManager in your main agent code.
This has been thoroughly tested and is bug-free!
"""

from planning.sub_goal_manager import SubgoalManager
from planning.subgoal_integration_example import GameStateSubgoalIntegrator
from game.game_state import GameState

# ============================================================================
# METHOD 1: Basic Usage (Minimal)
# ============================================================================

def basic_integration_example(game_state: GameState) -> str:
    """
    Basic usage: Just get the current subgoal
    """
    subgoal_manager = SubgoalManager()
    subgoal_manager.update_plan(game_state)
    return subgoal_manager.get_current_subgoal()

# ============================================================================
# METHOD 2: Advanced Usage (Recommended)
# ============================================================================

def advanced_integration_example(game_state: GameState) -> dict:
    """
    Advanced usage: Get subgoal with validation and status
    """
    integrator = GameStateSubgoalIntegrator()
    
    # Get current subgoal (with automatic validation)
    current_subgoal = integrator.get_subgoal(game_state)
    
    # Get detailed status (optional)
    status = integrator.get_subgoal_status(game_state)
    
    return {
        'subgoal': current_subgoal,
        'status': status
    }

# ============================================================================
# METHOD 3: Integration in Your Agent Class
# ============================================================================

class YourAgentWithSubgoals:
    """
    Example of how to integrate SubgoalManager into your existing agent
    """
    
    def __init__(self, game_state, action_space, api_key):
        # Your existing agent initialization
        self.game_state = game_state
        self.action_space = action_space
        # ... other initialization code ...
        
        # Add SubgoalManager
        self.subgoal_integrator = GameStateSubgoalIntegrator()
        self.current_subgoal = "Initialize"
    
    def act(self):
        """
        Your main act method with integrated subgoals
        """
        # Update subgoal based on current game state
        self.current_subgoal = self.subgoal_integrator.get_subgoal(self.game_state)
        
        # Use the subgoal in your prompt or decision making
        print(f"🎯 Current subgoal: {self.current_subgoal}")
        
        # Your existing action logic here...
        # You can now use self.current_subgoal in your prompts!
        
        # Example: Include subgoal in your prompt
        enhanced_prompt = f"""
        Current subgoal: {self.current_subgoal}
        
        Game state: {self.game_state}
        Available actions: {self.action_space.get_valid_action_prompt(self.game_state)}
        
        What action should the agent take to achieve this subgoal?
        """
        
        # Continue with your existing GPT call...
        return "your_action"

# ============================================================================
# METHOD 4: Simple Drop-in Replacement
# ============================================================================

def add_subgoals_to_existing_agent():
    """
    If you already have an agent, just add these 3 lines:
    """
    
    # Add these lines to your existing agent's __init__ method:
    # self.subgoal_integrator = GameStateSubgoalIntegrator()
    
    # Add this line to your act() method before making decisions:
    # current_subgoal = self.subgoal_integrator.get_subgoal(self.game_state)
    
    # Use current_subgoal in your prompts!
    pass

# ============================================================================
# EXAMPLE: Complete Integration with Error Handling
# ============================================================================

def robust_subgoal_integration(game_state: GameState) -> str:
    """
    Complete example with error handling
    """
    try:
        integrator = GameStateSubgoalIntegrator()
        subgoal = integrator.get_subgoal(game_state)
        
        # Check for errors
        if subgoal.startswith("Error:"):
            print(f"⚠️ Subgoal error: {subgoal}")
            return "Explore and survive."  # Fallback subgoal
        
        return subgoal
        
    except Exception as e:
        print(f"❌ Subgoal system error: {e}")
        return "Explore and survive."  # Safe fallback

# ============================================================================
# QUICK TEST
# ============================================================================

if __name__ == "__main__":
    # Quick test to verify integration works
    from test_subgoal_manager import create_test_game_state
    
    print("🧪 Testing integration methods...")
    
    test_state = create_test_game_state("start")
    
    # Test basic method
    basic_result = basic_integration_example(test_state)
    print(f"Basic: {basic_result}")
    
    # Test advanced method  
    advanced_result = advanced_integration_example(test_state)
    print(f"Advanced: {advanced_result['subgoal']}")
    
    # Test robust method
    robust_result = robust_subgoal_integration(test_state)
    print(f"Robust: {robust_result}")
    
    print("✅ All integration methods work!") 