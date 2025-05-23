import sys
sys.path.append('./')
from utils import *
from __init__ import *
from descriptor import SimplifiedStateDescriptor

class Verify:
    def __init__(self, discover_dir='./Dynamics/action/dynamics/discovered', trajectory_dir='./dynamics/action/segmented_trajectory',
                 save_dir='Dynamics/action/dynamics/verified'):
        # self._actions = ['collect_coal', 'collect_diamond', 'collect_drink', 'collect_iron', 'collect_sapling', 'collect_stone', 'collect_wood', 'defeat_skeleton', 
        #                  'defeat_zombie', 'eat_cow', 'eat_plant', 'make_iron_pickaxe', 'make_iron_sword', 'make_stone_pickaxe', 'make_stone_sword', 'make_wood_pickaxe', 
        #                  'make_wood_sword', 'place_furnace', 'place_plant', 'place_stone', 'place_table', 'sleep']
        self._actions = ['sleep']
        self._load_discovered_dynamics(discover_dir)
        self._load_trajectory(trajectory_dir)
        self._verified_dynamics = list()
        self._save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self._load_trajectory(trajectory_dir)
        self._describe()
    

    def _load_trajectory(self, trajectory_dir):
        self.loaded_trajectory = dict()
        for trajectory_name in os.listdir(trajectory_dir):
            with open(os.path.join(trajectory_dir, trajectory_name)) as f:
                trajectory = json.load(f)
                self.loaded_trajectory[trajectory_name[:-5]] = trajectory


    def _load_discovered_dynamics(self, discover_dir):
        self.immediate_objects_dynamics = dict()
        for action_name in os.listdir(os.path.join(discover_dir, 'immediate_objects')):
            with open(os.path.join(os.path.join(discover_dir, 'immediate_objects'), action_name)) as f:
                discovered_dynamics = json.load(f)
                # remove the suffix .json
                print(action_name)
                self.immediate_objects_dynamics[action_name[:-5]] = discovered_dynamics

        self.inventory_materials_used_dynamics = dict()
        for action_name in os.listdir(os.path.join(discover_dir, 'inventory_materials_used')):
            with open(os.path.join(os.path.join(discover_dir, 'inventory_materials_used'), action_name)) as f:
                discovered_dynamics = json.load(f)
                # remove the suffix .json
                print(action_name)
                self.inventory_materials_used_dynamics[action_name[:-5]] = discovered_dynamics

        self.inventory_tool_dynamics = dict()
        for action_name in os.listdir(os.path.join(discover_dir, 'inventory_tool')):
            with open(os.path.join(os.path.join(discover_dir, 'inventory_tool'), action_name)) as f:
                discovered_dynamics = json.load(f)
                # remove the suffix .json
                print(action_name)
                self.inventory_tool_dynamics[action_name[:-5]] = discovered_dynamics

        self.facing_object_dynamics = dict()
        for action_name in os.listdir(os.path.join(discover_dir, 'facing_object')):
            with open(os.path.join(os.path.join(discover_dir, 'facing_object'), action_name)) as f:
                discovered_dynamics = json.load(f)
                # remove the suffix .json
                print(action_name)
                self.facing_object_dynamics[action_name[:-5]] = discovered_dynamics
        
        ################## outcome ##################
        
        self.inventory_outcome_dynamics = dict()
        for action_name in os.listdir(os.path.join(discover_dir, 'inventory_outcome')):
            with open(os.path.join(os.path.join(discover_dir, 'inventory_outcome'), action_name)) as f:
                discovered_dynamics = json.load(f)
                # remove the suffix .json
                print(action_name)
                self.inventory_outcome_dynamics[action_name[:-5]] = discovered_dynamics

        self.facing_object_change_dynamics = dict()
        for action_name in os.listdir(os.path.join(discover_dir, 'facing_object_change')):
            with open(os.path.join(os.path.join(discover_dir, 'facing_object_change'), action_name)) as f:
                discovered_dynamics = json.load(f)
                # remove the suffix .json
                print(action_name)
                self.facing_object_change_dynamics[action_name[:-5]] = discovered_dynamics
    

    def _describe(self):
        self._description = dict()
        for action in self.loaded_trajectory:
            self._description[action] = []
            for trajectory_name in self.loaded_trajectory[action]:
                trajectory = self.loaded_trajectory[action][trajectory_name]
                for traj_i in range(len(trajectory)):
                    previous_state_description = trajectory[traj_i]['previous_description']
                    state_description = trajectory[traj_i]['current_description']
                    transition_description = f"""In state transition #{len(self._description[action])}, when action {action} is taken, the observation shifts {previous_state_description} **to** {state_description}\n"""
                    self._description[action].append(transition_description)
    

    def _verify_dynamics_inventory_tool_precondition(self, maxim_indices=5):
        self._tool_precondition_dir = os.path.join(self._save_dir, 'inventory_tool_precondition')
        if not os.path.exists(self._tool_precondition_dir):
            os.makedirs(self._tool_precondition_dir)

        for action in list(self.inventory_tool_dynamics.keys()):
            verified_dynamics = dict()
            if os.path.exists(os.path.join(self._save_dir, 'inventory_tool_precondition',f'{action}.json')):
                continue
            print(action)
            index = 0
            action_dynamics = self.inventory_tool_dynamics[action]
            action_description = self._description[action]
            for _, dynamics in action_dynamics.items():
                try:
                    preconditions = dynamics['most_advanced_common_inventory_tool']
                except:
                    continue
                print('==========================================')
                if maxim_indices > len(action_description):
                    maxim_indices = len(action_description)
                sampled_descriptions = random.sample(action_description, maxim_indices)

                output_format = """{"inventory_tools": {transition_1: {all_the_tools}, transition_2: {all_the_tools}, ......}, "common_inventory_tools": {all_the_tools}, "valid": valid/invalid}"""
                prefix_prompt = "You are a helpful assistant tasked with verifying the inventory tool pre-conditions for the action '{}'. Please respond in JSON format.".format(action)
                prompt = f"""
                In the crafter environment, you have discovered unique dynamics and need to verify the pre-conditions for the action '{action}'.
                Given the state transitions before and after taking the action '{action}', described as follows: {sampled_descriptions} 

                You are asked to verify the inventory pre-conditions for the action '{action}' based on the discovered dynamics.

                Precondition: You only need {preconditions} to execute the action.

                For the verification, you need to consider the followings:
                 List all the tools in the inventory for each state transition.
                - List the tools that are common across all the state transitions.
                - The common tools must be present in all state transitions' tools; if no tools are required, simply output as "None".
                - If the tools mentioned in the pre-condition are within the common tools, then it is valid; otherwise, it is invalid.

                Output in this format: {output_format}
                """
                precondition_verification = gpt_json(prefix_prompt, prompt)
                precondition_verification = json.loads(precondition_verification)
                print(action)
                print(dynamics['most_advanced_common_inventory_tool'])
                print(precondition_verification)
                print('==========================================')
                try:
                    if str(precondition_verification['valid']).lower() == 'valid':
                        verified_dynamics[index] = dynamics["most_advanced_common_inventory_tool"]
                    index += 1
                    with open(os.path.join(self._tool_precondition_dir, f'{action}.json'), 'w') as f:
                        json.dump(verified_dynamics, f, indent=4)
                except:
                    pass
            

    def _verify_dynamics_immediate_objects_precondition(self, maxim_indices=10):
        self._immediate_objects_dir = os.path.join(self._save_dir, 'immediate_objects_precondition')
        if not os.path.exists(self._immediate_objects_dir):
            os.makedirs(self._immediate_objects_dir)
        for action in reversed(list(self.immediate_objects_dynamics.keys())):
            verified_dynamics = dict()
            if os.path.exists(os.path.join(self._save_dir, 'immediate_objects_precondition',f'{action}.json')):
                continue
            index = 0
            action_dynamics = self.immediate_objects_dynamics[action]
            action_description = self._description[action]
            for _, dynamics in action_dynamics.items():
                print(dynamics)
                print('==========================================')

                if maxim_indices > len(action_description):
                    maxim_indices = len(action_description)
                sampled_descriptions = random.sample(action_description, maxim_indices)

                try:
                    precondition = dynamics['common_immediate_objects']
                except:
                    continue

                output_format = """{"immediate_objects": {transition_1: {all_the_immediate_objects}, transition_2: {all_the_immediate_objects}, ......}, "common_immediate_objects": {all_the_immediate_objects}, "not_in_common_immediate_objects": "objects_name", "valid": valid/invalid}"""
                prefix_prompt = "You are a helpful assistant tasked with verifying the objects withinin immediate distance pre-conditions for the action '{}'. Please respond in JSON format.".format(action)
                prompt = f"""
                In the crafter environment, you have discovered unique dynamics and need to verify the pre-conditions for the action '{action}'.
                Given the state transitions before and after taking the action '{action}', described as follows: {sampled_descriptions} 

                You are asked to verify the immediate objects pre-conditions for the action '{action}' based on the discovered dynamics.
                
                Precondition: You only need {precondition} within immediate distance.
                Object list: [coal, cow, diamond, furnace, iron, lava, skeleton, stone, table, tree, water, zombie, plant]

                For the verification, you need to consider the followings:
                - List all the objects within immediate distance before executing the action for each state transition only from the object list.
                - Identify and list the objects that are present in all state transitions within the immediate distance before executing the action as common immediate objects, only from the object list.
                - The common object **must** be present in all state transitions' immediate objects.
                - Determine if there are objects mentioned in the pre-condition that are not in the common immediate objects.
                - If there are objects mentioned in the pre-condition that are not in the common immediate objects, then it is invalid; otherwise, it is valid.
                Output in this format: {output_format}
                """
                precondition_verification = gpt_json(prefix_prompt, prompt)
                precondition_verification = json.loads(precondition_verification)
                print(action)
                print(dynamics['common_immediate_objects'])
                print(precondition_verification)
                print('==========================================')
                try:
                    if str(precondition_verification['valid']).lower() == 'valid':
                        verified_dynamics[index] = dynamics["common_immediate_objects"]
                    index += 1
                    with open(os.path.join(self._immediate_objects_dir, f'{action}.json'), 'w') as f:
                        json.dump(verified_dynamics, f, indent=4)
                except:
                    pass


    def _verify_dynamics_facing_objects_precondition(self, maxim_indices=5):
        self._facing_object_dir = os.path.join(self._save_dir, 'facing_object_precondition')
        if not os.path.exists(self._facing_object_dir):
            os.makedirs(self._facing_object_dir)
        for action in list(self.facing_object_dynamics.keys()):
            verified_dynamics = dict()
            if os.path.exists(os.path.join(self._save_dir, 'facing_object_precondition',f'{action}.json')):
                continue
            index = 0
            action_dynamics = self.facing_object_dynamics[action]
            action_description = self._description[action]
            for _, dynamics in reversed(action_dynamics.items()):
                print(dynamics)
                print('==========================================')

                try:
                    precondition = dynamics['all_facing_object_before_action']
                except:
                    continue
                if maxim_indices > len(action_description):
                    maxim_indices = len(action_description)
                sampled_descriptions = random.sample(action_description, maxim_indices)

                output_format = """{"facing_object_before_action": {transition_1: {facing_object_before_action}, transition_2: {facing_object_before_action}, ......}, "all_facing_object_before_action": {facing_object_before_action}, "within_all_facing_object_before_action": "yes/no", "valid": valid/invalid}"""
                prefix_prompt = "You are a helpful assistant tasked with verifying the facing object pre-conditions for the action '{}'. Please respond in JSON format.".format(action)
                prompt = f"""
                In the crafter environment, you have discovered unique dynamics and need to verify the pre-conditions for the action '{action}'.
                Given the state transitions before and after taking the action '{action}', described as follows: {sampled_descriptions} 

                You are asked to verify the facing object pre-conditions for the action '{action}' based on the discovered dynamics.

                Precondition: You need to face {precondition} before execute the action.

                For the verification, you need to consider the followings:
                - List the facing object for each state transition before this action executed.
                - List the union of all the facing object across all the state transitions before this action executed.
                - Determine if the facing object mentioned in the pre-condition is within the union of all the facing object.
                - If the facing object mentioned in the pre-condition is within the union of all the facing objects, then it is valid; otherwise, it is invalid.

                Finally, if there are more advanced tools exist, then it is invalid; otherwise, it is valid.
                Output in this format: {output_format}
                """
                precondition_verification = gpt_json(prefix_prompt, prompt)
                precondition_verification = json.loads(precondition_verification)
                print(action)
                print(dynamics['all_facing_object_before_action'])
                print(precondition_verification)
                print('==========================================')
                try:
                    if str(precondition_verification['valid']).lower() == 'valid':
                        verified_dynamics[index] = dynamics["all_facing_object_before_action"]
                    index += 1
                    with open(os.path.join(self._facing_object_dir, f'{action}.json'), 'w') as f:
                        json.dump(verified_dynamics, f, indent=4)
                except:
                    pass


    def _verify_dynamics_inventory_materials_used_precondition(self, maxim_indices=5):
        self._inventory_materials_used_dir = os.path.join(self._save_dir, 'inventory_materials_precondition')
        if not os.path.exists(self._inventory_materials_used_dir):
            os.makedirs(self._inventory_materials_used_dir)
        for action in reversed(list(self.inventory_materials_used_dynamics.keys())):
            verified_dynamics = dict()
            if os.path.exists(os.path.join(self._save_dir, 'inventory_materials_precondition',f'{action}.json')):
                continue
            index = 0
            action_dynamics = self.inventory_materials_used_dynamics[action]
            action_description = self._description[action]
            for _, dynamics in action_dynamics.items():
                print(dynamics)
                print('==========================================')

                try:
                    precondition = dynamics['all_common_materials_used']
                except:
                    continue
                if maxim_indices > len(action_description):
                    maxim_indices = len(action_description)
                sampled_descriptions = random.sample(action_description, maxim_indices)

                output_format = """{"inventory_materials_used": {transition_1: {inventory_materials_used}, transition_2: {inventory_materials_used}, ......}, "all_common_materials_used": {inventory_materials_used}, "within_all_common_materials_used": "yes/no", "valid": valid/invalid}"""
                prefix_prompt = "You are a helpful assistant tasked with verifying the inventory materials used pre-conditions for the action '{}'. Please respond in JSON format.".format(action)
                prompt = f"""
                In the crafter environment, you have discovered unique dynamics and need to verify the pre-conditions for the action '{action}'.
                Given the state transitions before and after taking the action '{action}', described as follows: {sampled_descriptions} 

                You are asked to verify the inventory materials used pre-conditions for the action '{action}' based on the discovered dynamics.

                Precondition: You need to use {precondition} to execute the action.

                For the verification, you need to consider the followings:
                - List all the inventory materials that are consumed not gained for each state transition and their corresponding quantity, materials are: wood, stone, coal, iron, diamond, sapling.
                - List the common inventory materials used across all the state transitions.
                - Determine if the inventory materials used mentioned in the pre-condition are within the common inventory materials used.
                - If it is within the common inventory materials used, then it is valid; otherwise, it is invalid.

                Finally, if there are more advanced tools exist, then it is invalid; otherwise, it is valid.
                Output in this format: {output_format}
                """
                precondition_verification = gpt_json(prefix_prompt, prompt)
                precondition_verification = json.loads(precondition_verification)
                print(action)
                print(dynamics['all_common_materials_used'])
                print(precondition_verification)
                print('==========================================')
                try:
                    if str(precondition_verification['valid']).lower() == 'valid':
                        verified_dynamics[index] = dynamics["all_common_materials_used"]
                    index += 1
                    with open(os.path.join(self._inventory_materials_used_dir, f'{action}.json'), 'w') as f:
                        json.dump(verified_dynamics, f, indent=4)
                except:
                    pass


    def _verify_dynamics_facing_object_change_precondition(self, maxim_indices=5):
        self._inventory_outcome_dir = os.path.join(self._save_dir, 'facing_object_change')
        if not os.path.exists(self._inventory_outcome_dir):
            os.makedirs(self._inventory_outcome_dir)
        for action in list(self.facing_object_change_dynamics.keys()):
            verified_dynamics = dict()
            if os.path.exists(os.path.join(self._save_dir, 'facing_object_change',f'{action}.json')):
                continue
            index = 0
            action_dynamics = self.facing_object_change_dynamics[action]
            action_description = self._description[action]
            for _, dynamics in action_dynamics.items():
                print(dynamics)
                print('==========================================')

                if maxim_indices > len(action_description):
                    maxim_indices = len(action_description)
                sampled_descriptions = random.sample(action_description, maxim_indices)
            
                try:
                    print(dynamics)
                    precondition = dynamics['common_facing_object_change']
                except:
                    continue

                output_format = """{"facing_object_change": {transition_1: {from...to...}, transition_2: {from...to...}, ......}, "common_facing_object_change": {from...to...}}, valid: "valid/invalid"} """
                prefix_prompt = "You are a helpful assistant tasked with verifying the facing object changes for the action '{}'. Please respond in JSON format.".format(action)
                prompt = f"""
                In the crafter environment, you have discovered unique dynamics and need to verify the outcome for the action '{action}'.
                Given the state transitions before and after taking the action '{action}', described as follows: {sampled_descriptions} 

                You are asked to verify the facing object changes after executing this action. '{action}' based on the discovered dynamics.
                
                predicted_changes: The facing object changes is {precondition} after executing the action.

                For the verification, you need to consider the followings:
                - List all the change about the facing object after executing the action for each state transition.
                - List the common change about the facing object across all the state transitions.
                - The common change must be present in all state transitions' facing object change; if no change can be found, simply output as "None".
                - Determine if the predicted changes are within the common changes.
                - If the predicted changes are within the common changes, then it is valid; otherwise, it is invalid.
                Output in this format: {output_format}
                """
                precondition_verification = gpt_json(prefix_prompt, prompt)
                precondition_verification = json.loads(precondition_verification)
                print(action)
                print(dynamics['common_facing_object_change'])
                print(precondition_verification)
                print('==========================================')
                try:
                    if str(precondition_verification['valid']).lower() == 'valid':
                        verified_dynamics[index] = dynamics["common_facing_object_change"]
                    index += 1
                    with open(os.path.join(self._inventory_outcome_dir, f'{action}.json'), 'w') as f:
                        json.dump(verified_dynamics, f, indent=4)
                except:
                    print('error')
                    pass


    def _verify_dynamics_inventory_outcome_precondition(self, maxim_indices=5):
        self._inventory_outcome_dir = os.path.join(self._save_dir, 'inventory_outcome')
        if not os.path.exists(self._inventory_outcome_dir):
            os.makedirs(self._inventory_outcome_dir)
        for action in reversed(list(self.inventory_outcome_dynamics.keys())):
            verified_dynamics = dict()
            if os.path.exists(os.path.join(self._save_dir, 'inventory_outcome',f'{action}.json')):
                continue
            index = 0
            action_dynamics = self.inventory_outcome_dynamics[action]
            action_description = self._description[action]
            for _, dynamics in action_dynamics.items():
                print(dynamics)
                print('==========================================')

                if maxim_indices > len(action_description):
                    maxim_indices = len(action_description)
                sampled_descriptions = random.sample(action_description, maxim_indices)
            
                try:
                    print(dynamics)
                    precondition = dynamics['common_increase']
                except:
                    continue

                output_format = """{"increases": {transition_1: {inventory_increase:..., status_increase:...}, transition_2: {inventory_increase:..., status_increase:...}, ......}, "common_increase": {inventory_increase:..., status_increase:...}, "valid": valid/invalid} """
                prefix_prompt = "You are a helpful assistant tasked with verifying the inventory and status outcome for the action '{}'. Please respond in JSON format.".format(action)
                prompt = f"""
                In the crafter environment, you have discovered unique dynamics and need to verify the outcome for the action '{action}'.
                Given the state transitions before and after taking the action '{action}', described as follows: {sampled_descriptions} 

                You are asked to verify the inventory and status increase after executing this action. '{action}' based on the discovered dynamics.
                
                predicted_increases: You only increase {precondition} in the inventory and status after executing the action.
                inventory: [wood, stone, coal, iron, diamond, sapling, wood_pickaxe, stone_pickaxe, iron_pickaxe, wood_sword, stone_sword, iron_sword]
                status: [health, food, drink, energy], the maximum value of status is 9 and you can use 'increased_to_9' to represent the status increase to the maximum value from the non-maximum value.

                For the verification, you need to consider the followings:
                - List all the increases of the inventory and status for each state transition after executing the action as the increases.
                - List the increases of the inventory and status that are common across all the state transitions after executing the action as the common increases.
                - The common increases must be present in all state transition's increases; if no inventory and status increases can be found, simply output as "None".
                - Determine if there are increases mentioned in the predicted_increases that are not in the common increases.
                - If there are increases mentioned in the predicted_increases that are not in the common increases, then it is invalid; otherwise, it is valid.
                Output in this format: {output_format}
                """
                precondition_verification = gpt_json(prefix_prompt, prompt)
                precondition_verification = json.loads(precondition_verification)
                print(action)
                print(dynamics['common_increase'])
                print(precondition_verification)
                print('==========================================')
                try:
                    if str(precondition_verification['valid']).lower() == 'valid':
                        verified_dynamics[index] = dynamics["common_increase"]
                    index += 1
                    with open(os.path.join(self._inventory_outcome_dir, f'{action}.json'), 'w') as f:
                        json.dump(verified_dynamics, f, indent=4)
                except:
                    print('error')
                    pass


if __name__ == '__main__':
    verify = Verify()
    verify._verify_dynamics_facing_objects_precondition()

