from typing import Dict, Any, List, Optional
from game.game_state import GameState

class SubgoalManager:
    """
    Crafter-specific sub-goal planning system.
    Decides and manages the current sub-goal(s) based on game state and long-term objectives.
    It handles hierarchical goals (crafting progression) and survival needs, and can adjust goals dynamically.
    """
    def __init__(self):
        # We can track long-term objectives and certain flags.
        self.main_objective = "Survive and obtain a diamond."
        # Flags to remember if key structures are placed (since state may not always show them if out of view).
        self.table_placed = False
        self.furnace_placed = False
        # Track if certain tools have been crafted (could also derive from achievements or inventory).
        self.has_wood_pickaxe = False
        self.has_stone_pickaxe = False
        self.has_iron_pickaxe = False
        self.has_wood_sword = False
        self.has_stone_sword = False
        self.has_iron_sword = False
        # Current top-level subgoal description (for prompt).
        self.current_subgoal = "Initialize"
        # We could use a stack or list to manage subgoal hierarchy explicitly if needed.
        self.goal_stack: List[str] = []
    
    def _extract_enemies_from_game_state(self, game_state: GameState) -> List[str]:
        """
        Extract enemy information from the GameState's local view.
        Returns a list of enemy types found nearby.
        """
        enemies = []
        if hasattr(game_state, 'text_local_view_obj') and game_state.text_local_view_obj is not None:
            for row in game_state.text_local_view_obj:
                for cell in row:
                    if cell in ['Zombie', 'Skeleton']:
                        enemies.append(cell.lower())
        return enemies
    
    def _extract_resources_from_game_state(self, game_state: GameState) -> List[str]:
        """
        Extract resource information from the GameState's local view.
        Returns a list of resources found nearby.
        """
        resources = []
        
        # Extract from material matrix
        if hasattr(game_state, 'text_local_view_mat') and game_state.text_local_view_mat is not None:
            for row in game_state.text_local_view_mat:
                for cell in row:
                    if cell in ['tree', 'stone', 'coal', 'iron', 'water', 'lava']:
                        if cell not in resources:
                            resources.append(cell)
        
        # Extract from object matrix
        if hasattr(game_state, 'text_local_view_obj') and game_state.text_local_view_obj is not None:
            for row in game_state.text_local_view_obj:
                for cell in row:
                    if cell in ['Cow', 'Plant']:
                        cell_lower = cell.lower()
                        if cell_lower not in resources:
                            resources.append(cell_lower)
        
        return resources

    def update_plan(self, game_state: GameState) -> None:
        """
        Update internal flags and determine the current highest-priority subgoal given the latest game state.
        This method sets self.current_subgoal (a descriptive string) to guide the agent's next action.
        """
        # Extract information from GameState object
        if not isinstance(game_state, GameState):
            raise TypeError(f"Expected GameState object, got {type(game_state)}")
        
        health = game_state.health
        # Fix field name mismatch and logic inversion
        hunger = 9 - game_state.food if game_state.food <= 9 else 0  # Convert food to hunger (higher hunger = more hungry)
        thirst = 9 - game_state.drink if game_state.drink <= 9 else 0  # Convert drink to thirst (higher thirst = more thirsty)
        energy = game_state.energy
        inventory = game_state.inventory
        achievements = game_state.achievements
        
        # Extract enemies and resources from the game state
        visible_enemies = self._extract_enemies_from_game_state(game_state)
        visible_resources = self._extract_resources_from_game_state(game_state)
        
        # Update known tool possession based on achievements or inventory.
        # If achievements are tracked, use them to mark crafted tools.
        if achievements:
            # Achievements like 'make_wood_pickaxe' etc. will have count 1 if done.
            self.has_wood_pickaxe = achievements.get('make_wood_pickaxe', 0) > 0
            self.has_stone_pickaxe = achievements.get('make_stone_pickaxe', 0) > 0
            self.has_iron_pickaxe = achievements.get('make_iron_pickaxe', 0) > 0
            self.has_wood_sword = achievements.get('make_wood_sword', 0) > 0
            self.has_stone_sword = achievements.get('make_stone_sword', 0) > 0
            self.has_iron_sword = achievements.get('make_iron_sword', 0) > 0
            # Table/furnace placement can be tracked via achievements as well.
            self.table_placed = self.table_placed or (achievements.get('place_table', 0) > 0)
            self.furnace_placed = self.furnace_placed or (achievements.get('place_furnace', 0) > 0)
        else:
            # If achievements not available, infer from inventory or prior flags (in a real scenario, state might explicitly list tools in inventory).
            # For example, if inventory has an item 'wood_pickaxe' or similar.
            self.has_wood_pickaxe = self.has_wood_pickaxe or (inventory.get('wood_pickaxe', 0) > 0)
            self.has_stone_pickaxe = self.has_stone_pickaxe or (inventory.get('stone_pickaxe', 0) > 0)
            self.has_iron_pickaxe = self.has_iron_pickaxe or (inventory.get('iron_pickaxe', 0) > 0)
            self.has_wood_sword = self.has_wood_sword or (inventory.get('wood_sword', 0) > 0)
            self.has_stone_sword = self.has_stone_sword or (inventory.get('stone_sword', 0) > 0)
            self.has_iron_sword = self.has_iron_sword or (inventory.get('iron_sword', 0) > 0)
            # For table/furnace, perhaps we can infer if inventory no longer has wood but a table was not yet placed; 
            # but that's unreliable. Instead, rely on our own flags which we set when we plan to place them.
            # (Alternatively, if state had a list of world objects nearby, we could see a 'table' or 'furnace' present.)
        
        # Check if diamond has been obtained (goal achieved). If yes, we can set subgoal to none or celebrate.
        # Diamond obtained might be indicated by achievement or having 'diamond' in inventory.
        if (achievements and achievements.get('collect_diamond', 0) > 0) or (inventory.get('diamond', 0) > 0):
            self.current_subgoal = "Goal accomplished! You obtained a diamond."
            return
        
        # 1. Survival high-priority checks (override other goals if urgent)
        # If any critical need, handle that first.
        # Define thresholds for critical levels (these can be tuned).
        critical_hunger = hunger > 7  # High hunger means low food
        critical_thirst = thirst > 7  # High thirst means low drink
        critical_energy = energy < 2  # Very low energy
        # Danger if multiple enemies or a strong enemy nearby.
        enemy_nearby = len(visible_enemies) > 0
        
        if health <= 2:  # Very low health, try to heal or avoid conflict
            if enemy_nearby:
                self.current_subgoal = "Health critical! Avoid enemies and find a safe spot."
            else:
                # If health is low but no enemies now, try to recover health.
                # Recovery could be by sleeping (if energy not full and no hunger/thirst issues) or by eating if hungry.
                if hunger > 4 or thirst > 4:  # If somewhat hungry/thirsty
                    # If health is low partly due to hunger/thirst, fix those first.
                    if hunger > thirst:
                        # hunger is higher - eat food if possible
                        if 'cow' in visible_resources or 'plant' in visible_resources:
                            self.current_subgoal = "Health low. Find food and eat to recover."
                        else:
                            self.current_subgoal = "Health low. Search for food to eat."
                    else:
                        # thirst is higher or equal - drink water
                        if 'water' in visible_resources:
                            self.current_subgoal = "Health low. Drink water to recover."
                        else:
                            self.current_subgoal = "Health low. Search for water to drink."
                else:
                    # Not particularly hungry/thirsty, maybe we just need to rest.
                    if energy < 5:
                        self.current_subgoal = "Health low. Find shelter and sleep to recover health."
                    else:
                        self.current_subgoal = "Health low. Avoid any danger and let health regenerate."
            return
        
        if critical_hunger:
            # Immediate need: eat something
            if 'cow' in visible_enemies or 'cow' in visible_resources:
                # Cow present, kill and eat it
                self.current_subgoal = "Starving! Hunt the cow and eat it now."
            elif 'plant' in visible_resources:
                # Edible plant/fruit present
                self.current_subgoal = "Starving! Eat the edible plant now."
            else:
                # No immediate food visible
                self.current_subgoal = "Starving! Urgently search for food (plants or animals)."
            return
        
        if critical_thirst:
            # Immediate need: drink water
            if 'water' in visible_resources:
                self.current_subgoal = "Dehydrated! Drink from the water now."
            else:
                self.current_subgoal = "Dehydrated! Urgently search for water to drink."
            return
        
        if critical_energy:
            # Too tired, must sleep very soon
            # Ideally, check for safety (no enemies nearby) before sleeping.
            if enemy_nearby:
                self.current_subgoal = "Exhausted! First, evade the enemy then find a safe spot to sleep."
            else:
                self.current_subgoal = "Exhausted! Sleep now to avoid collapse."
            return
        
        if enemy_nearby:
            # There is at least one enemy in vicinity.
            # Determine strategy based on equipment and health.
            enemy = visible_enemies[0]  # (We assume list contains descriptors like "zombie" or "skeleton")
            if (self.has_stone_sword or self.has_iron_sword or self.has_wood_sword):
                # We have a weapon, we can fight.
                self.current_subgoal = f"Defend yourself! Confront and defeat the {enemy}."
            else:
                # No sword; if we have a pickaxe it could be used at a pinch, but not ideal.
                if self.has_stone_pickaxe or self.has_iron_pickaxe or self.has_wood_pickaxe:
                    # We have some tool but it's not a proper weapon. Still, maybe fight if health is good.
                    if health > 5:
                        self.current_subgoal = f"A {enemy} is near! Use your tools to fight it off or keep distance."
                    else:
                        self.current_subgoal = f"A {enemy} is near and you're weak. Avoid it or retreat!"
                else:
                    # No tools or weapons at all.
                    self.current_subgoal = f"Unarmed and a {enemy} is nearby! Evade or hide immediately."
            return
        
        # 2. Long-term goal progression (diamond quest)
        # At this point, no immediate survival threat. Focus on progression toward diamond.
        
        # For clarity, define some handy variables for resource counts.
        wood = inventory.get('wood', 0)
        stone = inventory.get('stone', 0)
        coal = inventory.get('coal', 0)
        iron = inventory.get('iron', 0)
        # Also check if we have any saplings (for planting trees if wood is scarce).
        sapling = inventory.get('sapling', 0)
        
        # Check if we already have an Iron Pickaxe (then we can skip directly to finding diamond).
        if self.has_iron_pickaxe:
            # Already have the required tool for diamond. Next: find and mine a diamond.
            # Check if a diamond is visible in the current observation (perhaps unlikely, but just in case).
            if 'diamond' in visible_resources:
                self.current_subgoal = "Iron Pickaxe ready. Mine the diamond in sight!"
            else:
                self.current_subgoal = "Iron Pickaxe acquired. Explore caves/mountains to find a diamond."
            return
        
        # If no iron pickaxe yet, need to craft it via progression.
        # Step 1: Wooden Pickaxe (if not already have stone pick).
        if not self.has_stone_pickaxe:
            # Ensure we have a wooden pickaxe first.
            if not self.has_wood_pickaxe:
                # No wooden pickaxe yet: plan to craft one.
                # Need wood and a crafting table.
                if not self.table_placed:
                    # If table not placed, we will need to place one, which requires wood.
                    if wood < 1:
                        # No wood in inventory -> gather wood first.
                        if 'tree' in visible_resources:
                            self.current_subgoal = "No wood. Chop a tree to gather wood."
                        else:
                            self.current_subgoal = "No wood. Explore until you find a tree for wood."
                        return
                    else:
                        # We have wood but no table placed yet.
                        self.current_subgoal = "Place a crafting table using wood."
                        # Once we execute this, table_placed will be set to True via achievement or by us.
                        return
                else:
                    # Table is available (already placed).
                    if wood < 1:
                        # If somehow we have a table but no wood left (e.g., used it for the table), gather wood again to craft pickaxe.
                        if 'tree' in visible_resources:
                            self.current_subgoal = "Out of wood. Gather more wood to craft a Wooden Pickaxe."
                        else:
                            self.current_subgoal = "Out of wood. Find another tree to chop for wood."
                        return
                    else:
                        # We have wood and a table ready -> craft wooden pickaxe.
                        self.current_subgoal = "Craft a Wooden Pickaxe at the crafting table."
                        return
            else:
                # We have a Wooden Pickaxe already (but not a stone pickaxe yet).
                # Next subgoal: craft a Stone Pickaxe.
                if not self.has_stone_pickaxe:
                    # Ensure resources for stone pick: need wood + stone.
                    # Check wood: (we may have used one wood to craft the wooden pickaxe, ensure another wood for stone pick).
                    if wood < 1:
                        if 'tree' in visible_resources:
                            self.current_subgoal = "Need wood for Stone Pickaxe. Chop another tree."
                        else:
                            self.current_subgoal = "Need wood for Stone Pickaxe. Search for a tree."
                        return
                    # Check stone:
                    if stone < 1:
                        # No stone yet, need to mine stone.
                        # Wooden pickaxe is available, so we can mine stone nodes.
                        if 'stone' in visible_resources:
                            self.current_subgoal = "Mine some stone with your Wooden Pickaxe."
                        else:
                            self.current_subgoal = "No stone available here. Explore to find rocks or a cave for stone."
                        return
                    # If we have at least 1 stone and 1 wood, ensure table is placed:
                    if not self.table_placed:
                        # (Unlikely if we got wood pick, table was placed, but just in case)
                        self.current_subgoal = "Place a crafting table to use for crafting (stone pickaxe)."
                        return
                    # Now all requirements met:
                    self.current_subgoal = "Craft a Stone Pickaxe at the crafting table."
                    return
        # If we reach here, we have a Stone Pickaxe (or better).
        # Next: craft Iron Pickaxe.
        if not self.has_iron_pickaxe:
            # Iron Pickaxe requirements: wood, iron, coal, table, furnace.
            # Ensure we have placed a furnace:
            if not self.furnace_placed:
                # Need to place furnace (requires at least 1 stone in inventory).
                if stone < 1:
                    # If no stone left (maybe used for stone tools), gather stone.
                    if 'stone' in visible_resources:
                        self.current_subgoal = "No furnace yet. Mine stone to build a furnace."
                    else:
                        self.current_subgoal = "No furnace yet. Explore for more stone to place a furnace."
                    return
                else:
                    self.current_subgoal = "Place a furnace using stone (near the crafting table)."
                    return
            # Furnace is available now (placed).
            # Ensure we have needed resources for iron pickaxe: wood, iron, coal.
            if wood < 1:
                if 'tree' in visible_resources:
                    self.current_subgoal = "Out of wood. Chop a tree to get wood for the Iron Pickaxe."
                else:
                    self.current_subgoal = "Out of wood. Search for a tree to get wood (for Iron Pickaxe)."
                return
            if coal < 1:
                if 'coal' in visible_resources:
                    self.current_subgoal = "Mine coal ore to collect coal for smelting iron."
                else:
                    self.current_subgoal = "No coal yet. Explore caves or mountains to find coal."
                return
            if iron < 1:
                if 'iron' in visible_resources:
                    self.current_subgoal = "Mine iron ore to collect iron."
                else:
                    self.current_subgoal = "No iron yet. Delve into caves/mountains to find iron ore."
                return
            # If all resources are in inventory and furnace+table are ready, craft the Iron Pickaxe:
            self.current_subgoal = "Craft an Iron Pickaxe at the table (with the furnace available)."
            return
        
        # If somehow none of the above triggered, just default to main objective.
        self.current_subgoal = "Explore and survive until you can achieve the main goal (diamond)."
    
    def get_current_subgoal(self) -> str:
        """
        Return a description of the current priority subgoal for the agent.
        """
        return self.current_subgoal
