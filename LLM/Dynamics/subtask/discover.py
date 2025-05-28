import sys
sys.path.append('./')
from __init__ import *
from descriptor import SimplifiedStateDescriptor

class Discover:
    def __init__(self, trajectory_dir='dynamics/subtask/segmented_trajectory', merged_action_dir = 'dynamics/action/dynamics/merged',
                 save_dir='dynamics/subtask/discovered'):
        self._subtasks = ['collect_coal', 'collect_diamond', 'collect_drink', 'collect_iron', 'collect_sapling', 'collect_stone', 'collect_wood', 'defeat_skeleton', 
                         'defeat_zombie', 'eat_cow', 'eat_plant', 'make_iron_pickaxe', 'make_iron_sword', 'make_stone_pickaxe', 'make_stone_sword', 'make_wood_pickaxe', 
                         'make_wood_sword', 'place_furnace', 'place_plant', 'place_stone', 'place_table', 'sleep']
        # self._load_trajectory(trajectory_dir)
        # self._describe()
        self._save_path = save_dir
        if not os.path.exists(self._save_path):
            os.makedirs(self._save_path)
       
        with open(os.path.join(merged_action_dir, 'facing_object_change.json'), 'r') as f:
            self.facing_object_change = json.load(f)

        with open(os.path.join(merged_action_dir, 'facing_object_preconditions.json'), 'r') as f:
            self.facing_object_preconditions = json.load(f)

        with open(os.path.join(merged_action_dir, 'immediate_object_preconditions.json'), 'r') as f:
            self.immediate_object_preconditions = json.load(f)

        with open(os.path.join(merged_action_dir, 'inventory_materials_precondition.json'), 'r') as f:
            self.inventory_materials_precondition = json.load(f)

        with open(os.path.join(merged_action_dir, 'inventory_outcome.json'), 'r') as f:
            self.inventory_outcome = json.load(f)

        with open(os.path.join(merged_action_dir, 'inventory_tool_precondition.json'), 'r') as f:
            self.inventory_tool_precondition = json.load(f)
        
        self._load_trajectory(trajectory_dir)
        self._describe()
    

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
                    
                    transition_description = f"""In transition, for executing the subtask{action}, these actions are taken: {trajectory[traj_i]['action']} and observation changes are: {trajectory[traj_i]['descriptions']}. \n"""
                    self._description[action].append(transition_description)

    
    def discover(self, sampled_num=5):
        for action in self._description:
            prefix_prompt = "You are a helpful assistant tasked with discover the facing object pre-conditions for the action '{}'. Please respond in JSON format.".format(action)
            output_format = """{"facing_object_before_action": {transition_1: {facing_object_before_action}, transition_2: {facing_object_before_action}, ......}, "all_facing_object_before_action": {facing_object_before_action}}"""


            description = self._description[action]
            dynamics = dict()
            save_path = os.path.join(self._save_path, f'{action}.json')
            if os.path.exists(save_path):
                continue

            if sampled_num > len(description):
                sampled_num = len(description)
            sampled_descriptions = random.sample(description, sampled_num)
            
            partial_description = ' '.join(sampled_descriptions)

            examples = """
            "place_furnace": {
                "General Plan": {
                    "step_1": "Moving toward the table; if no table can be found, place the table first.",
                    "step_2": "Execute the place_furnace action, when it is available."
                },
                "termination_condition": "There is a furnace in the observation and nearby with no obstacles in between, or the food, drink, or energy levels are low, or there are zombies or skeletons nearby."
            },

            "defeat_zombie": {
                "General Plan": {
                    "step_1": "Navigate the environment to locate zombies, considering they can spawn on grass or path surfaces.",
                    "step_3": "Position you within a immediate distance of a zombie to engage.",
                    "step_4": "Face the zombie to fulfill the action requirement for defeat_zombie.",
                    "step_5": "Execute the defeat_zombie action to successfully eliminate the zombie."
                },
                "termination_condition": "there are no zombies nearby."
            },
            "make_iron_pickaxe": {
                "General Plan": {
                    "step_1": "Walk to the nearest table and furnace",
                    "step_2": "Standing within immediate distance from both the table and furnace",
                    "step_3": "Use the crafting table and furnace to make an iron pickaxe."
                },
                "termination_condition": "The inventory's iron_pickaxe amount increased by 1, or the food, drink, or energy levels are low, or there are zombies or skeletons nearby."
            },
            """

            subtask_plan_format = """ 
            "subtask_name": {
                "General Plan": {
                    "step_1": "......",
                    "step_2": "......",
                    "step_3": "......."
                },
                "termination_condition": "....."
            },
            """

            prefix_prompt = "You are an AI agent tasked with writing the subtask plan for the Crafter environment in the json format."
            prompt = f"""
            In the Crafter environment, the world dynamics are complex and there are many subtasks to be completed.
            Here are the dynamics about the core action {action}:
            The precondition:
            - it need to face: {self.facing_object_preconditions[action]}
            - it need to have {self.immediate_object_preconditions[action]} within immediate distance
            - it need to have {self.inventory_materials_precondition[action]} in the inventory.
            - it need to have {self.inventory_tool_precondition[action]} in the inventory.
            The outcome:
            - its facing object changes to {self.facing_object_change[action]}
            - its inventory and status outcome increases on {self.inventory_outcome[action]}
            Note: 'None' indicates that there are no specific preconditions or outcomes for the corresponding elements of the dynamics."

            Given the subtask "{action}", I want you to write the step-plan for completing this subtask.
            First, read and understand all the provided world dynamics.
            Then, locate the world dynamics that are relevant to the subtask.
            Next, write the subtask's requirements, the step-plan for completing the subtask based on the world dynamics and the outcomes in this format {subtask_plan_format}
                -steps: the general steps required to complete the subtask.
                -termination_condition: when should this subtask be terminated; you should consider the status, potential danger and the outcome of the action
            Finally, only output the plan for the subtask.
            Here are a few examples: {examples}

            Here are the observations on how to completing the subtask: {partial_description}
            """

            action_dynamics = gpt_json(prefix_prompt, prompt)
            action_dynamics = json.loads(action_dynamics)
            
            dynamics[len(dynamics)] = action_dynamics
        
            with open(save_path, 'w') as f:
                json.dump(dynamics, f, indent=4)





if __name__ == '__main__':
    discover = Discover()
    # discover.discover()

    subtasks = dict()
    for file in os.listdir('dynamics/subtask/discovered'):
        with open(os.path.join('dynamics/subtask/discovered', file), 'r') as f:
            subtask = json.load(f)
        subtask = subtask['0']
        action_name = file[:-5]
        subtask[action_name][f'precondition_for_executing_the_action_{action_name}'] = {}
        if discover.facing_object_preconditions[action_name] is not None:
             subtask[action_name][f'precondition_for_executing_the_action_{action_name}']['facing_object'] = f'You need to face one of the following objects {discover.facing_object_preconditions[action_name]}'
        if discover.immediate_object_preconditions[action_name] is not None:
             subtask[action_name][f'precondition_for_executing_the_action_{action_name}']['immediate_objects'] = f'You need to have these objects within immediate distance: {discover.immediate_object_preconditions[action_name]}'

        subtasks.update(subtask)
    with open('./demo.json', 'w') as f:
        json.dump(subtasks, f, indent=4)