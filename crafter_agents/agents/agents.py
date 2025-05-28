from PIL import Image
import base64
import io
import crafter
import openai
import numpy as np
import matplotlib.pyplot as plt
import utils.memory as memory
import random
import json
import time
from utils.memory import *
from run_agents import *
from game.game_state import *
from basic_actions import *
from game.action_space import *
from agents.prompts import *
from utils.helper_functions import *
from game.game_infos import *


class lan_agent_react_v2:
    def __init__(self, game_state, action_space:ActionSpace,api_key):
        self.game_state = game_state
        self.recent_results = Recent_Results(num_of_results=5)
        openai.api_key = api_key
        self.action_space = action_space
        self.time = 0
        self.token_count = 0
        self.current_reasoning = None
        self.current_action = None
        self.current_observation = None
        self.step_count = 0
    

    def get_current_reasoning(self):
        self.current_reasoning =add_newlines(self.current_reasoning)
        return self.current_reasoning
    def get_current_action(self):
        
        return self.current_action
    def get_current_observation(self):
        self.current_observation =add_newlines(self.current_observation)
        return self.current_observation
    
    def prompt_creator(self):
        """
        create the prompt for the agent
        """
        mat_str = array_to_string(self.game_state.text_local_view_mat)
        obj_str = array_to_string(self.game_state.text_local_view_obj)
        

        
        print(self.game_state.walkable_view_string)
        language_wrapper_description_prompt = language_wrapper_description_prompt_creator(self.game_state.lan_wrapper)
        self.prompt = [
            # {"type": "text", "text": "Here is the local view of the map:"},
            # {"type": "text", "text": f"wood around you:{self.game_state.wood_matrix}\n"},
            # {"type": "text", "text": f"Materials around you:{self.game_state.text_local_view_mat}\n"},
            # {"type": "text", "text": f"Objects around you:{self.game_state.text_local_view_obj}\n"},

            # {"type": "text", "text": f"The closest wood locations are:{self.game_state.closest_wood}\n"},
            # {"type": "text", "text": f"The closest cows locations are:{self.game_state.closest_cows}\n"},
            {"type": "text", "text": f"Your current inventory: {self.game_state.inventory}\n"},
            {"type": "text", "text": f"Your current achievements: {self.game_state.achievements}\n"},
            {"type": "text", "text": f"{target_material_prompt(self)}\n"},
            {"type": "text", "text": f"{target_obj_prompt(self)}\n"},
            {"type": "text", "text": f"{self.game_state.walkable_description}\n"},
            {"type": "text", "text": f"{language_wrapper_description_prompt}\n"},
            # {"type": "text", "text": f"The walkable areas map is:{self.game_state.walkable_view_string}\nThe map is oriented with north at the top, south at the bottom, west on the left, and east on the right.before any reasoning, you should always print out the walkable condition of the surrounding position of the player. eg. 'the position One space due north of the player is walkable' or 'the position One space due north of the player is not walkable'\n"},
            {"type": "text", "text": f"the facing direction is {self.game_state.get_facing_direction()}. "},
            # {"type": "text", "text": f"the facing direction not affect the further moving direction of player. that is, if you facing south but a tree is in north side, you can directly move north without any problem\n"},
            {"type": "text", "text":"""(you need to let a material/object to be
            target of the player if you want to do some thing to it like collect it. if a material is One space to the north of the player, 
            and the player's facing direction is north, then this material/object will become the player's target.The same is true in several other directions)\n"""},
            {"type": "text", "text":"""When a object that going to be collect is adjacent to the player but not be faced by the player, you can using turn to function. For example,if a player is facing south, and there is a tree in north side, the player can turn to north to let the wood be the target of the player if the player wanna collect it.\n"""},
            {"type": "text", "text": f"""the action you can do currently is {self.action_space.get_valid_action_prompt(self.game_state)}. \n"""},
            {"type": "text", "text": f"""the action you cannot do currently with their 
            usage and using requirement is {self.action_space.get_invalid_action_prompt(self.game_state)}. By which you might be able to find some action
            you need to do but cannot do now because of requirement unmeeted, and learning how to meet the requirement of them.\n"""},
            {"type": "text", "text": "Your current task is to work to iterately move to closest trees and collect 10 woods and iterately move to closest cows and collect 10 meat\n"},
            # {"type": "text", "text": "Your current task is to work to iterately move to closest cows and collect 10 meat\n"},
            # {"type": "text", "text": "Your current task is to walk as far as possible in limited 30 steps by the walkable areas information\n"},
            {"type": "text", "text": """Given these information, which action should the player do?"""}
        ]
        # Structured Prompt for Crafter Environment LLM Agent
        
    def act(self):
        """
        1. retrieve game state from the game state class and update the prompt to the agent api
        2. send the prompt to the agent api and get the response(json file)
        3. parse the json file and get the action
        4. return the action
        """

        
        reasoning_way_prompt = reasoning_way_prompt_creator(self.action_space.get_valid_action_prompt(self.game_state))
        
        
        self.prompt_creator()
        start_time = time.time()
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": env_description_prompt},
                {"role": "system", "content": reasoning_way_prompt},
                {"role": "system", "content": format_prompt},
                {"role": "user", "content": self.prompt},
            ],
        )
        end_time = time.time()
        each_time = end_time - start_time
        
        tokens = response.usage.total_tokens
        self.token_count += tokens
        self.time += each_time
        
        try: 
            response_json = json.loads(response.choices[0].message.content)
            action = response_json.get('action')
            print("observation is :",response_json.get('observation'),'\n')
            print("reasoning is :",response_json.get('reasoning'),"\n")
            self.current_observation = response_json.get('observation')
            self.current_reasoning = response_json.get('reasoning')
            
            try:
                action = action.strip()  
                if action in legal_actions:  
                    self.current_action = action
                    print("action is :",action)
                    self.step_count += 1
                    return action
                else:
                    current_random_action = random.choice(legal_actions)
                    self.current_action = f"encode action failed. use random action{current_random_action}"
                    print(f"Invalid action from GPT: {action}. Choosing a random action instead.")
                    self.step_count += 1
                    return current_random_action
            except ValueError:
                current_random_action = random.choice(legal_actions)
                self.current_action = f"encode action failed. use random action{current_random_action}"
                print(f"Invalid GPT response: {action}. Choosing a random action instead.")
                self.step_count += 1
                return current_random_action
        except:
            current_random_action = random.choice(legal_actions)
            self.current_observation = "encode observation failed"
            self.current_reasoning = "encode reasoning failed"
            self.current_action = f"encode action failed. use random action{current_random_action}"
            print(f"Unable to encode json. This is the json-like string: {response.choices[0].message.content}. Choosing a random action instead.")
            self.step_count += 1
            return current_random_action






class random_agent:
    def __init__(self, env, api_key):
        self.env = env
        self.action_space = env.action_space
        openai.api_key = api_key

    def act(self, image_base64):
        prompt = [ 
            {"type": "text", "text": "Here is the map"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}", "detail": "high"}},
            {"type": "text", "text": """Given there are no diamonds in the map and diamonds can be found near stone, iron, coal, lava and path, which direction should the player to explore?"""}
        ]
        
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful agent for understanding the map. Please answer one signal word. only answer one of these four actions:'move_left', 'move_right', 'move_up', 'move_down'"},
                {"role": "user", "content": prompt},
            ],
        )
        
        
        action_text = response.choices[0].message.content
        print(response.choices[0].message.content)
        legal_actions = ['move_left', 'move_right', 'move_up', 'move_down']
        try:
            action = action_text.strip()  
            if action in legal_actions:  
                return action
            else:
                print(f"Invalid action from GPT: {action}. Choosing a random action instead.")
                return legal_actions.sample()
        except ValueError:
            print(f"Invalid GPT response: {action_text}. Choosing a random action instead.")
            return legal_actions.sample()
class cot_agent:
    def __init__(self, env, api_key):
        self.env = env
        self.action_space = env.action_space
        openai.api_key = api_key

    def act(self, image_base64):
        prompt = [ 
            {"type": "text", "text": "Here is the map"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}", "detail": "high"}},
            {"type": "text", "text": """Given there are no diamonds in the map and diamonds can be found near stone, iron, coal, lava and path, which direction should the player to explore?"""}
        ]
        example_prompt = """
            Here is an example of answer:

            {
  "reasoning": "1. **Current Position**: The player is located in an open grassy area with no visible nearby resources that indicate the presence of diamonds. 2. **Conditions for Finding Diamonds**: Diamonds are located near elements such as stone, iron, coal, lava, and paths. 3. **Exploration Requirement**: The current area shows no immediate signs of any of these elements. To find diamonds, exploring nearby areas is necessary. 4. **Possible Directions**: - **Left**: There may be more unobserved areas, potentially leading to resources. - **Right**: This area also appears unvisited, which could yield necessary elements. - **Up**: The area above doesn't provide much information regarding resources. - **Down**: Like the left and right, the down direction is unexplored. 5. **Conclusion**: Since the player is surrounded by unobserved areas on multiple sides, moving either left, right, or down might yield potential discoveries. However, to maximize exploration of unknown terrain, moving down seems to offer a clearer path to new areas, avoiding the limited visibility upwards.",
  "answer": "move_down"
    }
    ```
            """

        json_example_prompt = """
    Please return the following data in valid JSON format.
    The JSON should have the keys "reasoning" and "answer".  This JSON-like string you generate must be able to convert to json format by json.loads() function Here's an example of the expected format:

    {
    "reasoning": "Detailed explanation of the reasoning process",
    "answer": "move_left"  # Must be one of 'move_left', 'move_right', 'move_up', 'move_down'
    }. 
    """
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful agent for understanding the map. Please answer step by step using the Chain of Thought method. For each problem, you must show your reasoning process in detail before providing the final answer(shaped like \"reasoning process: 'the reasoning process'\"). After that, you should give a one-word answer shaped like \"answer: 'move_left'\". one of these four actions:'move_left', 'move_right', 'move_up', 'move_down' is the only acceptable answer. "+example_prompt+json_example_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        legal_actions = ['move_left', 'move_right', 'move_up', 'move_down']  
        try: 
            response_json = json.loads(response.choices[0].message.content)
            action = response_json.get('answer')
            try:
                action = action.strip()  
                if action in legal_actions:  
                    return action
                else:
                    print(f"Invalid action from GPT: {action}. Choosing a random action instead.")
                    return random.choice(legal_actions)
            except ValueError:
                print(f"Invalid GPT response: {action}. Choosing a random action instead.")
                return random.choice(legal_actions) 
        except:

            print(f"Unable encode json. This is the json-like string: {response.choices[0].message.content}. Choosing a random action instead.")
            return random.choice(legal_actions)
class react_agent:
    def __init__(self, env, api_key):
        self.env = env
        self.action_space = env.action_space
        openai.api_key = api_key
        self.time = 0
        self.token_count = 0
    def act(self, image_base64):
        prompt = [ 
            {"type": "text", "text": "Here is the map"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}", "detail": "high"}},
            {"type": "text", "text": """Given there are no diamonds in the map and diamonds can be found near stone, iron, coal, lava and path, which direction should the player to explore?"""}
        ]
        example_prompt = """
            You are an AI agent that uses the ReAct (Reasoning + Acting) framework to understanding the map. Your task is to observe the current situation, reason about the next best action, and then act based on your reasoning. You will alternate between reasoning and acting to achieve your goals. 

        For each step, follow these guidelines:
        1. **Reasoning**: Analyze the current environment and explain your reasoning step by step. Consider the current state and any available information to deduce the best possible action.
        2. **Action**: After reasoning, provide a specific action based on your analysis. The action should be a simple command (e.g., 'move_left', 'move_right', 'pick_item', etc.) that reflects your next move.
        3. **Environment Feedback**: After taking an action, observe the environment's feedback and incorporate it into your next reasoning step.
        4. **Iterate**: Repeat this process by alternating between reasoning and acting until the problem is solved.

        ### Example:
        #### Step 1:
        - **Observation**: The player is standing at a crossroads, with paths leading left, right, and forward. The left path is covered in dense forest, the right path shows signs of a river, and the forward path appears to lead to an open field.
        - **Reasoning**: Moving into the dense forest might slow progress and make exploration difficult. The river to the right could block further movement. The forward path seems to provide the most direct route for exploration.
        - **Action**: move_forward

        #### Step 2:
        - **Observation**: The player moved forward and now stands in the open field. There are mountains visible in the distance.
        - **Reasoning**: The open field is clear and provides visibility of distant landmarks. Heading toward the mountains may reveal new resources or opportunities.
        - **Action**: move_towards_mountains

        Furthermore, In this environment, for the action, one of these four actions:'move_left', 'move_right', 'move_up', 'move_down' is the only acceptable answer. 
        Please return the following data in valid JSON format.
        The JSON should have the keys "observation","reasoning" and "action".  This JSON-like string you generate must be able to convert to json format by json.loads() function Here's an example of the expected format:

    {
    "observation": "The player moved forward and now stands in the open field. There are mountains visible in the distance.",
    "reasoning": "The open field is clear and provides visibility of distant landmarks. Heading toward the mountains may reveal new resources or opportunities.",
    "action": "move_down"
    }.
    ```
            """

        start_time = time.time()
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": example_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        end_time = time.time()
        each_time = end_time - start_time
        tokens = response.usage.total_tokens
        self.token_count += tokens
        self.time += each_time
        legal_actions = ['move_left', 'move_right', 'move_up', 'move_down']  
        try: 
            response_json = json.loads(response.choices[0].message.content)
            action = response_json.get('action')
            print("observation is :",response_json.get('observation'),'\n')
            print("reasoning is :",response_json.get('reasoning'),"\n")
            try:
                action = action.strip()  
                if action in legal_actions:  
                    return action
                
                else:
                    print(f"Invalid action from GPT: {action}. Choosing a random action instead.")
                    return random.choice(legal_actions)
            except ValueError:
                print(f"Invalid GPT response: {action}. Choosing a random action instead.")
                return random.choice(legal_actions) 
        except:

            print(f"Unable encode json. This is the json-like string: {response.choices[0].message.content}. Choosing a random action instead.")
            return random.choice(legal_actions)
class lan_agent_random:
    def __init__(self, env, api_key):
        self.env = env
        openai.api_key = api_key
    
    def lang_wrapper(self,world,player):
        def extract_subarray(big_array, x, y, size=9):
            half_size = size // 2
            # Compute the boundaries while ensuring they don't go out of bounds
            x_min = max(0, x - half_size)
            x_max = min(big_array.shape[0], x + half_size + 1)

            y_min = max(0, y - half_size)
            y_max = min(big_array.shape[1], y + half_size + 1)

            # Extract the 9x9 subarray
            subarray = big_array[x_min:x_max, y_min:y_max]
            return subarray
        def map_array_to_text(array, mapping):
            reverse_mapping_dict = {v:k for k, v in mapping.items()}
            text_array = [[reverse_mapping_dict[element] for element in row] for row in array]
            return text_array
        
        wbarr_mat = world._world._mat_map
        wx, wy  = player.pos[0], player.pos[1]
        local_view_mat =  extract_subarray(wbarr_mat,wx,wy)

        wbarr_obj = world._world._obj_map
        wx, wy  = player.pos[0], player.pos[1]
        local_view_obj =  extract_subarray(wbarr_obj,wx,wy)

        mapping_mat = world._mat_ids
        mapping_obj_objform = world._obj_ids
        mapping_obj_strform = {
            "Nothing": 0,
            "Player" : 13,
            "Cow" : 14,
            "Zombie": 15,
            "Skeleton": 16,
            "Arrow":17,
            "Plant": 18
        }
        world_objs = world._world._objects
        def map_obj_to_num(obj):
            if obj is None:
                return 0
            else:
                return mapping_obj_objform.get(type(obj))
        world_objs_arr = np.array(world_objs)
        vectorized_map = np.vectorize(map_obj_to_num)
        list_objs_numform = vectorized_map(world_objs)

        world_objs_numform = np.array(list_objs_numform)[wbarr_obj]
        local_view_obj =  extract_subarray(world_objs_numform,wx,wy)
        text_local_view_mat = map_array_to_text(local_view_mat,mapping_mat)
        text_local_view_obj = map_array_to_text(local_view_obj,mapping_obj_strform)
        return text_local_view_mat, text_local_view_obj
    def act(self, local_view_mat,local_view_obj):
        # Convert the 9x9 arrays to a string format for the prompt
        def array_to_string(array):
            return '\n'.join([' '.join(map(str, row)) for row in array])
        
        mat_str = array_to_string(local_view_mat)
        obj_str = array_to_string(local_view_obj)
        
        prompt = [
            {"type": "text", "text": "Here is the local view of the map:"},
            {"type": "text", "text": f"Materials:\n{mat_str}"},
            {"type": "text", "text": f"Objects:\n{obj_str}"},
            {"type": "text", "text": """Given the materials and objects around the player, which direction should the player explore?"""}
        ]
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful agent for understanding the map. Please answer one signal word. Only answer one of these four actions: 'move_left', 'move_right', 'move_up', 'move_down'"},
                {"role": "user", "content": prompt},
            ],
        )
        
        action_text = response.choices[0].message.content
        print(response.choices[0].message.content)
        legal_actions = ['move_left', 'move_right', 'move_up', 'move_down']
        try:
            action = action_text.strip()  
            if action in legal_actions:  
                return action
            else:
                print(f"Invalid action from GPT: {action}. Choosing a random action instead.")
                return random.choice(legal_actions)
        except ValueError:
            print(f"Invalid GPT response: {action_text}. Choosing a random action instead.")
            return random.choice(legal_actions)
class lan_agent_cot:
    def __init__(self, env, api_key):
        self.env = env
        openai.api_key = api_key
    
    def lang_wrapper(self,world,player):
        def extract_subarray(big_array, x, y, size=9):
            half_size = size // 2
            # Compute the boundaries while ensuring they don't go out of bounds
            x_min = max(0, x - half_size)
            x_max = min(big_array.shape[0], x + half_size + 1)

            y_min = max(0, y - half_size)
            y_max = min(big_array.shape[1], y + half_size + 1)

            # Extract the 9x9 subarray
            subarray = big_array[x_min:x_max, y_min:y_max]
            return subarray
        def map_array_to_text(array, mapping):
            reverse_mapping_dict = {v:k for k, v in mapping.items()}
            text_array = [[reverse_mapping_dict[element] for element in row] for row in array]
            return text_array
        
        wbarr_mat = world._world._mat_map
        wx, wy  = player.pos[0], player.pos[1]
        local_view_mat =  extract_subarray(wbarr_mat,wx,wy)

        wbarr_obj = world._world._obj_map
        wx, wy  = player.pos[0], player.pos[1]
        local_view_obj =  extract_subarray(wbarr_obj,wx,wy)

        mapping_mat = world._mat_ids
        mapping_obj_objform = world._obj_ids
        mapping_obj_strform = {
            "Nothing": 0,
            "Player" : 13,
            "Cow" : 14,
            "Zombie": 15,
            "Skeleton": 16,
            "Arrow":17,
            "Plant": 18
        }
        world_objs = world._world._objects
        def map_obj_to_num(obj):
            if obj is None:
                return 0
            else:
                return mapping_obj_objform.get(type(obj))
        world_objs_arr = np.array(world_objs)
        vectorized_map = np.vectorize(map_obj_to_num)
        list_objs_numform = vectorized_map(world_objs)

        world_objs_numform = np.array(list_objs_numform)[wbarr_obj]
        local_view_obj =  extract_subarray(world_objs_numform,wx,wy)
        text_local_view_mat = map_array_to_text(local_view_mat,mapping_mat)
        text_local_view_obj = map_array_to_text(local_view_obj,mapping_obj_strform)
        return text_local_view_mat, text_local_view_obj
    
    def act(self, local_view_mat, local_view_obj):
        # Convert the 9x9 arrays to a string format for the prompt
        def array_to_string(array):
            return '\n'.join([' '.join(map(str, row)) for row in array])
        
        mat_str = array_to_string(local_view_mat)
        obj_str = array_to_string(local_view_obj)
        
        prompt = [
            {"type": "text", "text": "Here is the local view of the map:"},
            {"type": "text", "text": f"Materials:\n{mat_str}"},
            {"type": "text", "text": f"Objects:\n{obj_str}"},
            {"type": "text", "text": """Given the materials and objects around the player, which direction should the player explore?"""}
        ]
        
        example_prompt = """
            Here is an example of answer:
    
            {
    "reasoning": "1. **Current Position**: The player is located in an open grassy area with no visible nearby resources that indicate the presence of diamonds. 2. **Conditions for Finding Diamonds**: Diamonds are located near elements such as stone, iron, coal, lava, and paths. 3. **Exploration Requirement**: The current area shows no immediate signs of any of these elements. To find diamonds, exploring nearby areas is necessary. 4. **Possible Directions**: - **Left**: There may be more unobserved areas, potentially leading to resources. - **Right**: This area also appears unvisited, which could yield necessary elements. - **Up**: The area above doesn't provide much information regarding resources. - **Down**: Like the left and right, the down direction is unexplored. 5. **Conclusion**: Since the player is surrounded by unobserved areas on multiple sides, moving either left, right, or down might yield potential discoveries. However, to maximize exploration of unknown terrain, moving down seems to offer a clearer path to new areas, avoiding the limited visibility upwards.",
    "answer": "move_down"
    }
        """
        
        json_example_prompt = """
    Please return the following data in valid JSON format.
    The JSON should have the keys "reasoning" and "answer".  This JSON-like string you generate must be able to convert to json format by json.loads() function Here's an example of the expected format:
    
    {
    "reasoning": "Detailed explanation of the reasoning process",
    "answer": "move_left"  # Must be one of 'move_left', 'move_right', 'move_up', 'move_down'
    }. 
    """
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful agent for understanding the map. Please answer step by step using the Chain of Thought method. For each problem, you must show your reasoning process in detail before providing the final answer (shaped like \"reasoning process: 'the reasoning process'\"). After that, you should give a one-word answer shaped like \"answer: 'move_left'\". One of these four actions: 'move_left', 'move_right', 'move_up', 'move_down' is the only acceptable answer. " + example_prompt + json_example_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        
        legal_actions = ['move_left', 'move_right', 'move_up', 'move_down']  
        try: 
            response_json = json.loads(response.choices[0].message.content)
            action = response_json.get('answer')
            try:
                action = action.strip()  
                if action in legal_actions:  
                    return action
                else:
                    print(f"Invalid action from GPT: {action}. Choosing a random action instead.")
                    return random.choice(legal_actions)
            except ValueError:
                print(f"Invalid GPT response: {action}. Choosing a random action instead.")
                return random.choice(legal_actions) 
        except:
            print(f"Unable to encode json. This is the json-like string: {response.choices[0].message.content}. Choosing a random action instead.")
            return random.choice(legal_actions)
class lan_agent_react:
    def __init__(self, env, api_key):
        self.env = env
        openai.api_key = api_key
        self.time = 0
        self.token_count = 0
    
    def lang_wrapper(self,world,player):
        def extract_subarray(big_array, x, y, size=9):
            half_size = size // 2
            # Compute the boundaries while ensuring they don't go out of bounds
            x_min = max(0, x - half_size)
            x_max = min(big_array.shape[0], x + half_size + 1)

            y_min = max(0, y - half_size)
            y_max = min(big_array.shape[1], y + half_size + 1)

            # Extract the 9x9 subarray
            subarray = big_array[x_min:x_max, y_min:y_max]
            return subarray
        
        def map_array_to_text(array, mapping):
            reverse_mapping_dict = {v:k for k, v in mapping.items()}
            text_array = [[reverse_mapping_dict[element] for element in row] for row in array]
            return text_array
        
        wbarr_mat = world._world._mat_map
        wx, wy  = player.pos[0], player.pos[1]
        local_view_mat =  extract_subarray(wbarr_mat,wx,wy)

        wbarr_obj = world._world._obj_map
        wx, wy  = player.pos[0], player.pos[1]
        local_view_obj =  extract_subarray(wbarr_obj,wx,wy)

        mapping_mat = world._mat_ids
        mapping_obj_objform = world._obj_ids
        mapping_obj_strform = {
            "Nothing": 0,
            "Player" : 13,
            "Cow" : 14,
            "Zombie": 15,
            "Skeleton": 16,
            "Arrow":17,
            "Plant": 18
        }

        world_objs = world._world._objects
        def map_obj_to_num(obj):
            if obj is None:
                return 0
            else:
                return mapping_obj_objform.get(type(obj))
            
        world_objs_arr = np.array(world_objs)
        vectorized_map = np.vectorize(map_obj_to_num)
        list_objs_numform = vectorized_map(world_objs)

        world_objs_numform = np.array(list_objs_numform)[wbarr_obj]
        local_view_obj =  extract_subarray(world_objs_numform,wx,wy)
        text_local_view_mat = map_array_to_text(local_view_mat,mapping_mat)
        text_local_view_obj = map_array_to_text(local_view_obj,mapping_obj_strform)
        return text_local_view_mat, text_local_view_obj
    
    def act(self, local_view_mat, local_view_obj):
        # Convert the 9x9 arrays to a string format for the prompt
        def array_to_string(array):
            return '\n'.join([' '.join(map(str, row)) for row in array])
        
        mat_str = array_to_string(local_view_mat)
        obj_str = array_to_string(local_view_obj)
        
        prompt = [
            {"type": "text", "text": "Here is the local view of the map:"},
            {"type": "text", "text": f"Materials:\n{mat_str}"},
            {"type": "text", "text": f"Objects:\n{obj_str}"},
            {"type": "text", "text": """Given the materials and objects around the player, which direction should the player explore?"""}
        ]
        
        example_prompt = """
            You are an AI agent that uses the ReAct (Reasoning + Acting) framework to understanding the map. Your task is to observe the current situation, reason about the next best action, and then act based on your reasoning. You will alternate between reasoning and acting to achieve your goals. 
    
        For each step, follow these guidelines:
        1. **Reasoning**: Analyze the current environment and explain your reasoning step by step. Consider the current state and any available information to deduce the best possible action.
        2. **Action**: After reasoning, provide a specific action based on your analysis. The action should be a simple command (e.g., 'move_left', 'move_right', 'pick_item', etc.) that reflects your next move.
        3. **Environment Feedback**: After taking an action, observe the environment's feedback and incorporate it into your next reasoning step.
        4. **Iterate**: Repeat this process by alternating between reasoning and acting until the problem is solved.
    
        ### Example:
        #### Step 1:
        - **Observation**: The player is standing at a crossroads, with paths leading left, right, and forward. The left path is covered in dense forest, the right path shows signs of a river, and the forward path appears to lead to an open field.
        - **Reasoning**: Moving into the dense forest might slow progress and make exploration difficult. The river to the right could block further movement. The forward path seems to provide the most direct route for exploration.
        - **Action**: move_forward
    
        #### Step 2:
        - **Observation**: The player moved forward and now stands in the open field. There are mountains visible in the distance.
        - **Reasoning**: The open field is clear and provides visibility of distant landmarks. Heading toward the mountains may reveal new resources or opportunities.
        - **Action**: move_towards_mountains
    
        Furthermore, In this environment, for the action, one of these four actions:'move_left', 'move_right', 'move_up', 'move_down' is the only acceptable answer. 
        Please return the following data in valid JSON format.
        The JSON should have the keys "observation","reasoning" and "action".  This JSON-like string you generate must be able to convert to json format by json.loads() function Here's an example of the expected format:
    
    {
      "observation": "The player moved forward and now stands in the open field. There are mountains visible in the distance.",
      "reasoning": "The open field is clear and provides visibility of distant landmarks. Heading toward the mountains may reveal new resources or opportunities.",
      "action": "move_down"
    }.
        """
        start_time = time.time()
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": example_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        end_time = time.time()
        each_time = end_time - start_time
        legal_actions = ['move_left', 'move_right', 'move_up', 'move_down']  
        tokens = response.usage.total_tokens
        self.token_count += tokens
        self.time += each_time
        try: 
            response_json = json.loads(response.choices[0].message.content)
            action = response_json.get('action')
            print("observation is :",response_json.get('observation'),'\n')
            print("reasoning is :",response_json.get('reasoning'),"\n")
            try:
                action = action.strip()  
                if action in legal_actions:  
                    return action
                else:
                    print(f"Invalid action from GPT: {action}. Choosing a random action instead.")
                    return random.choice(legal_actions)
            except ValueError:
                print(f"Invalid GPT response: {action}. Choosing a random action instead.")
                return random.choice(legal_actions) 
        except:
            print(f"Unable to encode json. This is the json-like string: {response.choices[0].message.content}. Choosing a random action instead.")
            return random.choice(legal_actions)
