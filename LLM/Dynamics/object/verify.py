import sys
sys.path.append('./')
from __init__ import *
from descriptor import SimplifiedStateDescriptor

class Verify:
    def __init__(self, trajectory_dir='Dynamics/object/segmented_trajectory', 
                save_dir='Dynamics/object/dynamics/verified', 
                discovered_dir='Dynamics/object/dynamics/discovered'):
        self._load_trajectory(trajectory_dir)
        self._describe()
        self._save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self._load_discovered_dynamics(discovered_dir)
        


    def _load_trajectory(self, trajectory_dir):
        self.loaded_trajectory = dict()
        for trajectory_name in os.listdir(trajectory_dir):
            with open(os.path.join(trajectory_dir, trajectory_name)) as f:
                trajectory = json.load(f)
                self.loaded_trajectory[trajectory_name[:-5]] = trajectory


    def _load_discovered_dynamics(self, discovered_dir):
        self.discovered_dynamics = dict()
        for object_name in os.listdir(discovered_dir):
            with open(os.path.join(discovered_dir, object_name)) as f:
                dynamics = json.load(f)
                self.discovered_dynamics[object_name[:-5]] = dynamics


    def _describe(self):
        self._description = dict()
        for obj in self.loaded_trajectory:
            self._description[obj] = []
            for _, description in self.loaded_trajectory[obj].items():
                self._description[obj].append(description)


    def verify(self, maximum_indices=16, maxim_sample=16):
        for obj in self.discovered_dynamics:
            save_path = os.path.join(self._save_dir, f'{obj}.json')
            if os.path.exists(save_path):
                continue

            obj_relationship = dict()

            for dynamic_num, dynamics in self.discovered_dynamics[obj].items():

                description = self._description[obj]
                random.shuffle(description)

                maximum_sample = min(len(description), maxim_sample)
                for obj_i in range(0, maximum_sample, maximum_indices):
                    initial_index, final_index = obj_i, min(maximum_sample, (obj_i + maximum_indices))
                    description = description[initial_index:final_index]
                    prefix_prompt = "You are a helpful assistant tasked with verifying object relationships in the Crafter environment. Please respond in JSON format."
                    object_relationship_format = """{
                        "related_objects": {
                            "object_1": "relationship to object_1",
                            "object_2": "relationship to object_2",
                            ...
                            }
                        },
                        "valid_relationships": {
                            "object_1": "relationship to object_1",
                            "object_2": "relationship to object_2",
                            ...
                            },
                        }"""

                    prompt = f"""
                    Given randomly selected frames featuring '{obj}' described as: {description}, please complete the following tasks:

                    1. Identify the objects most closely related to '{obj}' in the provided description.
                        - Rate their relevance using the following terms: 'Very related, 'Not related'.
                        
                    2. Based on the discovered dynamics {dynamics}, verify the relationships between the objects. Only consider relationships between objects with the same relevance in the provided frames as valid relationships.

                    3. Output all the valid relationships within the discovered dynamics that match all the relevance levels of the objects in the provided frames only about the object '{obj}'.

                    Consider relationships with the following objects only: ['grass', 'coal', 'cow', 'diamond', 'furnace', 'iron', 'lava', 'skeleton', 'stone', 'table', 'tree', 'water', 'zombie', 'plant', 'path', 'sand', 'plant-ripe'].

                    Relationship definitions:
                    - Very related: They are always found together.
                    - Not related: They are never found together.

                    Output in the following format: {object_relationship_format}
                    """


                    relationship = gpt_json(prefix_prompt, prompt)
                    relationship = json.loads(relationship)
                    obj_relationship[f'{dynamic_num}_{obj_i}'] = relationship

                    with open(save_path, 'w') as f:
                        json.dump(obj_relationship, f, indent=4)

            

if __name__ == '__main__':
    verify = Verify()
    verify.verify()