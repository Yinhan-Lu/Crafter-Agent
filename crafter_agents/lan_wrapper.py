import crafter
import numpy as np

class CrafterLanguageWrapper:
    """
    A language wrapper for the Crafter environment that converts observations and actions
    to language representations.
    """
    
    def __init__(self):
        self.env = crafter.Env()  # Create the base environment
        
        # Define mappings for items based on actual Crafter items
        self.item_names = {
            'health': 'health',
            'food': 'food',
            'wood': 'wood',
            'stone': 'stone',
            'coal': 'coal',
            'iron': 'iron',
            'diamond': 'diamond',
            'stick': 'stick',
            'table': 'crafting table',
            'furnace': 'furnace',
            'plant': 'plant',
            'wooden_pickaxe': 'wooden pickaxe',
            'stone_pickaxe': 'stone pickaxe',
            'iron_pickaxe': 'iron pickaxe',
            'wooden_sword': 'wooden sword',
            'stone_sword': 'stone sword',
            'iron_sword': 'iron sword'
        }

    def _obs_to_language(self, obs):
        """Convert Crafter observation to language description."""
        description = []
        
        # Add health status - handle health as a scalar
        health = obs['health']
        description.append(f"Health: {health}/9")
        
        # Add inventory items
        inventory_items = []
        for item_name, value in obs.items():
            if item_name in self.item_names:
                if isinstance(value, (int, float, bool, np.bool_, np.integer, np.floating)):
                    if value > 0:
                        inventory_items.append(f"{self.item_names[item_name]} x{value}")
        
        if inventory_items:
            description.append("Inventory: " + ", ".join(inventory_items))
            
        # Add position and visual information if available
        if 'position' in obs:
            pos = obs['position']
            description.append(f"Position: ({pos[0]}, {pos[1]})")
            
        return " ".join(description)

    def reset(self):
        """Reset environment and convert observation to language."""
        obs = self.env.reset()
        return self._obs_to_language(obs)

    def step(self, action):
        """Take step and convert observation to language."""
        obs, reward, done, info = self.env.step(action)
        language_obs = self._obs_to_language(obs)
        return language_obs, reward, done, info

    def close(self):
        """Close the environment."""
        self.env.close()

# Example usage:
if __name__ == "__main__":
    # Create the wrapped environment
    env = CrafterLanguageWrapper()
    
    # Reset and get initial observation
    obs = env.reset()
    print("\nInitial observation:")
    print(obs)
    
    # Take a few random actions
    for i in range(5):
        action = np.random.randint(0, 17)  # Crafter has 17 actions
        obs, reward, done, info = env.step(action)
        print(f"\nStep {i+1} observation (action={action}):")
        print(obs)
        print(f"Reward: {reward}, Done: {done}")
        
        if done:
            break
    
    env.close()