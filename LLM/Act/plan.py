import sys
sys.path.append('./')
from utils import *
from __init__ import *
from descriptor import StateDescriptor

env_dynamics = {
    "grass": "grass can be found near ['tree', 'water', 'path'], but it is not associated with ['diamond', 'coal', 'iron'] \n You can walk directly through grass. \n grass can only be used for: ['collect_sapling', 'eat_plant'] \n ",
    "coal": "coal can be found near ['stone', 'iron', 'diamond'], but it is not associated with ['grass', 'cow', 'skeleton'] \n You cannot walk directly through coal.coal turn into path after collect_coal \n coal can only be used for: ['make_iron_pickaxe', 'make_iron_sword', 'collect_coal'] \n coal can be collected by ['wood_pickaxe'] \n ",
    "cow": "cow can be found near ['grass', 'tree', 'water'] and appears more during daytime, but it is not associated with ['coal', 'diamond', 'iron'] \n You cannot walk directly through cow.cow turn into grass after eat_cow \n cow can only be used for: ['eat_cow'] \n ",
    "diamond": "diamond can be found near ['stone', 'iron', 'coal'], but it is not associated with ['grass', 'cow', 'tree'] \n You cannot walk directly through diamond.diamond turn into path after collect_diamond \n diamond can only be used for: ['collect_diamond'] \n diamond can be collected by ['iron_pickaxe'] \n ",
    "iron": "iron can be found near ['coal', 'diamond', 'stone'], but it is not associated with ['grass', 'cow', 'skeleton'] \n You cannot walk directly through iron.iron turn into path after collect_iron \n iron can only be used for: ['make_iron_pickaxe', 'make_iron_sword', 'collect_iron'] \n iron can be collected by ['stone_pickaxe'] \n ",
    "lava": "lava can be found near ['stone', 'water', 'sand'], but it is not associated with ['cow', 'tree', 'zombie'] \n You cannot walk directly through lava.",
    "skeleton": "skeleton can be found near ['zombie', 'lava', 'grass'], but it is not associated with ['cow', 'grass', 'coal'] \n You cannot walk directly through skeleton.skeleton turn into path after defeat_skeleton \n skeleton can only be used for: ['defeat_skeleton'] \n ",
    "stone": "stone can be found near ['iron', 'coal', 'diamond'], but it is not associated with ['cow', 'zombie', 'skeleton'] \n You cannot walk directly through stone.stone turn into path after collect_stone \n stone can be placed after place_stone\n stone can only be used for: ['make_stone_pickaxe', 'make_stone_sword', 'place_furnace', 'place_stone', 'collect_stone', 'eat_plant', 'sleep'] \n stone can be collected by ['wood_pickaxe'] \n ",
    "tree": "tree can be found near ['grass', 'path', 'water'], but it is not associated with ['coal', 'cow', 'diamond'] \n You cannot walk directly through tree.tree can only be used for: ['make_iron_pickaxe', 'make_iron_sword', 'make_stone_pickaxe', 'make_stone_sword', 'make_wood_pickaxe', 'make_wood_sword', 'place_table', 'collect_wood'] \n ",
    "water": "water can be found near ['sand', 'grass', 'tree'], but it is not associated with ['coal', 'diamond', 'iron'] \n You cannot walk directly through water.water can only be used for: ['collect_drink'] \n ",
    "zombie": "zombie can be found near ['skeleton', 'grass', 'cow'] and appears more during nighttime , but it is not associated with ['coal', 'diamond', 'iron'] \n You cannot walk directly through zombie.zombie turn into grass after defeat_zombie \n zombie can only be used for: ['defeat_zombie'] \n ",
    "plant": "plant can be found near ['grass', 'tree', 'water'], but it is not associated with ['coal', 'diamond', 'iron'] \n You cannot walk directly through plant.plant turn into plant after eat_plant \n plant can be placed after place_plant\n ",
    "path": "path can be found near ['grass', 'tree', 'water'], but it is not associated with ['zombie', 'coal', 'cow'] \n You can walk directly through path. \n path can only be used for: ['sleep'] \n ",
    "sand": "sand can be found near ['water', 'grass', 'path'], but it is not associated with ['coal', 'diamond', 'lava'] \n You can walk directly through sand. \n ",
    "plant-ripe": "plant-ripe can be found near ['grass', 'water', 'stone'], but it is not associated with ['coal', 'cow', 'diamond'] \n You cannot walk directly through plant-ripe.plant-ripe can only be used for: ['eat_plant'] \n ",
    "table": "table requires {'wood': 2} in the inventory to make or place \n ",
    "furnace": "furnace requires ['table'] within immediate distance to make or place \n furnace requires 4 stone \n ",
    "sapling": "You cannot walk directly through sapling.sapling can only be used for: ['place_plant'] \n sapling can be collected by ['wood_sword', 'wood_pickaxe'] \n ",
    "wood_pickaxe": "wood_pickaxe requires ['table'] within immediate distance to make or place \n wood_pickaxe 1 wood \n ",
    "stone_pickaxe": "stone_pickaxe requires ['table'] within immediate distance to make or place \n stone_pickaxe requires 1 wood and 1 stone \n ",
    "iron_pickaxe": "iron_pickaxe requires ['furnace', 'table'] within immediate distance to make or place \n iron_pickaxe requires 1 iron, 1 coal and 1 wood\n ",
    "wood_sword": "wood_sword requires ['table'] within immediate distance to make or place \n wood_sword requires 1 wood \n ",
    "stone_sword": "stone_sword requires ['table'] within immediate distance to make or place \n stone_sword requires 1 wood and 1 stone \n ",
    "iron_sword": "iron_sword requires ['furnace', 'table'] within immediate distance to make or place \n iron_sword requires 1 iron, 1 coal and 1 wood\n ",
    "sleep": "sleep requires ['path', 'stone'] within immediate distance and a stone_sword \n ",
}

class Subgoal_Planner:
    def __init__(self):
        with open('./Act/ground_truth_plan.json', 'r') as f:
            self._ground_truth_plan = json.load(f)
        with open('./Act/ground_truth_subtask.json', 'r') as f:
            self._ground_truth_subtask = json.load(f)


    def _select_subgoal(self, transition):
        inventory, state_description = transition['inventory'], transition['state_description']
        if inventory['wood'] < 4 and inventory['wood_pickaxe'] == 0 and 'table' not in state_description:
            return self._ground_truth_plan["subgoal_1"]
        elif 'table' not in state_description and inventory['wood_pickaxe'] == 0:
            return self._ground_truth_plan["subgoal_2"]
        elif inventory['wood_pickaxe'] == 0:
            return self._ground_truth_plan["subgoal_3"]
        elif inventory['wood_sword'] == 0:
            return self._ground_truth_plan["subgoal_4"]
        elif inventory['wood'] < 2 and inventory['stone_pickaxe'] == 0:
            return self._ground_truth_plan["subgoal_5"]
        elif inventory['sapling'] == 0 and 'plant' not in state_description and inventory['stone_pickaxe'] == 0:
            return self._ground_truth_plan["subgoal_6"]
        elif 'plant' not in state_description and inventory['stone_pickaxe'] == 0:
            return self._ground_truth_plan["subgoal_7"]
        elif inventory['stone'] < 6 and inventory['stone_pickaxe'] == 0 and 'furnace' not in state_description:
            return self._ground_truth_plan["subgoal_8"]
        elif 'furnace' not in state_description and inventory['stone_pickaxe'] == 0:
            return self._ground_truth_plan["subgoal_9"]
        elif inventory['stone_pickaxe'] == 0:
            return self._ground_truth_plan["subgoal_10"]
        elif inventory['stone_sword'] == 0:
            return self._ground_truth_plan["subgoal_11"]
        elif inventory['iron_pickaxe'] == 0 and inventory['stone'] < 2:
            return self._ground_truth_plan["subgoal_12"]
        elif inventory['iron_pickaxe'] == 0 and inventory['coal'] < 2:
            return self._ground_truth_plan["subgoal_13"]
        elif inventory['iron_pickaxe'] == 0 and inventory['iron'] < 2:
            return self._ground_truth_plan["subgoal_14"]
        elif inventory['iron_pickaxe'] == 0:
            return self._ground_truth_plan["subgoal_15"]
        elif inventory['iron_sword'] == 0:
            return self._ground_truth_plan["subgoal_16"]
        elif inventory['diamond'] < 2:
            return self._ground_truth_plan["subgoal_17"]
        else:
            print('All subgoals completed')
            raise Exception('All subgoals completed')
        

    def plan(self, transition):
        subgoal = self._select_subgoal(transition)
        print('Current subgoal: ', subgoal)
        print('='*50)
        return {'subgoal': subgoal}

    
class Subtask_Planner:
    def __init__(self):
        with open('./Act/ground_truth_subtask.json', 'r') as f:
            self._ground_truth_subtask = json.load(f)
        self._subgoal_planner = Subgoal_Planner()
        self._subgoal_termination = False
        self._subgoal = None


    def _select_available_subtasks(self, transition):
        inventory = transition['inventory']
        available_subtasks = []

        if inventory['energy'] < 9 and inventory['stone_sword'] > 0:
            available_subtasks.append({'sleep': self._ground_truth_subtask['sleep']})

        # basic actions with no pre-conditions
        available_subtasks.append({'collect_wood': self._ground_truth_subtask['collect_wood']})

        if inventory['wood_pickaxe'] > 0:
            available_subtasks.append({'collect_water': self._ground_truth_subtask['collect_water']})

        if inventory['wood_pickaxe'] > 0 and inventory['wood_sword'] > 0:
            available_subtasks.append({'collect_sapling': self._ground_truth_subtask['collect_sapling']})

        if inventory['sapling'] > 0 and inventory['wood_pickaxe'] > 0 and inventory['wood_sword'] > 0:
            available_subtasks.append({'place_plant': self._ground_truth_subtask['place_plant']})
        
        # if 'plant-ripe' in state_description.lower():
        #     available_subtasks.append({'collect_plant': self._ground_truth_subtask['collect_plant']})
        
        if inventory['stone'] > 0:
            available_subtasks.append({'place_stone': self._ground_truth_subtask['place_stone']})

        # actions with wood_pickaxe pre-conditions
        if inventory['wood_pickaxe'] > 0:
            available_subtasks.append({'collect_stone': self._ground_truth_subtask['collect_stone']})
            available_subtasks.append({'collect_coal': self._ground_truth_subtask['collect_coal']})

        # actions with wood_sword pre-conditions
        if inventory['stone_sword'] > 0:
            available_subtasks.append({'defeat_skeleton': self._ground_truth_subtask['defeat_skeleton']})
        if inventory['wood_sword'] > 0:
            available_subtasks.append({'defeat_zombie': self._ground_truth_subtask['defeat_zombie']})
        if inventory['wood_sword'] > 0 and inventory['stone_sword'] > 0:
            available_subtasks.append({'eat_cow': self._ground_truth_subtask['eat_cow']})        

        
        # actions with stone_pickaxe pre-conditions
        if inventory['stone_pickaxe'] > 0:
            available_subtasks.append({'collect_iron': self._ground_truth_subtask['collect_iron']})

        # actions with diamond_pickaxe pre-conditions
        if inventory['iron_pickaxe'] > 0:
            available_subtasks.append({'collect_diamond': self._ground_truth_subtask['collect_diamond']})
            available_subtasks.append({'eat_plant': self._ground_truth_subtask['collect_plant']})

        # actions with table pre-conditions
        if inventory['wood'] >= 1:
            available_subtasks.append({'make_wood_pickaxe': self._ground_truth_subtask['make_wood_pickaxe']})
        if inventory['wood'] >= 1 and inventory['wood_pickaxe'] >= 1:
            available_subtasks.append({'make_wood_sword': self._ground_truth_subtask['make_wood_sword']})
        if inventory['wood'] >= 1 and inventory['stone'] >= 1:
            available_subtasks.append({'make_stone_pickaxe': self._ground_truth_subtask['make_stone_pickaxe']})
        if inventory['wood'] >= 1 and inventory['stone'] >= 1:
            available_subtasks.append({'make_stone_sword': self._ground_truth_subtask['make_stone_sword']})
        
        # actions with table and furnace pre-conditions
        # print(state_description)
        if inventory['wood'] >= 1 and inventory['coal'] >= 1 and inventory['iron'] >= 1:
            available_subtasks.append({'make_iron_pickaxe': self._ground_truth_subtask['make_iron_pickaxe']})
        if inventory['wood'] >= 1 and inventory['coal'] >= 1 and inventory['iron'] >= 1 and inventory['stone_sword'] >=1 and inventory['iron_pickaxe'] >= 1:
            available_subtasks.append({'make_iron_sword': self._ground_truth_subtask['make_iron_sword']})

        # actions with place_X
        if inventory['wood'] >= 2:
            available_subtasks.append({'place_table': self._ground_truth_subtask['place_table']})
        if inventory['stone'] >= 4:
            available_subtasks.append({'place_furnace': self._ground_truth_subtask['place_furnace']})
        
        truncated_available_subtasks = dict()
        for subtask in available_subtasks:
            (subtask_name, subtask_content), = subtask.items()
            truncated_available_subtasks[subtask_name] = {'Pre-conditions': subtask_content['Pre-conditions']}
            truncated_available_subtasks[subtask_name] = {'Outcome': subtask_content['Outcome']}
            truncated_available_subtasks[subtask_name] = {'termination_condition': subtask_content['termination_condition']}
        print('available_subtasks: ', list(truncated_available_subtasks.keys()))
        return truncated_available_subtasks

    
    def _select_subtask(self, transition):
        
        subtask = None
        feedback = {"You should only select from the provided available subtasks."}

        while subtask not in transition['available_subtasks']:
            prefix_prompt = "You are a helpful assistant, tasked with guiding the player to choose the best subtask to execute next to complete the current subgoal. Please provide your answer in JSON format."
            subtask_format = """{
                'subgoal_related_objects': {'object_1_name': {'location': object 1's location, 'reachable': object 1 is reachable or not}, ......},
                'top_3_subtasks_and_their_objects': {'subtask_name_1': {'object_1_name': {'dynamic': object 1's dynamic}, ......}
                                           'subtask_name_2': ......
                                           'subtask_name_3': ......},
                'top_3_subtasks_consequences': {'subtask_name_1': 'consequences', 'subtask_name_2': 'consequences', 'subtask_name_3': 'consequences'},
                'subtask_name': 'subtask_name',
                'subtask_justification': 'justification'
            }"""
            prompt = f"""
            Given the following details:
            - Subgoal: {transition['subgoal']}.
            - Previous subtask {transition['previous_subtask']},
            - Current observation {transition['state_description']}, 
            - Environment's Dynamics: {env_dynamics}
            
            You are asked to:
            - identify the objects related to the current subtask and provide their locations and dynamics.
            - select the top 3 subtasks that you considered to be the best for completing the current subgoal and provide all the objects with their dynamics related to each subtask.
            - based on each subtask's related objects, provide the rationale and detailed consequences of executing each subtask on the objects.
            - select the best subtask to execute next for completing the current subgoal and provide the justification for your choice.
            
            Note: Avoid unnecessary crafting and placement if the items are within reachable distance.
            Lastly, select the subtask only from the available subtasks: {transition['available_subtasks']}; {feedback}.

            Please format your response in the following format: {subtask_format}
            """
            subtask_and_thoughts = gpt_json(prefix_prompt, prompt)
            try:
                subtask_and_thoughts = json.loads(subtask_and_thoughts)
                subtask = subtask_and_thoughts["subtask_name"]
                thoughts = subtask_and_thoughts
            except:
                print('Keyerror in subtask selection')
                print(subtask_and_thoughts)
            if subtask not in transition['available_subtasks']:
                feedback.add(f"{subtask} is not available in the current state.")
                print(feedback)
                print(transition['available_subtasks'])
        
        print(subtask_and_thoughts)
        transition['subtask'] = {'subtask': self._ground_truth_subtask[subtask], 'subtask_justification': thoughts['subtask_justification']}
        
        return transition
    

    def _terminate_subgoal(self, transition):
        if self._subgoal is None:
            return True, None
        
        prefix_prompt = "You are a helpful assistant, tasked with deciding whether the current subgoal should be terminated or not. Please answer in JSON format."
        output_format = '{"Termination": "Yes/No", "Justification": "..." }'  # Adjusted to valid JSON format
        prompt = f"""
        Given the following details to consider:
        Current observation: {transition['state_description']}, 
        Initial observation: {transition['subgoal_initial_state_description']}, 
        Previous subtask: {transition['previous_subtask']}, 
        Subgoal description: {transition['subgoal']}, 
        you are asked to decide whether the subgoal should be terminated or not.

        For deciding whether to terminate the subgoal, consider the following:
        - The previous subtask and its termination reason.
        - The difference between the current observation and the initial observation, including changes in the inventory.

        If the subgoal's termination condition has been met, output 'Yes'; otherwise, output 'No'. Also, provide a concise justification for the decision.
        Output in this format: {output_format}.
        """
        termination = gpt_json(prefix_prompt, prompt)
        termination = json.loads(termination)
        if 'yes' in termination['Termination'].lower():
            return True, termination['Justification']
        return False, None
    
    
    def _evolve(self, transition):
        prefix_prompt = "You are a helpful assistant tasked with evolving useful and advanced dynamics from primitive dynamics. Please answer in JSON format."

        output_format = """{
            "Object_required_for_the_subtask": {
                "Situation": "Description of the required object's location.",
                "Dynamics_1": {
                    "description": "a detailed dynamics description of the dynamics for solving the difficulty",
                    "primitive_dynamics_used": "primitive dynamics involved in the situation",
                    "deductive_reasoning_steps": "{'step_1': {'rule_of_inference': '...', 'reasoning': '...'}, 'step_2': {'rule_of_inference': '...', 'reasoning': '...'}, ...}"
                },
                "Dynamics_2": {
                    "description": "a detailed dynamics description of the dynamics for solving the difficulty",
                    "primitive_dynamics_used": "primitive dynamics involved in the situation",
                    "deductive_reasoning_steps": "{'step_1': {'rule_of_inference': '...', 'reasoning': '...'}, 'step_2': {'rule_of_inference': '...', 'reasoning': '...'}, ...}"
                },
                "Dynamics_3": {
                    "description": "a detailed dynamics description of the dynamics for solving the difficulty",
                    "primitive_dynamics_used": "primitive dynamics involved in the situation",
                    "deductive_reasoning_steps": "{'step_1': {'rule_of_inference': '...', 'reasoning': '...'}, 'step_2': {'rule_of_inference': '...', 'reasoning': '...'}, ...}"
                }
            },
            "Possible_obstacles": {
                "Situation": "Description of all possible obstacles that may be encountered along the way.",
                "Dynamics_1": {
                    "description": "a detailed dynamics description of the dynamics for solving the difficulty",
                    "primitive_dynamics_used": "primitive dynamics involved in the situation",
                    "deductive_reasoning_steps": "{'step_1': {'rule_of_inference': '...', 'reasoning': '...'}, 'step_2': {'rule_of_inference': '...', 'reasoning': '...'}, ...}"
                },
                "Dynamics_2": {
                    "description": "a detailed dynamics description of the dynamics for solving the difficulty",
                    "primitive_dynamics_used": "primitive dynamics involved in the situation",
                    "deductive_reasoning_steps": "{'step_1': {'rule_of_inference': '...', 'reasoning': '...'}, 'step_2': {'rule_of_inference': '...', 'reasoning': '...'}, ...}"
                },
                "Dynamics_3": {
                    "description": "a detailed dynamics description of the dynamics for solving the difficulty",
                    "primitive_dynamics_used": "primitive dynamics involved in the situation",
                    "deductive_reasoning_steps": "{'step_1': {'rule_of_inference': '...', 'reasoning': '...'}, 'step_2': {'rule_of_inference': '...', 'reasoning': '...'}, ...}"
                }
            }
        }"""

        prompt = f"""
        Given the following details:
        - Primitive dynamics: {env_dynamics}
        - Current subtask: {transition['subtask']}
        - Current observation: {transition['state_description']}

        You are asked to identify the difficulties in completing the current subtask and provide 3 primitive or evolved dynamics to solve each of these difficulties.

        Instructions for identifying difficulties:
        - List the objects required to complete the subtask, specify their locations, and explain where to find them if they are not in the current observation. 
        - Outline all possible obstacles that may be encountered along the way.

        Instructions for evolving advanced dynamics:
        - Do not introduce any new objects that are not part of the primitive dynamics.
        - The evolved dynamics should not contradict the primitive dynamics.
        - If a difficulty cannot be resolved by existing dynamics, evolve new and advanced dynamics by combining only existing dynamics using deductive reasoning.

        Instructions for providing deductive reasoning steps:
        - For each evolved dynamics, provide the used primitive dynamics.
        - For the deductive reasoning steps, provide the steps to combine the primitive dynamics to evolve the advanced dynamics and the rule of inference used (Modus Ponens, Modus Tollens, ......)

        Last, for each situation and dynamics should be general and do not contain details about specific locations about the objects.
        Output in the following format:{output_format} and leaves 'None' for deductive_reasoning_steps if the dynamics are primitive.
        """
        reformatted_dynamics = None
        while reformatted_dynamics is None:
            try:
                evolved_dynamics = gpt_json(prefix_prompt, prompt)
                evolved_dynamics = json.loads(evolved_dynamics)
                transition['evolved_dynamics'] = evolved_dynamics
                transition['primitive_dynamics'] = env_dynamics
                print('Subtask: ', transition['subtask'])
                print('Evolved dynamics: ', evolved_dynamics)

                reformatted_dynamics = dict()
                dynamics_count = 0
                for _, dynamics in evolved_dynamics.items():
                    for _, dynamics_content in dynamics.items():
                        reformatted_dynamics[dynamics_count] = dynamics_content
                        dynamics_count += 1
                transition['reformatted_dynamics'] = reformatted_dynamics
            except:
                print('Error in evolving dynamics')
                reformatted_dynamics = None

        return transition


    def _evolve_critics(self, transition):
        prefix_prompt = "You are a helpful assistant tasked with examing the validity and usefulness of the evolved dynamics. Please answer in JSON format."

        output_format = """ 
            "0": {"introduce_new_dynamics": "true/false", "introduce_new_objects": "true/false", "contradict_with_primitive_dynamics": "true/false", 'usefulness': '5/4/3/2/1'},
            "0": {"introduce_new_dynamics": "true/false", "introduce_new_objects": "true/false", "contradict_with_primitive_dynamics": "true/false", 'usefulness': '5/4/3/2/1'},
            "0": {"introduce_new_dynamics": "true/false", "introduce_new_objects": "true/false", "contradict_with_primitive_dynamics": "true/false", 'usefulness': '5/4/3/2/1'},
            ...
        }"""

        prompt = f"""
        Given the following details:
        - Primitive dynamics: {env_dynamics}
        - Evolved dynamics: {transition['reformatted_dynamics']}
        - Current subtask: {transition['subtask']}

        You are asked to examine the validity of the evolved dynamics and provide feedback.

        Instructions for examining the validity of the evolved dynamics:
        - The evolved dynamics should only be a combination of existing dynamics using deductive reasoning and should not introduce new dynamics. Output 'True' if the evolved dynamics introduce new dynamics; otherwise, output 'False'.
        - The evolved dynamics should not introduce any new objects that are not mentioned in the primitive dynamics. Output 'True' if the evolved dynamics introduce new objects; otherwise, output 'False'.
        - Each deductive reasoning step should not contradict any of the primitive dynamics. Output 'True' if the evolved dynamics contradict the primitive dynamics; otherwise, output 'False'.

        Instructions for examing the usefulness of the evolved dynamics:
        - The difficulties should be directly related to the current subtask.
        - The evolved dynamics should be useful in solving the difficulties identified in the subtask.
        - Evluating the usefulness of the evolved dynamics on a scale of 1 to 5, where 5 is the most useful and 1 is the least useful.

        Last, output the validity of the evolved dynamics in the following format: {output_format}.
        """
        filtered_evolved_dynamics = None
        while filtered_evolved_dynamics is None:
            try:

                critics = gpt_json(prefix_prompt, prompt)
                critics = json.loads(critics)
                transition['critics'] = critics
                filtered_evolved_dynamics = dict()
                evolved_dynamics = transition['evolved_dynamics']
                dynamics_count = 0
                for difficulty_name, dynamics in evolved_dynamics.items():
                    filtered_evolved_dynamics[difficulty_name] = dict()
                    for situation, dynamics_content in dynamics.items():
                        if str(critics[str(dynamics_count)]['introduce_new_dynamics']).lower() == 'false' and str(critics[str(dynamics_count)]['introduce_new_objects']).lower() == 'false' and str(critics[str(dynamics_count)]['contradict_with_primitive_dynamics']).lower() == 'false' and int(critics[str(dynamics_count)]['usefulness']) >= 3:
                            filtered_evolved_dynamics[difficulty_name][situation] = dynamics_content
                            
                        dynamics_count += 1
                transition['filtered_evolved_dynamics'] = filtered_evolved_dynamics
            except:
                print('Error in evolving dynamics')
                filtered_evolved_dynamics = None
        return transition


    def plan(self, transition):
        termination, reason = self._terminate_subgoal(transition)
        if termination:
            print('Subgoal: ', self._subgoal, ' terminated. Reason: ', reason)
            self._subgoal = self._subgoal_planner.plan(transition)
            transition['subgoal'] = self._subgoal
            transition['subgoal_termination'] = True
            transition['subgoal_termination_reason'] = reason
            transition['subgoal_initial_state_description'] = transition['state_description']

        available_subtasks = self._select_available_subtasks(transition)
        transition['available_subtasks'] = available_subtasks
        transition = self._select_subtask(transition)
        transition = self._evolve(transition)
        transition = self._evolve_critics(transition)
        return transition