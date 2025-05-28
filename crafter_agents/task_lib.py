from typing import Dict, List, Optional
from game.game_state import GameState

class Task:
    def __init__(self, name: str, prerequisites: List[str], required_items: Dict[str, int]):
        self.name = name
        self.prerequisites = prerequisites
        self.required_items = required_items
        self.completed = False

class TaskLibrary:
    def __init__(self):
        self.tasks = {
            # Basic Collection Tasks
            "collect_wood": Task("collect_wood", [], {}),
            "collect_stone": Task("collect_stone", 
                                ["collect_wood"], 
                                {"wood_pickaxe": 1}),
            "collect_coal": Task("collect_coal", 
                               ["collect_wood"], 
                               {"wood_pickaxe": 1}),
            "collect_iron": Task("collect_iron", 
                               ["collect_stone", "make_stone_pickaxe"], 
                               {"stone_pickaxe": 1}),
            "collect_diamond": Task("collect_diamond", 
                                  ["collect_iron", "make_iron_pickaxe"], 
                                  {"iron_pickaxe": 1}),
            "collect_sapling": Task("collect_sapling", [], {}),
            "collect_drink": Task("collect_drink", [], {}),

            # Crafting Tasks
            "make_wood_pickaxe": Task("make_wood_pickaxe", 
                                    ["collect_wood"], 
                                    {"wood": 1}),
            "make_stone_pickaxe": Task("make_stone_pickaxe", 
                                     ["collect_stone"], 
                                     {"wood": 1, "stone": 1}),
            "make_iron_pickaxe": Task("make_iron_pickaxe", 
                                    ["collect_iron", "collect_coal"], 
                                    {"wood": 1, "iron": 1, "coal": 1}),
            "make_wood_sword": Task("make_wood_sword", 
                                  ["collect_wood"], 
                                  {"wood": 1}),
            "make_stone_sword": Task("make_stone_sword", 
                                   ["collect_stone"], 
                                   {"wood": 1, "stone": 1}),
            "make_iron_sword": Task("make_iron_sword", 
                                  ["collect_iron", "collect_coal"], 
                                  {"wood": 1, "iron": 1, "coal": 1}),

            # Placement Tasks
            "place_stone": Task("place_stone", 
                              ["collect_stone"], 
                              {"stone": 1}),
            "place_table": Task("place_table", 
                              ["collect_wood"], 
                              {"wood": 2}),
            "place_furnace": Task("place_furnace", 
                                ["collect_stone"], 
                                {"stone": 4}),
            "place_plant": Task("place_plant", 
                              ["collect_sapling"], 
                              {"sapling": 1}),

            # Combat Tasks
            "defeat_skeleton": Task("defeat_skeleton", 
                                  ["make_wood_sword"], 
                                  {"wood_sword": 1}),
            "defeat_zombie": Task("defeat_zombie", 
                                ["make_wood_sword"], 
                                {"wood_sword": 1}),
            "eat_cow": Task("eat_cow", 
                          ["make_wood_sword"], 
                          {"wood_sword": 1}),
            "eat_plant": Task("eat_plant", [], {}),

            # Other Tasks
            "wake_up": Task("wake_up", [], {})
        }

    def get_next_task(self, game_state: GameState) -> Optional[str]:
        """
        Determines the next task to complete based on the current game state.
        """
        achievements = game_state.achievements
        inventory = game_state.inventory

        for task_name, task in self.tasks.items():
            # Skip if task is already completed
            if achievements.get(task_name, 0) > 0:
                continue

            # Check if prerequisites are met
            prereqs_met = all(achievements.get(prereq, 0) > 0 
                            for prereq in task.prerequisites)
            if not prereqs_met:
                continue

            return task_name
        
        return None

    def get_task_prompt(self, task_name: str, game_state: GameState) -> str:
        """
        Generates a prompt for the current task based on the game state.
        """
        task = self.tasks[task_name]
        inventory = game_state.inventory

        # Basic template for different task types
        prompts = {
            "collect_wood": lambda: (
                f"Task: Collect wood\n"
                f"Current wood: {inventory['wood']}\n"
                f"Nearby trees: {game_state.closest_wood}\n"
                f"Hint: Look for trees and collect wood from them."
            ),
            
            "collect_stone": lambda: (
                f"Task: Collect stone\n"
                f"Current stone: {inventory['stone']}\n"
                f"Required: Wood pickaxe (have: {inventory['wood_pickaxe']})\n"
                f"Hint: Use a wood pickaxe to mine stone."
            ),

            "collect_coal": lambda: (
                f"Task: Collect coal\n"
                f"Current coal: {inventory['coal']}\n"
                f"Required: Wood pickaxe (have: {inventory['wood_pickaxe']})\n"
                f"Hint: Use a wood pickaxe to mine coal."
            ),

            "make_wood_pickaxe": lambda: (
                f"Task: Craft a wood pickaxe\n"
                f"Current wood: {inventory['wood']}\n"
                f"Required: 1 wood, must be near a crafting table\n"
                f"Hint: Place a crafting table if needed, then craft the pickaxe."
            ),

            "place_table": lambda: (
                f"Task: Place a crafting table\n"
                f"Current wood: {inventory['wood']}\n"
                f"Required: 2 wood\n"
                f"Hint: Find a suitable location on grass, sand, or path to place the table."
            ),

            "collect_drink": lambda: (
                f"Task: Collect water to drink\n"
                f"Current drink level: {game_state.drink}\n"
                f"Hint: Find a water source and collect water from it."
            ),

            "eat_cow": lambda: (
                f"Task: Hunt and eat a cow\n"
                f"Nearby cows: {game_state.closest_cows}\n"
                f"Required: Wood sword (have: {inventory['wood_sword']})\n"
                f"Hint: Equip a sword and attack a cow."
            ),
        }

        # Generic prompt for tasks without specific templates
        default_prompt = (
            f"Task: {task_name}\n"
            f"Prerequisites: {', '.join(task.prerequisites) if task.prerequisites else 'None'}\n"
            f"Required items: {', '.join(f'{k}: {v}' for k, v in task.required_items.items())}\n"
            f"Current inventory: {', '.join(f'{k}: {v}' for k, v in inventory.items() if v > 0)}"
        )

        return prompts.get(task_name, lambda: default_prompt)()

    def is_task_possible(self, task_name: str, game_state: GameState) -> bool:
        """
        Checks if a task is currently possible given the game state.
        """
        task = self.tasks[task_name]
        inventory = game_state.inventory

        # Check if prerequisites are completed
        for prereq in task.prerequisites:
            if game_state.achievements.get(prereq, 0) == 0:
                return False

        # Check if required items are available
        for item, amount in task.required_items.items():
            if inventory.get(item, 0) < amount:
                return False

        return True
