class GameRules:
    """
    Contains a reference description of the Crafter game, including objectives, 
    rules, actions, and mechanics. This text is used in prompts to remind the LLM 
    of the game environment and constraints.
    """
    RULES_TEXT: str = (
        "### Crafter Game Environment Rules and Objectives\n"
        "Crafter is a 2D open-world survival game on a 64x64 grid:contentReference[oaicite:30]{index=30}. Each game starts in a unique world with grasslands, lakes, and mountains that contain forests, caves, ores, and lava:contentReference[oaicite:31]{index=31}. "
        "Your overarching goal is to **survive** as long as possible and eventually **find and collect a diamond**, which is the most difficult achievement:contentReference[oaicite:32]{index=32}.\n\n"
        "**Survival**: You have Health, Hunger, Thirst, and Energy (fatigue). Keep yourself fed, hydrated, and rested, or you will start losing health. You can eat food (plants or cows) to restore hunger and drink water from lakes to quench thirst:contentReference[oaicite:33]{index=33}. "
        "Sleep when you are tired to restore energy:contentReference[oaicite:34]{index=34}. If you are not hungry, thirsty, or exhausted, your health will slowly regenerate:contentReference[oaicite:35]{index=35}. If any of Hunger, Thirst, or Energy runs out, your health will begin to drop. "
        "The game ends if your health reaches 0 (death) or after a certain time limit (10000 steps):contentReference[oaicite:36]{index=36}.\n\n"
        "**Hazards**: Beware of monsters and environmental dangers. Hostile creatures like zombies and skeletons roam the world:contentReference[oaicite:37]{index=37}, especially in dark areas or at night. They will attack you on sight, reducing your health. "
        "Avoid or defeat them to stay alive (using weapons makes fighting easier). Wild animals like cows are not hostile and can be hunted for food. "
        "Lava pools exist in some caves or mountains:contentReference[oaicite:38]{index=38} – falling into lava or touching it will severely hurt or kill you, so stay away from lava. Always be cautious at night or when exploring caves.\n\n"
        "**Resources**: The world contains various resources you can collect:\n"
        "- **Wood**: obtained by chopping trees (use the interact action on a tree). Wood is used for crafting tools and building a crafting table:contentReference[oaicite:39]{index=39}.\n"
        "- **Stone**: obtained by mining rocks. Stone is needed for better tools and for building a furnace:contentReference[oaicite:40]{index=40}.\n"
        "- **Coal**: obtained by mining coal ore (usually found in rocks or caves). Coal is used as a fuel/resource for crafting iron tools:contentReference[oaicite:41]{index=41}.\n"
        "- **Iron**: obtained by mining iron ore (found in mountains/caves). Iron (along with coal) is needed to craft the highest tier tools:contentReference[oaicite:42]{index=42}.\n"
        "- **Saplings**: sometimes obtained from chopping trees. You can plant saplings to grow new trees (providing a renewable source of wood or food).\n"
        "- **Food**: Plants (fruits) and animals (cows) provide food. Eating a plant or a cow immediately restores some hunger:contentReference[oaicite:43]{index=43} (and grants an achievement **eat_plant** or **eat_cow**:contentReference[oaicite:44]{index=44}). Cows must be killed (interact with a cow) to yield meat; plants or fruits can be directly consumed when found.\n"
        "- **Water**: Lakes are water sources. Interact with a water tile (lake) to drink:contentReference[oaicite:45]{index=45}, restoring thirst (achievement **collect_drink**:contentReference[oaicite:46]{index=46}).\n"
        "Some resources (stone, coal, iron, diamond) require the appropriate tool tier to collect. For example, you need a pickaxe to mine stone/ore, and only an Iron Pickaxe can mine diamond.\n\n"
        "**Crafting and Building**:\n"
        "You can craft tools and build certain structures using resources:\n"
        "- **Crafting Table**: Basic workstation crafted from wood. Place a table (action `place_table`) when you have wood:contentReference[oaicite:47]{index=47}. Crafting tools requires being adjacent to a table.\n"
        "- **Furnace**: Smelting facility crafted from stone. Place a furnace (action `place_furnace`) when you have stone:contentReference[oaicite:48]{index=48}. A furnace is required to craft iron tools.\n"
        "- **Tools**: You can craft pickaxes and swords of increasing quality:\n"
        "  - *Wooden Pickaxe* – Requires at least 1 wood and a nearby crafting table:contentReference[oaicite:49]{index=49}. Allows mining stone and coal. (Craft using action `make_wood_pickaxe`.)\n"
        "  - *Stone Pickaxe* – Requires 1 wood + 1 stone and a table:contentReference[oaicite:50]{index=50}. Allows mining iron ore. (Action `make_stone_pickaxe`.)\n"
        "  - *Iron Pickaxe* – **Requires** 1 wood + 1 iron + 1 coal, a table, **and** a furnace:contentReference[oaicite:51]{index=51}. Needed to mine diamond. (Action `make_iron_pickaxe`.)\n"
        "  - *Wooden Sword* – Requires 1 wood and a table:contentReference[oaicite:52]{index=52}. A basic weapon for defense. (Action `make_wood_sword`.)\n"
        "  - *Stone Sword* – Requires 1 wood + 1 stone and a table:contentReference[oaicite:53]{index=53}. Better weapon. (Action `make_stone_sword`.)\n"
        "  - *Iron Sword* – Requires 1 wood + 1 iron + 1 coal, a table, and a furnace:contentReference[oaicite:54]{index=54}. Strongest weapon. (Action `make_iron_sword`.)\n"
        "- **Building Blocks**: You can also place raw materials into the world: e.g. place stone blocks (`place_stone`) to build walls or barriers (this uses a stone from your inventory), or plant a sapling (`place_plant`) to grow a tree:contentReference[oaicite:55]{index=55}.\n"
        "Crafting or placing an item consumes the required resources from your inventory, so gather sufficient quantities.\n\n"
        "**Available Actions**:\n"
        "Each turn, you can perform one action. The actions you can take include:contentReference[oaicite:56]{index=56}:contentReference[oaicite:57]{index=57}:\n"
        "- **Move**: `move_up`, `move_down`, `move_left`, or `move_right` to move one tile in that direction (if the path is clear).\n"
        "- **Interact**: `do` – Use the item in front of you or attack what's in front of you. This is used to gather resources (chop wood, mine ores), pick up items, drink water, or attack enemies. You must be facing the target and have the correct tool if required (e.g. need a pickaxe equipped to mine, a sword to effectively fight monsters).\n"
        "- **Place**: `place_table`, `place_furnace`, `place_stone`, `place_plant` – Build/place a crafting table (uses wood), furnace (uses stone), stone block (uses stone), or plant a sapling (uses a sapling) respectively. These actions are only available when you have the required item in inventory.\n"
        "- **Craft**: `make_wood_pickaxe`, `make_stone_pickaxe`, `make_iron_pickaxe`, `make_wood_sword`, `make_stone_sword`, `make_iron_sword` – Craft a tool or weapon if you have the required resources and are next to a crafting table (and furnace for iron-tier). These actions instantly produce the item and consume the resources.\n"
        "- **Sleep**: `sleep` – Rest to recover energy when tired (only possible if your energy is not full). Sleeping skips some time (possibly to daytime) and heals you a bit if you were injured and not hungry/thirsty. After sleeping, you automatically wake up (`wake_up`). Use this to avoid dying of exhaustion and to regenerate health safely.\n"
        "- **Noop**: `noop` – Do nothing for a turn. (Use this if you have no other viable action or need to wait.)\n\n"
        "**Goal**: Survive as long as possible by managing your needs and dangers, and work towards mining a **diamond**. Achieve this by following the progression: gather basic resources, craft better tools, build necessary structures, fight or avoid monsters, and explore the world for rare resources. There are 22 milestones (achievements) you can accomplish:contentReference[oaicite:58]{index=58}:contentReference[oaicite:59]{index=59}, and finding the diamond is the final and most challenging one. Good luck!\n"
    )

env_description_prompt = """
        You are an agent in a procedurally generated 2D survival world called Crafter. Your goal is to explore, collect resources, 
        craft tools, place objects, fight monsters, and survive. Each episode, you face different challenges, and your task is to
        unlock as many achievements as possible by making the right decisions. Below are the detailed descriptions of the environment,
        your available actions, and the mechanics you need to know to succeed.
        """

actions_prompt = """
        
        # ### Actions:
        # - noop: Do nothing.
        # - move_left, move_right, move_up, move_down: Move in the respective direction.
        # - do: Interact with the object in front of you (e.g., collect resources, attack enemies).
        # - sleep: Rest to restore energy. Use when your energy is low.
        # - place_stone, place_table, place_furnace, place_plant: Place items in the environment.
        # - place_stone: Place a stone on walkable terrain (grass, sand, path, water, lava).
        # - place_table: Place a crafting table to craft tools.
        # - place_furnace: Place a furnace to smelt resources.
        # - place_plant: Place a sapling to grow trees.
        # - make_wood_pickaxe, make_stone_pickaxe, make_iron_pickaxe: Craft different levels of pickaxes.
        # - wood_pickaxe: Used for collecting basic resources like stone and coal.
        # - stone_pickaxe: Allows mining of harder materials like iron.
        # - iron_pickaxe: Necessary for mining diamonds.
        # - make_wood_sword, make_stone_sword, make_iron_sword: Craft different levels of swords for combat.

        # ### Materials:
        # - water: Found in lakes, used to drink and restore the thirst meter.
        # - grass: A common walkable surface that can yield saplings for planting.
        # - stone: Used for crafting and placing objects like furnaces.
        # - path: A walkable surface left behind after mining certain materials.
        # - sand: A walkable surface found in certain biomes.
        # - tree: Chop down to collect wood, essential for crafting.
        # - lava: Dangerous, causes damage if walked on.
        # - coal: A material used for crafting advanced items, mined with a pickaxe.
        # - iron: Required for crafting advanced tools like iron pickaxes and swords.
        # - diamond: The rarest material, used for the strongest tools, mined with an iron pickaxe.
        # - table: A crafting table, placed to craft tools.
        # - furnace: Used for smelting iron and crafting advanced items.

        # ### Walkable Surfaces:
        # - grass, path, sand: These surfaces can be walked on safely.

        # ### Items:
        # - health (max: 9): Your health points. If they reach zero, you die. 
        # - food (max: 9): Eat cows or plants to restore food.
        # - drink (max: 9): Drink water to restore thirst.
        # - energy (max: 9): Sleep to restore energy.
        # - sapling, wood, stone, coal, iron, diamond: Collect these resources for crafting and building.
        # - wood_pickaxe, stone_pickaxe, iron_pickaxe: Tools for mining.
        # - wood_sword, stone_sword, iron_sword: Weapons for combat.

        # ### Collecting Resources:
        # - tree: No tool required, provides wood. 
        # - stone: Requires wood_pickaxe, provides stone.
        # - coal: Requires wood_pickaxe, provides coal.
        # - iron: Requires stone_pickaxe, provides iron.
        # - diamond: Requires iron_pickaxe, provides diamonds.
        # - water: Collect from lakes to restore drink.
        # - grass: Occasionally yields saplings for planting.

        # ### Crafting Items:
        # - wood_pickaxe: Requires wood and a nearby crafting table.
        # - stone_pickaxe: Requires wood, stone, and a nearby crafting table.
        # - iron_pickaxe: Requires wood, coal, iron, and both a table and furnace.
        # - wood_sword: Requires wood and a nearby crafting table.
        # - stone_sword: Requires wood, stone, and a nearby crafting table.
        # - iron_sword: Requires wood, coal, iron, and both a table and furnace.

        # ### Placing Objects:
        # - stone: Place on grass, sand, path, water, or lava.
        # - table: Place on grass, sand, or path.
        # - furnace: Place on grass, sand, or path.
        # - plant: Place saplings on grass to grow trees.

        # ### Achievements:
        # Unlock achievements by completing tasks:
        # - collect_coal: Collect coal by mining with a wood_pickaxe.
        # - collect_diamond: Collect diamond with an iron_pickaxe.
        # - collect_drink: Drink water from a lake.
        # - collect_iron: Collect iron with a stone_pickaxe.
        # - collect_sapling: Collect saplings from grass.
        # - collect_stone: Collect stone with a wood_pickaxe.
        # - collect_wood: Collect wood from trees.
        # - defeat_skeleton: Defeat a skeleton in combat.
        # - defeat_zombie: Defeat a zombie in combat.
        # - eat_cow: Eat meat from a cow.
        # - eat_plant: Eat a plant.
        # - make_iron_pickaxe: Craft an iron_pickaxe.
        # - make_iron_sword: Craft an iron_sword.
        # - make_stone_pickaxe: Craft a stone_pickaxe.
        # - make_stone_sword: Craft a stone_sword.
        # - make_wood_pickaxe: Craft a wood_pickaxe.
        # - make_wood_sword: Craft a wood_sword.
        # - place_furnace: Place a furnace.
        # - place_plant: Plant a sapling.
        # - place_stone: Place a stone.
        # - place_table: Place a crafting table.
        # - wake_up: Wake up after sleeping.

        # Use the available actions, manage your resources effectively, and survive as long as possible. Unlock as many achievements as you can by making strategic decisions based on the environment and your current state.
        # """



def reasoning_way_prompt_creator(action_space):
    reasoning_way_prompt = f"""
            You are an AI agent that uses the ReAct (Reasoning + Acting). Your task is to observe the current situation, reason about the next best action, and then act based on your reasoning. You will alternate between reasoning and acting to achieve your goals. 
    
        For each step, follow these guidelines:
        1. **Reasoning**: Analyze the current environment and explain your reasoning step by step. Consider the current state and any available information to deduce the best possible action.
        2. **Action**: After reasoning, provide a specific action based on your analysis. The action should be either:
            2.1. one exact word in the list: {action_space}  that reflects your next move.
            2.2. or you can do "read document". In this case, you would read document module in which you can select a chapter from a documentation book to read, and then do the action. 
        3. **Environment Feedback**: After taking an action, observe the environment's feedback and incorporate it into your next reasoning step.
        4. **Iterate**: Repeat this process by alternating between reasoning and acting until the problem is solved.
    
        ### Example:
        #### Step 1:
        - **Observation**: The player is standing near a forest of trees. There is no wood in the player's inventory, 
        but they need wood to craft basic tools.
        - **Reasoning**: Wood is essential for crafting basic tools such as pickaxes. The trees nearby are a good 
        source of wood.
        - **Action**: do

        #### Step 2:
        - **Observation**: The player has collected wood from the trees and now stands near a crafting table.
        - **Reasoning**: The collected wood can now be used to craft a wood pickaxe at the crafting table, which will 
        enable the collection of stone for advanced tools.
        - **Action**: make_wood_pickaxe
        """
    return reasoning_way_prompt

def language_wrapper_description_prompt_creator(lan_wrapper):
        language_wrapper_prompt = f"""
             environment uses a specialized language wrapper to communicate the game state. Here are the key rules for understanding the observations:
                1. Distance Rules
                Objects are described using distance buckets relative to your position:

                "adjacent" for items 1 tile away
                "very near" for items up to 3 tiles away
                "near" for items up to 5 tiles away
                "far" for items up to 20 tiles away
                "very far" for items beyond 20 tiles

                2. Direction Rules
                Directions are specified using cardinal and intercardinal points:

                Cardinal: north, south, east, west
                Intercardinal: northeast, northwest, southeast, southwest
                Intermediate directions like "northnortheast" for positions between cardinal and intercardinal points

                3. Observation Format

                Each object is described as: "[object name] [distance] [direction]"
                Multiple objects in the same distance/direction are grouped together
                When multiples of the same object exist, they are pluralized
                Observations are joined with semicolons
                Objects are listed by distance (closest to farthest)

                the language description of the local view are:{lan_wrapper}\n"""
        return language_wrapper_prompt
format_prompt="""
        Please return the following data in valid JSON format.
        The JSON should have the keys "observation","reasoning" and "action".  This JSON-like string you generate must be able to convert to json format by json.loads() function Here's an example of the expected format:
    
    {
      "observation": "The player moved forward and now stands in the open field. There are mountains visible in the distance.",
      "reasoning": "The open field is clear and provides visibility of distant landmarks. Heading toward the mountains may reveal new resources or opportunities.",
      "action": "place_plant"
    }.
        """