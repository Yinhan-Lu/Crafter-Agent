import sys
sys.path.append('./')
from __init__ import *
from descriptor import SimplifiedStateDescriptor

class Discover:
    def __init__(self, trajectory_dir='./dynamics/action/segmented_trajectory', 
                 save_dir='./dynamics/action/dynamics/discovered'):
        self._actions = ['collect_coal', 'collect_diamond', 'collect_drink', 'collect_iron', 'collect_sapling', 'collect_stone', 'collect_wood', 'defeat_skeleton', 
                         'defeat_zombie', 'eat_cow', 'eat_plant', 'make_iron_pickaxe', 'make_iron_sword', 'make_stone_pickaxe', 'make_stone_sword', 'make_wood_pickaxe', 
                         'make_wood_sword', 'place_furnace', 'place_plant', 'place_stone', 'place_table', 'sleep']
        self._load_trajectory(trajectory_dir)
        self._describe()
        self._save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
                
    
    def _load_trajectory(self, trajectory_dir):
        self.loaded_trajectory = dict()
        for trajectory_name in os.listdir(trajectory_dir):
            with open(os.path.join(trajectory_dir, trajectory_name)) as f:
                trajectory = json.load(f)
                self.loaded_trajectory[trajectory_name[:-5]] = trajectory

    
    def _describe(self):
        self._description = dict()
        for action in self.loaded_trajectory:
            self._description[action] = []
            for trajectory_name in self.loaded_trajectory[action]:
                trajectory = self.loaded_trajectory[action][trajectory_name]
                for traj_i in range(len(trajectory)):
                    previous_state_description = trajectory[traj_i]['previous_description']
                    state_description = trajectory[traj_i]['current_description']
                    # transition_description = f"""In state transition #{len(self._description[action])}, when action {action} is taken, the observation shifts {previous_state_description} **to** {state_description}\n"""
                    transition_description = f"""In transition #{len(self._description[action])}, observation before {action} is taken: {previous_state_description}. \n"""
                    self._description[action].append(transition_description)
    

    # def discover(self, maxim_indices=3, maxim_length=15):
    #         for action in self._description:
    #             prefix_prompt = "You are a helpful assistant, tasked with identifying all the possible pre-conditions for the action '{}'. Please respond in JSON format.".format(action)
    #             discover_format = """
    #             "precondition_0": {
    #                 "precondition_about_facing_object": facing_object,
    #                 "precondition_about_inventory_materials": {"object_name": quantity, ...},
    #                 "precondition_about_inventory_tool": tool_name,
    #                 "precondition_about_immediate_objects": [object_name, ...]
    #                 "other_preconditions": "......"
    #             }, 
    #             ......
    #             """
    #             description = self._description[action]
    #             dynamics = dict()
    #             save_path = os.path.join(self._save_dir, f'{action}.json')
    #             if os.path.exists(save_path):
    #                 continue

    #             for _ in range(maxim_length):
    #                 if len(description) < maxim_indices:
    #                     sampled_descriptions = description
    #                 else:
    #                     sampled_descriptions = random.sample(description, maxim_indices)
                    
    #                 partial_description = ' '.join(sampled_descriptions)
    #                 print(partial_description)
    #                 print('=======================')
    #                 prompt = f"""
    #                             In the Crafter environment, the world dynamics are similar to Minecraft but with differences. You are tasked with discovering the unique dynamics of actions within this environment.
    #                             Given the state transitions described as follows: {partial_description}, identify all possible and specific pre-conditions required for executing this action.

    #                             To discover the pre-conditions, consider the following aspects:
    #                             - The object that the agent must be facing to take the action, which can be a block or an entity or None.
    #                             - The materials in the inventory that are required to execute the action and their quantities, which can only be sapling, wood, stone, coal, iron, diamond.
    #                             - The most advanced tool required from the inventory to execute the action can be one of the following: wood pickaxe, stone pickaxe, iron pickaxe, wood sword, stone sword, or iron sword. The tools are ranked in the order of effectiveness as follows: wood < stone < iron.
    #                             - The objects within immediate distance that are required to execute the action, which can be any object in the environment.
                                
    #                             If no pre-condition is required, simply output as "None".
    #                             Output as many pre-conditions as you can think of in the following format: {discover_format}
    #                             """
    #                 action_dynamics = gpt_json(prefix_prompt, prompt)
    #                 action_dynamics = json.loads(action_dynamics)
    #                 print(action_dynamics)
    #                 dynamics[len(dynamics)] = action_dynamics
                
    #                 with open(save_path, 'w') as f:
    #                     json.dump(dynamics, f, indent=4)
                        

    def discover_inventory_materials_used(self, maxim_indices=5, maxim_length=10):
            self._save_path = os.path.join(self._save_dir, 'inventory_materials_used')
            if not os.path.exists(self._save_path):
                os.makedirs(self._save_path)
            for action in reversed(self._description):
                prefix_prompt = f"You are a helpful assistant, tasked with identifying the inventory materials used for the action '{action}'. Please respond in JSON format.".format(action)
                output_format = """{"inventory_materials_used": {transition_1: {inventory_materials_used}, transition_2: {inventory_materials_used}, ......}, "all_common_materials_used": {inventory_materials_used}} """

                description = self._description[action]
                dynamics = dict()
                save_path = os.path.join(self._save_path, f'{action}.json')
                if os.path.exists(save_path):
                    continue

                for _ in range(maxim_length):
                    if len(description) < maxim_indices:
                        sampled_descriptions = description
                    else:
                        sampled_descriptions = random.sample(description, maxim_indices)
                    
                    partial_description = ' '.join(sampled_descriptions)
                    print('=======================')
                    prompt = f"""
                    In the Crafter environment, the world dynamics are unique. You are tasked with discovering the unique dynamics of actions within this environment.
                    Given the state transitions described as follows: {partial_description}, identify the materials used in the inventory for executing this action.

                    To discover the materials used in the inventory, consider the following aspects:
                    - List all the materials used not gained for each state transition and their corresponding quantities; materials are: wood, stone, coal, iron, diamond, sapling.
                    - List all the common materials used in all state transitions and their corresponding quantities.
                    
                    If no materials are used in common, simply output as "None".
                    Output as many pre-conditions as you can think of in the following format: {output_format}
                    """
                    action_dynamics = gpt_json(prefix_prompt, prompt)
                    action_dynamics = json.loads(action_dynamics)
                    print(action_dynamics)
                    dynamics[len(dynamics)] = action_dynamics
                
                    with open(save_path, 'w') as f:
                        json.dump(dynamics, f, indent=4)


    def discover_immediate_objects(self, maxim_indices=5, maxim_length=10):
            self._save_path = os.path.join(self._save_dir, 'immediate_objects')
            if not os.path.exists(self._save_path):
                os.makedirs(self._save_path)
            for action in self._description:
                print(action)
                prefix_prompt = f"You are a helpful assistant, tasked with identifying the objects within immediate distance required for the action '{action}'. Please respond in JSON format.".format(action)
                output_format = """{"immediate_objects": {transition_1: {all_the_immediate_objects}, transition_2: {all_the_immediate_objects}, ......}, "common_immediate_objects": {all_the_immediate_objects}}"""


                description = self._description[action]
                dynamics = dict()
                save_path = os.path.join(self._save_path, f'{action}.json')
                if os.path.exists(save_path):
                    continue

                for _ in range(maxim_length):
                    if len(description) < maxim_indices:
                        sampled_descriptions = description
                    else:
                        sampled_descriptions = random.sample(description, maxim_indices)
                    
                    partial_description = ' '.join(sampled_descriptions)
                    print('=======================')
                    prompt = f"""
                    In the Crafter environment, the world dynamics are unique. You are tasked with discovering the unique dynamics of actions within this environment.
                    Given the state transitions described as follows: {partial_description}, identify the objects within immediate distance required for executing this action.
                    Object list: [coal, cow, diamond, furnace, iron, lava, skeleton, stone, table, tree, water, zombie, plant]

                    To discover the objects within immediate distance, consider the following aspects:
                    - List all the objects within immediate distance for each state transition before executing the action, which you can only choose from the object list.
                    - Identify and list the objects that are present in all state transitions within the immediate distance before executing the action, which you can only choose from the object list.
                    - The common object **must** be present in all state transitions' immediate objects.
                    
                    If no objects within immediate distance are in common, simply output as "None".
                    Output as many pre-conditions as you can think of in the following format: {output_format}
                    """
                    action_dynamics = gpt_json(prefix_prompt, prompt)
                    action_dynamics = json.loads(action_dynamics)
                    print(action_dynamics)

                    dynamics[len(dynamics)] = action_dynamics
                
                    with open(save_path, 'w') as f:
                        json.dump(dynamics, f, indent=4)


    def discover_facing_object(self, maxim_indices=5, maxim_length=10):
        self._save_path = os.path.join(self._save_dir, 'facing_object')
        if not os.path.exists(self._save_path):
            os.makedirs(self._save_path)
        for action in self._description:
            prefix_prompt = "You are a helpful assistant tasked with discover the facing object pre-conditions for the action '{}'. Please respond in JSON format.".format(action)
            output_format = """{"facing_object_before_action": {transition_1: {facing_object_before_action}, transition_2: {facing_object_before_action}, ......}, "all_facing_object_before_action": {facing_object_before_action}}"""


            description = self._description[action]
            dynamics = dict()
            save_path = os.path.join(self._save_path, f'{action}.json')
            if os.path.exists(save_path):
                continue

            for _ in range(maxim_length):
                if len(description) < maxim_indices:
                    sampled_descriptions = description
                else:
                    sampled_descriptions = random.sample(description, maxim_indices)
                
                partial_description = ' '.join(sampled_descriptions)

                print(partial_description)

                prompt = f"""
                In the Crafter environment, the world dynamics are unique. You are tasked with discovering the unique dynamics of actions within this environment.
                Given the state transitions described as follows: {partial_description}, identify the facing object required for executing this action.

                To discover the objects within immediate distance, consider the following aspects:
                - List the facing object for each state transition before this action executed, not the direction.
                - List the union of all the facing object across all the state transitions before this action executed.
                - The union of all the facing object must be present in at least one state transitions' facing object.
                
                Output as many pre-conditions as you can think of in the following format: {output_format}
                """
                action_dynamics = gpt_json(prefix_prompt, prompt)
                action_dynamics = json.loads(action_dynamics)
                
                dynamics[len(dynamics)] = action_dynamics
            
                with open(save_path, 'w') as f:
                    json.dump(dynamics, f, indent=4)


    def discover_inventory_tool(self, maxim_indices=5, maxim_length=10):
        self._save_path = os.path.join(self._save_dir, 'inventory_tool')
        if not os.path.exists(self._save_path):
            os.makedirs(self._save_path)
        for action in self._description:
            prefix_prompt = "You are a helpful assistant tasked with discover the the inventory tool pre-conditions for the action '{}'. Please respond in JSON format.".format(action)
            output_format = """{"inventory_tools": {transition_1: {all_tools}, transition_2: {all_tools}, ......}, "common_inventory_tools": {common_tools}, "most_advanced_common_inventory_tools: {tool}"  """

            description = self._description[action]
            dynamics = dict()
            save_path = os.path.join(self._save_path, f'{action}.json')
            if os.path.exists(save_path):
                continue

            for _ in range(maxim_length):
                if len(description) < maxim_indices:
                    sampled_descriptions = description
                else:
                    sampled_descriptions = random.sample(description, maxim_indices)
                
                partial_description = ' '.join(sampled_descriptions)

                prompt = f"""
                In the Crafter environment, the world dynamics are unique. You are tasked with discovering the unique dynamics of actions within this environment.
                Given the state transitions described as follows: {partial_description}, identify the the inventory tool required for executing this action.
                Tool list: [None, wood pickaxe, stone pickaxe, iron pickaxe, wood sword, stone sword, iron sword].

                To discover the objects within immediate distance, consider the following aspects:
                - List all the tools in the inventory for each state transition.
                - List the tools that are common across all the state transitions.
                - The common tools must be present in all state transitions' tools; if no tools are required, simply output as "None".
                - List the most advanced tool required for executing the action within the common tools.
                
                Output as many pre-conditions as you can think of in the following format: {output_format}
                """
                action_dynamics = gpt_json(prefix_prompt, prompt)
                action_dynamics = json.loads(action_dynamics)
                
                dynamics[len(dynamics)] = action_dynamics
            
                with open(save_path, 'w') as f:
                    json.dump(dynamics, f, indent=4)


    def discover_outcome(self, maxim_indices=5, maxim_length=10):
        self._save_path = os.path.join(self._save_dir, 'inventory_outcome')
        if not os.path.exists(self._save_path):
            os.makedirs(self._save_path)
        for action in self._description:
            prefix_prompt = "You are a helpful assistant tasked with discover the the increase for the action '{}' in terms of the inventory and status. Please respond in JSON format.".format(action)
            output_format = """{"increase": {transition_1: {inventory_increase:..., status_increase:...}, transition_2: {inventory_increase:..., status_increase:...}, ......}, "common_increase": {inventory_increase:..., status_increase:...} """

            description = self._description[action]
            dynamics = dict()
            save_path = os.path.join(self._save_path, f'{action}.json')
            if os.path.exists(save_path):
                continue

            for _ in range(maxim_length):
                if len(description) < maxim_indices:
                    sampled_descriptions = description
                else:
                    sampled_descriptions = random.sample(description, maxim_indices)
                
                partial_description = ' '.join(sampled_descriptions)

                prompt = f"""
                In the Crafter environment, the world dynamics are unique. You are tasked with discovering the unique dynamics of actions within this environment.
                Given the state transitions described as follows: {partial_description}, identify the inventory and status increase after executing this action.
                inventory: [wood, stone, coal, iron, diamond, sapling, wood_pickaxe, stone_pickaxe, iron_pickaxe, wood_sword, stone_sword, iron_sword]
                status: [health, food, drink, energy], the maximum value of status is 9 and you can use 'increased_to_9' to represent the status increase to the maximum value.

                To discover the increase about the inventory and status, consider the following aspects:
                - List all the increase of the inventory and status for each state transition after executing the action.
                - List the increase of the inventory and status that are common across all the state transitions after executing the action.
                - The common increase must be present in all state transition's increase; if no inventory and status can be found, simply output as "None";
                
                Output as many pre-conditions as you can think of in the following format: {output_format}
                """
                action_dynamics = gpt_json(prefix_prompt, prompt)
                action_dynamics = json.loads(action_dynamics)
                
                dynamics[len(dynamics)] = action_dynamics
            
                with open(save_path, 'w') as f:
                    json.dump(dynamics, f, indent=4)


    def discover_facing_object_change(self, maxim_indices=5, maxim_length=10):
        self._save_path = os.path.join(self._save_dir, 'facing_object_change')
        if not os.path.exists(self._save_path):
            os.makedirs(self._save_path)
        for action in reversed(self._description):
            prefix_prompt = "You are a helpful assistant tasked with discover the facing object change for the action '{}'. Please respond in JSON format.".format(action)
            output_format = """{"facing_object_change": {transition_1: {from...to...}, transition_2: {from...to...}, ......}, "common_facing_object_change": {from...to...}}"""


            description = self._description[action]
            dynamics = dict()
            save_path = os.path.join(self._save_path, f'{action}.json')
            if os.path.exists(save_path):
                continue

            for _ in range(maxim_length):
                if len(description) < maxim_indices:
                    sampled_descriptions = description
                else:
                    sampled_descriptions = random.sample(description, maxim_indices)
                
                partial_description = ' '.join(sampled_descriptions)

                prompt = f"""
                In the Crafter environment, the world dynamics are unique. You are tasked with discovering the unique dynamics of actions within this environment.
                Given the state transitions described as follows: {partial_description}, identify the facing object changes for executing this action.

                To discover the change about the facing object, consider the following aspects:
                - List all the change about the facing object after executing the action for each state transition.
                - List the common change about the facing object across all the state transitions.
                - The common change must be present in all state transitions' facing object change; if no change can be found, simply output as "None".
                
                Output as many pre-conditions as you can think of in the following format: {output_format}
                """
                action_dynamics = gpt_json(prefix_prompt, prompt)
                action_dynamics = json.loads(action_dynamics)
                
                dynamics[len(dynamics)] = action_dynamics
            
                with open(save_path, 'w') as f:
                    json.dump(dynamics, f, indent=4)




if __name__ == '__main__':
    discover = Discover()
    discover.discover_facing_object()
